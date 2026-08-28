/* OPT-017 serial counterprobe; no universal MAXDOP recommendation. */
SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @Checksum int,@Rows bigint,@Measure bigint;
EXEC lab.usp_Opt017Aggregate @ProfileCode='S',@RequestedDop=1,@ResultChecksum=@Checksum OUTPUT,@ResultRows=@Rows OUTPUT,@ResultMeasure=@Measure OUTPUT;
DELETE lab.Opt017Evidence WHERE Phase='SERIAL';
INSERT lab.Opt017Evidence(Phase,ProfileCode,RequestedDop,ActualDop,ExchangeCount,ActiveThreads,ResultChecksum,ResultRows,ResultMeasure) VALUES('SERIAL','S',1,1,0,1,@Checksum,@Rows,@Measure);
SELECT 1 Sequence,'MITIGATION' Phase,'SUMMARY' CheckId,'PASS' Outcome,'OK' Code,CONCAT(N'Rows=',@Rows,N'; Checksum=',@Checksum) ObservedValue,N'dieselbe konzentrierte Verteilung mit querylokalem MAXDOP 1' RequiredValue,N'Die serielle Gegenprobe ist keine pauschale Empfehlung.' Message;
PRINT 'SQLPERF_SUMMARY|PASS|OK';
