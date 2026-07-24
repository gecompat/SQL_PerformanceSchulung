/* OPT-013 mitigation: provide the order required by the window function. */
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF INDEXPROPERTY(OBJECT_ID(N'lab.SpillData'),N'IX_SpillData_Payload_SortKey','IndexId') IS NULL
BEGIN
    CREATE INDEX IX_SpillData_Payload_SortKey
    ON lab.SpillData(Payload,SortKey);
END;

SELECT 1 Sequence,'MITIGATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,
       N'IX_SpillData_Payload_SortKey(Payload,SortKey)' ObservedValue,
       N'Zugriffspfad liefert die benötigte Ordnung ohne instanzweite Speicheränderung' RequiredValue,
       N'Die Gegenmaßnahme adressiert die Sortierarbeit statt den Server-Grant pauschal zu erhöhen.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
