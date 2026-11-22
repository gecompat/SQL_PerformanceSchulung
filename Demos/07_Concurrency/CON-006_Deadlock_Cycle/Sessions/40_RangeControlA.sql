SET NOCOUNT ON;SET XACT_ABORT ON;
DECLARE @Error int=NULL;
INSERT lab.RangeControlEvidence(RoleName,SessionId,KeyValue,Outcome,ErrorNumber,CapturedAtUtc)
VALUES('ACTOR_A',@@SPID,70,'READY',NULL,SYSUTCDATETIME());
EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','RANGE_CONTROL_B_READY',12000;
BEGIN TRY
    INSERT lab.RangeRows(KeyValue)VALUES(70);
    UPDATE lab.RangeControlEvidence SET Outcome='INSERTED',ErrorNumber=NULL,CapturedAtUtc=SYSUTCDATETIME()
    WHERE RoleName='ACTOR_A' AND SessionId=@@SPID AND KeyValue=70 AND Outcome='READY';
    IF @@ROWCOUNT<>1 THROW 51006,'FAIL_RESULT_CONTRACT: Range-Control-A-Evidenz konnte nicht abgeschlossen werden.',1;
END TRY
BEGIN CATCH
    SET @Error=ERROR_NUMBER();
    UPDATE lab.RangeControlEvidence SET Outcome='ERROR',ErrorNumber=@Error,CapturedAtUtc=SYSUTCDATETIME()
    WHERE RoleName='ACTOR_A' AND SessionId=@@SPID AND KeyValue=70;
    THROW;
END CATCH;
EXEC fwk.USP_Signal '$(DemoId)','$(RunToken)','RANGE_CONTROL_A_DONE';
PRINT 'SQLPERF_SUMMARY|PASS|OK';
