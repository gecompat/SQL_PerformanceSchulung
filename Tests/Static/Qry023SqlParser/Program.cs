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

var tempdbGuard = Path.Combine(repository, "Tests/Runtime/qry023_tempdb_resource_guard.sql");
foreach (var dialect in dialects)
{
    using var reader = new StringReader(File.ReadAllText(tempdbGuard));
    _ = dialect.Parser.Parse(reader, out var errors);
    foreach (var error in errors)
    {
        failed = true;
        Console.Error.WriteLine($"FAIL qry023_tempdb_resource_guard.sql ({dialect.Name}) {error.Line}:{error.Column} {error.Message}");
    }
    if (errors.Count == 0)
        Console.WriteLine($"PASS qry023_tempdb_resource_guard.sql parses in {dialect.Name}");
}

var dgn004Directory = Path.Combine(repository, "Tests/Fixtures/DGN004_SourcePair");
var expectedDgn004Files = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
{
    "CapturePlanFrame.sql",
    "ReplayHintControl.sql",
    "ReplayReference.sql",
    "SnapshotPlanCandidates.sql",
};
var dgn004Files = Directory.GetFiles(dgn004Directory, "*.sql")
    .OrderBy(Path.GetFileName, StringComparer.OrdinalIgnoreCase)
    .ToArray();
var actualDgn004Names = dgn004Files.Select(path => Path.GetFileName(path)!)
    .ToHashSet(StringComparer.OrdinalIgnoreCase);
if (!expectedDgn004Files.SetEquals(actualDgn004Names))
{
    failed = true;
    Console.Error.WriteLine("FAIL DGN-004 SQL fixture set differs from the declared syntax-check scope.");
    foreach (var missing in expectedDgn004Files.Except(actualDgn004Names, StringComparer.OrdinalIgnoreCase))
        Console.Error.WriteLine($"Missing: {missing}");
    foreach (var extra in actualDgn004Names.Except(expectedDgn004Files, StringComparer.OrdinalIgnoreCase))
        Console.Error.WriteLine($"Unexpected: {extra}");
}

foreach (var file in dgn004Files)
{
    var fileName = Path.GetFileName(file)!;
    var dgn004Sql = File.ReadAllText(file);
    dgn004Sql = dgn004Sql
        .Replace("$(DGN004_RUN)", "dgn004-run-1", StringComparison.Ordinal)
        .Replace("$(DGN004_ROLE)", "R", StringComparison.Ordinal)
        .Replace("$(DGN004_CALL)", "3", StringComparison.Ordinal)
        .Replace("$(DGN004_DATABASE_ID)", "73", StringComparison.Ordinal)
        .Replace("$(DGN004_OBJECT_ID)", "101", StringComparison.Ordinal)
        .Replace("$(DGN004_STATEMENT_START_OFFSET)", "0", StringComparison.Ordinal)
        .Replace("$(DGN004_PLAN_HANDLE)", "0000", StringComparison.Ordinal)
        .Replace("__DGN004_EXPECTED_MODULE_UTF16_HEX__", "4100", StringComparison.Ordinal);
    foreach (var dialect in dialects)
    {
        using var reader = new StringReader(dgn004Sql);
        _ = dialect.Parser.Parse(reader, out var errors);
        foreach (var error in errors)
        {
            failed = true;
            Console.Error.WriteLine($"FAIL {fileName} ({dialect.Name}) {error.Line}:{error.Column} {error.Message}");
        }
        if (errors.Count == 0)
            Console.WriteLine($"PASS {fileName} parses in {dialect.Name} (syntax only)");
    }
}

var res004Lesson = Path.Combine(repository, "Documentation/Curriculum/COMPETING_MEMORY_GRANTS_LESSON.md");
var res004Markdown = File.ReadAllText(res004Lesson);
var res004Queries = System.Text.RegularExpressions.Regex.Matches(
    res004Markdown,
    @"(?is)```sql\s*(.*?)```"
)
    .Select(match => match.Groups[1].Value)
    .Where(sql => sql.Contains("DECLARE @OwnRequests TABLE", StringComparison.OrdinalIgnoreCase))
    .ToArray();
if (res004Queries.Length != 1)
{
    failed = true;
    Console.Error.WriteLine("FAIL expected exactly one RES-004 teaching query in the curriculum lesson");
}
else
{
    foreach (var dialect in dialects)
    {
        using var reader = new StringReader(res004Queries[0]);
        _ = dialect.Parser.Parse(reader, out var errors);
        foreach (var error in errors)
        {
            failed = true;
            Console.Error.WriteLine($"FAIL RES-004 competing memory grants ({dialect.Name}) {error.Line}:{error.Column} {error.Message}");
        }
        if (errors.Count == 0)
            Console.WriteLine($"PASS RES-004 competing memory grants parses in {dialect.Name} (syntax only)");
    }
}

ParseDocumentationSql(
    "Documentation/Curriculum/IMPLICIT_CONVERSION_LESSON.md",
    "QRY-002 implicit conversion");
ParseDocumentationSql(
    "Documentation/Curriculum/HALF_OPEN_DATE_INTERVAL_LESSON.md",
    "QRY-003 half-open date intervals");
ParseDocumentationSql(
    "Documentation/Curriculum/WORKER_QUEUE_PRESSURE_LESSON.md",
    "RES-001 worker queue pressure");
ParseDocumentationSql(
    "Documentation/Curriculum/BUFFER_POOL_PRESSURE_LESSON.md",
    "RES-003 buffer pool pressure");
ParseDocumentationSql(
    "Documentation/Curriculum/LAST_PAGE_INSERT_CONTENTION_LESSON.md",
    "IDX-007 last-page insert contention");
ParseDocumentationSql(
    "Documentation/HowTo/SQL_SERVER_2025_AI_VECTOR_COMPATIBILITY.md",
    "SQL Server 2025 VECTOR compatibility");

void ParseDocumentationSql(string relativePath, string documentName)
{
    var lessonPath = Path.Combine(repository, relativePath);
    var markdown = File.ReadAllText(lessonPath);
    var blocks = System.Text.RegularExpressions.Regex.Matches(
        markdown,
        @"(?is)```sql\s*(.*?)```"
    );
    if (blocks.Count == 0)
    {
        failed = true;
        Console.Error.WriteLine($"FAIL {documentName} has no fenced SQL examples");
        return;
    }

    var blockNumber = 0;
    foreach (System.Text.RegularExpressions.Match block in blocks)
    {
        blockNumber++;
        foreach (var dialect in dialects)
        {
            using var reader = new StringReader(block.Groups[1].Value);
            _ = dialect.Parser.Parse(reader, out var errors);
            foreach (var error in errors)
            {
                failed = true;
                Console.Error.WriteLine(
                    $"FAIL {documentName} example {blockNumber} ({dialect.Name}) " +
                    $"{error.Line}:{error.Column} {error.Message}");
            }
            if (errors.Count == 0)
                Console.WriteLine(
                    $"PASS {documentName} example {blockNumber} parses in {dialect.Name} " +
                    "(syntax only)");
        }
    }
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
    ? "FAIL selected ScriptDom syntax parsing; this does not execute SQL Server."
    : "PASS selected SQL Server ScriptDom syntax parsing; no SQL Server execution.");
return failed ? 1 : 0;
