@{
    RootModule = 'PerformanceTrainingScenario.psm1'
    ModuleVersion = '1.2.0'
    GUID = '69a872d4-9782-46c8-9066-402105cbfd40'
    Author = 'SQL_PerformanceSchulung'
    Description = 'Interaktiver Lifecycle fuer markergebundene SQL-Performance-Schulungsszenarien.'
    PowerShellVersion = '7.2'
    FunctionsToExport = @(
        'Get-PerformanceTrainingScenario',
        'Start-PerformanceTrainingScenario',
        'Reset-PerformanceTrainingScenario',
        'Remove-PerformanceTrainingScenario'
    )
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
