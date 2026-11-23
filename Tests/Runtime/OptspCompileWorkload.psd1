@{
    Batch = 'SELECT @value + (SELECT COUNT(*) FROM (VALUES (1),(2),(3)) a(id) JOIN (VALUES (1),(3),(4)) b(id) ON a.id = b.id JOIN (VALUES (1),(2),(5)) c(id) ON b.id = c.id JOIN (VALUES (1),(2),(6)) d(id) ON c.id = d.id JOIN (VALUES (1),(3),(7)) e(id) ON d.id = e.id WHERE a.id > @value);'
    DistinctBatch = 'SELECT @value + (SELECT COUNT(*) FROM (VALUES (1),(2),(3)) a(id) JOIN (VALUES (1),(3),(4)) b(id) ON a.id = b.id JOIN (VALUES (1),(2),(5)) c(id) ON b.id = c.id JOIN (VALUES (1),(2),(6)) d(id) ON c.id = d.id JOIN (VALUES (1),(3),(7)) e(id) ON d.id = e.id WHERE a.id > @value AND e.id < 9);'
    Parameters = '@value int'
    Value = 37
}
