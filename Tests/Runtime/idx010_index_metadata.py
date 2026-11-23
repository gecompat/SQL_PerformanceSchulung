"""Read-only index evidence for the fixed profile of the ordered NCCI pilot."""
from __future__ import annotations

import json

from idx010_pilot_sequence import IndexEvidence, Target
from idx010_pilot_setup import (
    Arm, FIXTURE_ROWS, INDEX_NAME, ROWGROUP_COUNT, ROWGROUP_ROWS, owned_database_guard,
)


METADATA_LIMIT = 1024


def index_evidence_batch(target: Target) -> str:
    return owned_database_guard(target.run_token, target.arm) + f"""
DECLARE @ObjectId int = OBJECT_ID(N'dbo.Events', N'U');
DECLARE @IndexId int, @PartitionId bigint, @ColumnId int, @Ordinal int;

SELECT @IndexId = i.index_id
FROM sys.indexes AS i
WHERE i.object_id = @ObjectId AND i.name = N'{INDEX_NAME}'
    AND i.type = 6 AND i.has_filter = 0 AND i.is_disabled = 0 AND i.is_hypothetical = 0;
IF @IndexId IS NULL
    THROW 51010, 'NOT_PROVEN: expected unfiltered nonclustered columnstore index is absent.', 1;

IF (SELECT COUNT_BIG(*) FROM sys.partitions WHERE object_id = @ObjectId AND index_id = @IndexId) <> 1
    THROW 51011, 'NOT_PROVEN: expected exactly one index partition.', 1;
SELECT @PartitionId = p.partition_id
FROM sys.partitions AS p
WHERE p.object_id = @ObjectId AND p.index_id = @IndexId
    AND p.partition_number = 1 AND p.data_compression_desc = N'COLUMNSTORE';

DECLARE @IndexColumns table (column_id int NOT NULL, column_name sysname NOT NULL, order_ordinal int);
INSERT @IndexColumns
SELECT c.column_id, c.name, ic.column_store_order_ordinal
FROM sys.index_columns AS ic
JOIN sys.columns AS c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
WHERE ic.object_id = @ObjectId AND ic.index_id = @IndexId
    AND ic.is_included_column = 1 AND ic.key_ordinal = 0 AND ic.partition_ordinal = 0
    AND c.system_type_id = TYPE_ID(N'bigint') AND c.user_type_id = c.system_type_id
    AND c.is_nullable = 0;

SELECT @ColumnId = column_id, @Ordinal = order_ordinal
FROM @IndexColumns WHERE column_name = N'EventDayKey';
IF @PartitionId IS NULL OR @ColumnId IS NULL OR @Ordinal IS NULL
    OR (SELECT COUNT_BIG(*) FROM sys.index_columns WHERE object_id = @ObjectId AND index_id = @IndexId) <> 2
    OR (SELECT COUNT_BIG(*) FROM @IndexColumns) <> 2
    OR NOT EXISTS (SELECT 1 FROM @IndexColumns WHERE column_name = N'EventId' AND order_ordinal = 0)
    THROW 51012, 'NOT_PROVEN: index partition, columns or order differ from the profile.', 1;

DECLARE @Groups table (group_id int NOT NULL, state int NOT NULL, total_rows bigint, deleted_rows bigint);
INSERT @Groups
SELECT rg.row_group_id, rg.state, rg.total_rows, rg.deleted_rows
FROM sys.column_store_row_groups AS rg
WHERE rg.object_id = @ObjectId AND rg.index_id = @IndexId AND rg.partition_number = 1;

IF (SELECT COUNT_BIG(*) FROM @Groups) <> {ROWGROUP_COUNT}
    OR EXISTS (
        SELECT 1 FROM @Groups
        WHERE state <> 3 OR total_rows IS NULL OR total_rows <> {ROWGROUP_ROWS}
            OR deleted_rows IS NULL OR deleted_rows <> 0
    )
    OR EXISTS (
        SELECT 1 FROM sys.internal_partitions AS p
        WHERE p.object_id = @ObjectId AND p.index_id = @IndexId
            AND p.partition_number = 1 AND p.internal_object_type = 4
            AND (p.rows IS NULL OR p.rows <> 0)
    )
    THROW 51013, 'NOT_PROVEN: compressed rowgroups or delete buffer differ from profile.', 1;

DECLARE @Segments table (group_id int NOT NULL, minimum varbinary(18), maximum varbinary(18));
-- Same bigint encoding selection and conversion as Microsoft's order-quality.sql.
INSERT @Segments
SELECT s.segment_id, CONVERT(varbinary(18), s.min_data_id), CONVERT(varbinary(18), s.max_data_id)
FROM sys.column_store_segments AS s
WHERE s.partition_id = @PartitionId AND s.column_id = @ColumnId
    AND s.encoding_type IN (1, 2) AND s.has_nulls = 0
    AND s.row_count = {ROWGROUP_ROWS} AND s.min_data_id < s.max_data_id
    AND s.min_data_id >= 0 AND s.max_data_id < {FIXTURE_ROWS};

IF (
    SELECT COUNT_BIG(*) FROM sys.column_store_segments AS s
    WHERE s.partition_id = @PartitionId AND s.column_id = @ColumnId
) <> {ROWGROUP_COUNT}
    OR (SELECT COUNT_BIG(*) FROM @Segments) <> {ROWGROUP_COUNT}
    OR (SELECT COUNT(DISTINCT group_id) FROM @Segments) <> {ROWGROUP_COUNT}
    OR EXISTS (SELECT group_id FROM @Segments EXCEPT SELECT group_id FROM @Groups)
    OR EXISTS (SELECT group_id FROM @Groups EXCEPT SELECT group_id FROM @Segments)
    OR (
        SELECT COUNT(*) FROM (
            SELECT minimum AS endpoint FROM @Segments
            UNION
            SELECT maximum AS endpoint FROM @Segments
        ) AS distinct_endpoints
    ) <> {2 * ROWGROUP_COUNT}
    THROW 51014, 'NOT_PROVEN: segment coverage or endpoint uniqueness differs.', 1;

-- With distinct endpoints, each overlap in the Microsoft score contributes twice.
DECLARE @Pairs int = (
    SELECT COUNT(*) FROM @Segments AS a
    JOIN @Segments AS b ON a.group_id < b.group_id
        AND a.minimum < b.maximum AND b.minimum < a.maximum
);

SELECT DB_NAME() AS database_name, N'{INDEX_NAME}' AS index_name, @Ordinal AS order_ordinal,
    (SELECT COUNT(*) FROM @Groups) AS rowgroup_count,
    {ROWGROUP_ROWS} AS rowgroup_size, (SELECT COUNT(*) FROM @Segments) AS eligible_segments,
    @Pairs AS overlapping_pairs
FOR JSON PATH, WITHOUT_ARRAY_WRAPPER;
"""


def decode_index_evidence(payload: bytes, target: Target) -> IndexEvidence:
    if len(payload) > METADATA_LIMIT:
        raise ValueError("index metadata response exceeds the capture limit")
    try:
        record = json.loads(payload.decode("ascii"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, ValueError):
        raise ValueError("index metadata response is not a unique JSON object") from None
    expected = {
        "database_name": target.database_name,
        "index_name": INDEX_NAME,
        "order_ordinal": 1 if target.arm is Arm.ORDERED else 0,
        "rowgroup_count": ROWGROUP_COUNT,
        "rowgroup_size": ROWGROUP_ROWS,
        "eligible_segments": ROWGROUP_COUNT,
    }
    if (
        not isinstance(record, dict)
        or record.keys() != expected.keys() | {"overlapping_pairs"}
        or any(type(record[key]) is not type(value) or record[key] != value for key, value in expected.items())
    ):
        raise ValueError("index metadata response differs from the expected profile")
    overlaps = record["overlapping_pairs"]
    max_pairs = ROWGROUP_COUNT * (ROWGROUP_COUNT - 1) // 2
    if type(overlaps) is not int or not 0 <= overlaps <= max_pairs:
        raise ValueError("invalid number of overlapping segment pairs")
    return IndexEvidence(
        target.database_name,
        INDEX_NAME,
        expected["order_ordinal"],
        (ROWGROUP_ROWS,) * ROWGROUP_COUNT,
        False,
        ROWGROUP_COUNT,
        overlaps,
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    fields: dict[str, object] = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError("duplicate metadata field")
        fields[key] = value
    return fields
