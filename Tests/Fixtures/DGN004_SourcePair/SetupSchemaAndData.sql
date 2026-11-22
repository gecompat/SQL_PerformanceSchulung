/*
  DGN-004 owned-database fixture.

  The caller must create a uniquely named database in its private SQL Server
  container, add all four FWK-002 ownership markers, and run this file in that
  database.  This script never creates or drops a database.
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET QUOTED_IDENTIFIER ON;
SET NUMERIC_ROUNDABORT OFF;
SET LANGUAGE us_english;
SET DATEFORMAT mdy;
SET DATEFIRST 7;

DECLARE @Project nvarchar(128), @Contract nvarchar(128),
        @Demo nvarchar(128), @Run nvarchar(128);
SELECT
    @Project = MAX(CASE WHEN ep.name = N'SQLPERF.Project' THEN CONVERT(nvarchar(128), ep.value) END),
    @Contract = MAX(CASE WHEN ep.name = N'SQLPERF.ContractVersion' THEN CONVERT(nvarchar(128), ep.value) END),
    @Demo = MAX(CASE WHEN ep.name = N'SQLPERF.DemoId' THEN CONVERT(nvarchar(128), ep.value) END),
    @Run = MAX(CASE WHEN ep.name = N'SQLPERF.RunToken' THEN CONVERT(nvarchar(128), ep.value) END)
FROM sys.extended_properties AS ep
WHERE ep.class = 0
  AND ep.name IN (N'SQLPERF.Project', N'SQLPERF.ContractVersion',
                  N'SQLPERF.DemoId', N'SQLPERF.RunToken');

IF (SELECT COUNT(*) FROM sys.extended_properties
    WHERE class = 0 AND name IN (N'SQLPERF.Project', N'SQLPERF.ContractVersion',
                                  N'SQLPERF.DemoId', N'SQLPERF.RunToken')) <> 4
   OR @Project IS NULL OR @Project COLLATE Latin1_General_100_BIN2 <> N'SQL_PerformanceSchulung'
   OR DATALENGTH(@Project) <> DATALENGTH(N'SQL_PerformanceSchulung')
   OR @Demo IS NULL OR @Demo COLLATE Latin1_General_100_BIN2 <> N'DGN-004'
   OR DATALENGTH(@Demo) <> DATALENGTH(N'DGN-004')
   OR @Contract IS NULL OR @Contract COLLATE Latin1_General_100_BIN2 <> N'1.0'
   OR DATALENGTH(@Contract) <> DATALENGTH(N'1.0')
   OR @Run IS NULL OR LEN(@Run) NOT BETWEEN 1 AND 16
   OR @Run COLLATE Latin1_General_100_BIN2 LIKE N'%[^A-Z0-9]%'
    THROW 51020, 'DGN-004 ownership markers do not match.', 1;

IF SCHEMA_ID(N'dgn004') IS NOT NULL
    THROW 51021, 'DGN-004 schema already exists.', 1;

GO

CREATE SCHEMA dgn004 AUTHORIZATION dbo;
GO

CREATE TABLE dgn004.Orders
(
    OrderId int NOT NULL CONSTRAINT PK_DGN004_Orders PRIMARY KEY CLUSTERED,
    CustomerId int NOT NULL,
    ContactId int NOT NULL
);
CREATE TABLE dgn004.OrderLines
(
    LineId int NOT NULL CONSTRAINT PK_DGN004_OrderLines PRIMARY KEY CLUSTERED,
    OrderId int NOT NULL,
    ItemId int NOT NULL
);
CREATE TABLE dgn004.Customers
(
    CustomerId int NOT NULL CONSTRAINT PK_DGN004_Customers PRIMARY KEY CLUSTERED,
    CustomerValue int NOT NULL,
    CategoryId int NOT NULL,
    CityId int NOT NULL
);
CREATE TABLE dgn004.Categories
(
    CategoryId int NOT NULL CONSTRAINT PK_DGN004_Categories PRIMARY KEY CLUSTERED,
    CategoryValue int NOT NULL
);
CREATE TABLE dgn004.Contacts
(
    ContactId int NOT NULL CONSTRAINT PK_DGN004_Contacts PRIMARY KEY CLUSTERED,
    ContactValue int NOT NULL
);
CREATE TABLE dgn004.Cities
(
    CityId int NOT NULL CONSTRAINT PK_DGN004_Cities PRIMARY KEY CLUSTERED,
    CityValue int NOT NULL,
    RegionId int NOT NULL
);
CREATE TABLE dgn004.Regions
(
    RegionId int NOT NULL CONSTRAINT PK_DGN004_Regions PRIMARY KEY CLUSTERED,
    RegionValue int NOT NULL,
    CountryId int NOT NULL
);
CREATE TABLE dgn004.Countries
(
    CountryId int NOT NULL CONSTRAINT PK_DGN004_Countries PRIMARY KEY CLUSTERED,
    CountryValue int NOT NULL
);
CREATE TABLE dgn004.Items
(
    ItemId int NOT NULL CONSTRAINT PK_DGN004_Items PRIMARY KEY CLUSTERED,
    ItemValue int NOT NULL
);
CREATE TABLE dgn004.ItemGroups
(
    MapId int NOT NULL CONSTRAINT PK_DGN004_ItemGroups PRIMARY KEY CLUSTERED,
    ItemId int NOT NULL,
    GroupNo int NOT NULL
);
GO

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 96
)
INSERT dgn004.Orders (OrderId, CustomerId, ContactId)
SELECT Id, 1 + ((Id - 1) % 48), 1 + ((Id - 1) % 24) FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 192
)
INSERT dgn004.OrderLines (LineId, OrderId, ItemId)
SELECT Id, 1 + ((Id - 1) / 2), 1 + ((Id - 1) % 48) FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 48
)
INSERT dgn004.Customers (CustomerId, CustomerValue, CategoryId, CityId)
SELECT Id, 3000 + Id, 1 + ((Id - 1) % 4), 1 + ((Id - 1) % 12) FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 4
)
INSERT dgn004.Categories (CategoryId, CategoryValue)
SELECT Id, 1000 + Id FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 24
)
INSERT dgn004.Contacts (ContactId, ContactValue)
SELECT Id, 2000 + Id FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 12
)
INSERT dgn004.Cities (CityId, CityValue, RegionId)
SELECT Id, 4000 + Id, 1 + ((Id - 1) % 6) FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 6
)
INSERT dgn004.Regions (RegionId, RegionValue, CountryId)
SELECT Id, 5000 + Id, 1 + ((Id - 1) % 3) FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 3
)
INSERT dgn004.Countries (CountryId, CountryValue)
SELECT Id, 6000 + Id FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 48
)
INSERT dgn004.Items (ItemId, ItemValue)
SELECT Id, 7000 + Id FROM N
OPTION (MAXRECURSION 0);

;WITH N AS
(
    SELECT CONVERT(int, 1) AS Id
    UNION ALL SELECT Id + 1 FROM N WHERE Id < 96
)
INSERT dgn004.ItemGroups (MapId, ItemId, GroupNo)
SELECT Id, 1 + ((Id - 1) / 2), 1 + ((Id - 1) % 2) FROM N
OPTION (MAXRECURSION 0);
GO

CREATE NONCLUSTERED INDEX IX_DGN004_Orders_CustomerId ON dgn004.Orders(CustomerId);
CREATE NONCLUSTERED INDEX IX_DGN004_Orders_ContactId ON dgn004.Orders(ContactId);
CREATE NONCLUSTERED INDEX IX_DGN004_OrderLines_OrderId ON dgn004.OrderLines(OrderId);
CREATE NONCLUSTERED INDEX IX_DGN004_OrderLines_ItemId ON dgn004.OrderLines(ItemId);
CREATE NONCLUSTERED INDEX IX_DGN004_Customers_CategoryId ON dgn004.Customers(CategoryId);
CREATE NONCLUSTERED INDEX IX_DGN004_Customers_CityId ON dgn004.Customers(CityId);
CREATE NONCLUSTERED INDEX IX_DGN004_Cities_RegionId ON dgn004.Cities(RegionId);
CREATE NONCLUSTERED INDEX IX_DGN004_Regions_CountryId ON dgn004.Regions(CountryId);
CREATE NONCLUSTERED INDEX IX_DGN004_ItemGroups_ItemId_GroupNo ON dgn004.ItemGroups(ItemId, GroupNo);
GO

IF (SELECT SUM(rows) FROM sys.partitions WHERE index_id IN (0, 1)
    AND object_id IN (SELECT object_id FROM sys.tables WHERE schema_id = SCHEMA_ID(N'dgn004'))) <> 529
   OR (SELECT COUNT(*) FROM sys.tables WHERE schema_id = SCHEMA_ID(N'dgn004')) <> 10
   OR (SELECT COUNT(*) FROM sys.indexes AS i
       INNER JOIN sys.tables AS t ON t.object_id = i.object_id
       WHERE t.schema_id = SCHEMA_ID(N'dgn004') AND i.type = 2) <> 9
    THROW 51022, 'DGN-004 fixture shape differs from its fixed contract.', 1;

/* Engine text/settings and fixture counts, emitted for bounded caller checks. */
SELECT CONVERT(varchar(20), SERVERPROPERTY('ProductVersion')) + '|'
    + CONVERT(varchar(80), SERVERPROPERTY('Edition')) + '|'
    + CONVERT(varchar(10), (SELECT compatibility_level FROM sys.databases WHERE database_id = DB_ID())) + '|'
    + CONVERT(varchar(10), (SELECT SUM(p.rows)
                            FROM sys.partitions AS p
                            INNER JOIN sys.tables AS t ON t.object_id = p.object_id
                            INNER JOIN sys.schemas AS s ON s.schema_id = t.schema_id
                            WHERE s.name = N'dgn004' AND p.index_id = 1)) + '|'
    + CONVERT(varchar(10), (SELECT COUNT(*) FROM sys.tables AS t
                            INNER JOIN sys.schemas AS s ON s.schema_id = t.schema_id
                            WHERE s.name = N'dgn004')) + '|'
    + CONVERT(varchar(10), (SELECT COUNT(*) FROM sys.indexes AS i
                            INNER JOIN sys.tables AS t ON t.object_id = i.object_id
                            INNER JOIN sys.schemas AS s ON s.schema_id = t.schema_id
                            WHERE s.name = N'dgn004' AND i.type = 2)) AS DGN004_SETUP_RESULT;
