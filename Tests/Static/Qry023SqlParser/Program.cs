using Microsoft.SqlServer.TransactSql.ScriptDom;

var repository = Directory.GetCurrentDirectory();
var demo = Path.GetFullPath(Path.Combine(repository, "Demos/05_Query_Patterns/QRY-023_Graph_Tables"));
var expectedFiles = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
{
    "00_Preflight.sql",
    "10_Setup.sql",
    "15_Framework.sql",
    "20_Workload.sql",
    "22_Admin_Permission_Inventory.sql",
    "25_Qualification_Preflight.sql",
    "30_Correctness.sql",
    "40_Measurement.sql",
    "50_Plan_Evidence.sql",
    "90_Cleanup.sql",
};
var sqlFiles = Directory.GetFiles(demo, "*.sql").OrderBy(Path.GetFileName, StringComparer.OrdinalIgnoreCase).ToArray();
var actualNames = sqlFiles.Select(path => Path.GetFileName(path)!).ToHashSet(StringComparer.OrdinalIgnoreCase);
if (!expectedFiles.SetEquals(actualNames))
{
    Console.Error.WriteLine("FAIL QRY-023 SQL file set differs from the declared syntax-check scope.");
    foreach (var missing in expectedFiles.Except(actualNames, StringComparer.OrdinalIgnoreCase))
        Console.Error.WriteLine($"Missing: {missing}");
    foreach (var extra in actualNames.Except(expectedFiles, StringComparer.OrdinalIgnoreCase))
        Console.Error.WriteLine($"Unexpected: {extra}");
    return 2;
}

var dialects = new (string Name, TSqlParser Parser)[]
{
    ("SQL Server 2019 grammar", new TSql150Parser(initialQuotedIdentifiers: true)),
    ("SQL Server 2022 grammar", new TSql160Parser(initialQuotedIdentifiers: true)),
    ("SQL Server 2025 grammar", new TSql170Parser(initialQuotedIdentifiers: true)),
};
var failed = false;
foreach (var file in sqlFiles.Where(path => !Path.GetFileName(path).Equals("15_Framework.sql", StringComparison.OrdinalIgnoreCase)))
{
    var fileFailed = false;
    var sql = File.ReadAllText(file)
        .Replace("$(DemoId)", "QRY-023", StringComparison.Ordinal)
        .Replace("$(RunToken)", "LOCAL", StringComparison.Ordinal)
        .Replace("$(TargetDatabase)", "SQLPERF_LAB_QRY023_LOCAL", StringComparison.Ordinal)
        .Replace("$(StandardEndpointInventory)", "1G540063007000", StringComparison.Ordinal)
        .Replace("$(BoundObjectInventory)", "13", StringComparison.Ordinal);
    if (Path.GetFileName(file).Equals("50_Plan_Evidence.sql", StringComparison.OrdinalIgnoreCase))
    {
        const string widthDirective = ":setvar SQLCMDMAXVARTYPEWIDTH 0";
        if (!sql.Contains(widthDirective, StringComparison.OrdinalIgnoreCase))
        {
            failed = true;
            Console.Error.WriteLine("FAIL 50_Plan_Evidence.sql is missing its unlimited sqlcmd XML-width directive.");
            continue;
        }
        sql = System.Text.RegularExpressions.Regex.Replace(
            sql,
            @"(?im)^\s*:setvar\s+SQLCMDMAXVARTYPEWIDTH\s+0\s*\r?$",
            string.Empty);
    }
    foreach (var dialect in dialects)
    {
        using var reader = new StringReader(sql);
        _ = dialect.Parser.Parse(reader, out var errors);
        foreach (var error in errors)
        {
            failed = true;
            fileFailed = true;
            Console.Error.WriteLine($"FAIL {Path.GetFileName(file)} ({dialect.Name}) {error.Line}:{error.Column} {error.Message}");
        }
    }
    if (!fileFailed)
        Console.WriteLine($"PASS {Path.GetFileName(file)} parses in all three SQL Server grammars");
}

// This is a SQLCMD include wrapper, not a standalone T-SQL source file.
var frameworkWrapper = File.ReadAllText(Path.Combine(demo, "15_Framework.sql"));
if (!frameworkWrapper.Contains(":r Demos/00_Framework/Sql/FWK_Measurement.sql", StringComparison.Ordinal))
{
    failed = true;
    Console.Error.WriteLine("FAIL 15_Framework.sql no longer contains its declared SQLCMD include.");
}
else
{
    Console.WriteLine("PASS 15_Framework.sql retains the declared SQLCMD include (excluded from T-SQL parsing)");
}

Console.WriteLine(failed
    ? "FAIL QRY-023 ScriptDom syntax parsing; this does not execute SQL Server."
    : "PASS QRY-023 ScriptDom syntax parsing; no SQL Server execution.");
return failed ? 1 : 0;
