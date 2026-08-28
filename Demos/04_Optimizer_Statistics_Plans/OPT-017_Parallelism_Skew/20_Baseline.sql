/* OPT-017 balanced parallel baseline. */
SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @Checksum int,@Rows bigint,@Measure bigint;
EXEC lab.usp_Opt017Aggregate @ProfileCode='B',@RequestedDop=4,@ResultChecksum=@Checksum OUTPUT,@ResultRows=@Rows OUTPUT,@ResultMeasure=@Measure OUTPUT;
DELETE lab.Opt017Evidence WHERE Phase='BALANCED';
INSERT lab.Opt017Evidence(Phase,ProfileCode,RequestedDop,ResultChecksum,ResultRows,ResultMeasure) VALUES('BALANCED','B',4,@Checksum,@Rows,@Measure);
IF @Rows<>600000 THROW 51006,'FAIL_RESULT_CONTRACT: Balancierte Zeilenzahl ist ungueltig.',1;
SELECT 1 Sequence,'BASELINE' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'Rows=',@Rows,N'; Checksum=',@Checksum) ObservedValue,N'600000 balancierte Zeilen; querylokales MAXDOP 4' RequiredValue,N'Balancierte Parallelbasis ausgefuehrt.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
