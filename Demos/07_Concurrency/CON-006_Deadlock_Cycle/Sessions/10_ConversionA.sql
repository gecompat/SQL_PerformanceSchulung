SET NOCOUNT ON;SET XACT_ABORT ON;SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;SET DEADLOCK_PRIORITY LOW;
DECLARE @SessionId smallint=@@SPID;
BEGIN TRY
    BEGIN TRANSACTION;
    SELECT Value FROM lab.DeadlockRows WHERE RowId=1;
    EXEC fwk.USP_Signal '$(DemoId)','$(RunToken)','CONVERSION_A_READ';
    EXEC fwk.USP_WaitForSignal '$(DemoId)','$(RunToken)','CONVERSION_B_READ',15000;
    /*CON006_CONVERSION_$(RunToken)*/ UPDATE lab.DeadlockRows SET Value+=1 WHERE RowId=1;
    COMMIT TRANSACTION;
    INSERT lab.ConversionEvidence(Attempt,RoleName,Outcome,ErrorNumber,SessionId)
    VALUES('CONVERT','ACTOR_A','SURVIVOR',NULL,@SessionId);
END TRY
BEGIN CATCH
    IF XACT_STATE()<>0 ROLLBACK TRANSACTION;
    IF ERROR_NUMBER()<>1205 THROW;
    INSERT lab.ConversionEvidence(Attempt,RoleName,Outcome,ErrorNumber,SessionId)
    VALUES('CONVERT','ACTOR_A','VICTIM',1205,@SessionId);
END CATCH;
EXEC fwk.USP_Signal '$(DemoId)','$(RunToken)','CONVERSION_A_DONE';
PRINT 'SQLPERF_SUMMARY|PASS|OK';
