"""Small lexical helpers for static T-SQL source contracts."""
from __future__ import annotations

import re


def without_tsql_comments(sql: str) -> str:
    """Remove line and nested block comments without changing quoted content."""
    output: list[str] = []
    index = 0
    block_depth = 0
    quote: str | None = None
    bracketed = False
    while index < len(sql):
        if block_depth:
            if sql.startswith("/*", index):
                block_depth += 1
                output.extend("  ")
                index += 2
            elif sql.startswith("*/", index):
                block_depth -= 1
                output.extend("  ")
                index += 2
            else:
                output.append(sql[index] if sql[index] in "\r\n" else " ")
                index += 1
            continue
        if quote is not None:
            output.append(sql[index])
            if sql[index] == quote:
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    output.append(sql[index + 1])
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if bracketed:
            output.append(sql[index])
            if sql[index] == "]":
                if index + 1 < len(sql) and sql[index + 1] == "]":
                    output.append(sql[index + 1])
                    index += 2
                    continue
                bracketed = False
            index += 1
            continue
        if sql.startswith("--", index):
            while index < len(sql) and sql[index] not in "\r\n":
                output.append(" ")
                index += 1
            continue
        if sql.startswith("/*", index):
            block_depth = 1
            output.extend("  ")
            index += 2
            continue
        char = sql[index]
        output.append(char)
        if char in "'\"":
            quote = char
        elif char == "[":
            bracketed = True
        index += 1
    if block_depth:
        raise ValueError("query contains an unterminated block comment")
    if quote is not None:
        raise ValueError("query contains an unterminated quoted value or identifier")
    if bracketed:
        raise ValueError("query contains an unterminated bracketed identifier")
    return "".join(output)


def extract_tsql_cte_body(sql: str, name: str) -> str:
    """Extract one balanced named CTE body while respecting T-SQL quoting."""
    if type(name) is not str or not name:
        raise ValueError("CTE name must be nonempty text")
    source = without_tsql_comments(sql)
    pattern = re.compile(
        rf"\b{re.escape(name)}\s+AS\s*\(", flags=re.IGNORECASE,
    )
    matches = []
    index = 0
    while index < len(source):
        char = source[index]
        if char in "'\"":
            quote = char
            index += 1
            while index < len(source):
                if source[index] == quote:
                    if index + 1 < len(source) and source[index + 1] == quote:
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            continue
        if char == "[":
            index += 1
            while index < len(source):
                if source[index] == "]":
                    if index + 1 < len(source) and source[index + 1] == "]":
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            continue
        match = pattern.match(source, index)
        if match:
            matches.append(match)
            index = match.end()
        else:
            index += 1
    if len(matches) != 1:
        raise ValueError("expected exactly one named CTE")
    opening = matches[0].end() - 1
    depth = 0
    quote: str | None = None
    bracketed = False
    index = opening
    while index < len(source):
        char = source[index]
        if quote is not None:
            if char == quote:
                if index + 1 < len(source) and source[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if bracketed:
            if char == "]":
                if index + 1 < len(source) and source[index + 1] == "]":
                    index += 2
                    continue
                bracketed = False
            index += 1
            continue
        if char in "'\"":
            quote = char
        elif char == "[":
            bracketed = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[opening + 1:index]
        index += 1
    raise ValueError("named CTE is not balanced")


def without_tsql_comments_or_literals(sql: str) -> str:
    """Mask comments and quoted text so source-shape checks see executable text only."""
    return mask_tsql_literals(sql)[0]


def mask_tsql_literals(sql: str) -> tuple[str, tuple[str, ...]]:
    """Return executable source with indexed literal tokens and their decoded values."""
    uncommented = without_tsql_comments(sql)
    output: list[str] = []
    literals: list[str] = []
    literal_value: list[str] = []
    index = 0
    quote: str | None = None
    bracketed = False
    while index < len(uncommented):
        char = uncommented[index]
        if quote is not None:
            output.append(" " if char not in "\r\n" else char)
            if char == quote:
                if index + 1 < len(uncommented) and uncommented[index + 1] == quote:
                    output.append(" ")
                    literal_value.append(quote)
                    index += 2
                    continue
                literals.append("".join(literal_value))
                literal_value = []
                quote = None
            else:
                literal_value.append(char)
            index += 1
            continue
        if bracketed:
            output.append(char)
            if char == "]":
                if index + 1 < len(uncommented) and uncommented[index + 1] == "]":
                    output.append(uncommented[index + 1])
                    index += 2
                    continue
                bracketed = False
            index += 1
            continue
        if char in "'\"":
            quote = char
            output.append(f"__TSQL_LITERAL_{len(literals)}__")
        elif char == "[":
            bracketed = True
            output.append(char)
        else:
            output.append(char)
        index += 1
    return "".join(output), tuple(literals)


def has_tsql_literal_comparison(sql: str, expression: str, expected: str) -> bool:
    """Check that executable `expression = N'literal'` uses the expected value."""
    import re

    masked, literals = mask_tsql_literals(sql)
    pattern = rf"{re.escape(expression)}\s*=\s*N?__TSQL_LITERAL_(\d+)__"
    return any(
        literals[int(match.group(1))].casefold() == expected.casefold()
        for match in re.finditer(pattern, masked, flags=re.IGNORECASE)
    )


def split_tsql_projection_items(projection: str) -> tuple[str, ...]:
    """Split SELECT projection items at top-level commas."""
    source = without_tsql_comments_or_literals(projection)
    items = []
    start = 0
    depth = 0
    bracketed = False
    index = 0
    while index < len(source):
        char = source[index]
        if bracketed:
            if char == "]":
                if index + 1 < len(source) and source[index + 1] == "]":
                    index += 2
                    continue
                bracketed = False
        elif char == "[":
            bracketed = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("projection has unbalanced parentheses")
        elif char == "," and depth == 0:
            items.append(source[start:index].strip())
            start = index + 1
        index += 1
    if depth != 0 or bracketed:
        raise ValueError("projection has unbalanced syntax")
    items.append(source[start:].strip())
    return tuple(items)


def _projection_alias(item: str) -> str | None:
    """Find a trailing AS alias only when AS is outside nested expressions."""
    positions = []
    depth = 0
    bracketed = False
    index = 0
    while index < len(item):
        char = item[index]
        if bracketed:
            if char == "]":
                if index + 1 < len(item) and item[index + 1] == "]":
                    index += 2
                    continue
                bracketed = False
        elif char == "[":
            bracketed = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif depth == 0 and item[index:index + 2].casefold() == "as":
            before = item[index - 1] if index else " "
            after = item[index + 2] if index + 2 < len(item) else " "
            if before.isspace() and after.isspace():
                positions.append(index)
        index += 1
    if not positions:
        return None
    identifier = r"(?:\[[^\]]+(?:\]\][^\]]*)*\]|[A-Za-z_][\w$#@]*)"
    match = re.fullmatch(rf"\s*AS\s+({identifier})\s*", item[positions[-1]:], re.IGNORECASE)
    if match is None:
        return None
    return match.group(1).strip("[]").replace("]]", "]").casefold()


def tsql_projection_output_names(projection: str) -> frozenset[str]:
    """Return output names for simple columns and explicitly aliased items."""
    identifier = r"(?:\[[^\]]+(?:\]\][^\]]*)*\]|[A-Za-z_][\w$#@]*)"
    names = set()
    for item in split_tsql_projection_items(projection):
        alias = _projection_alias(item)
        if alias is not None:
            names.add(alias)
            continue
        column = re.fullmatch(rf"\s*(?:{identifier}\s*\.\s*)*({identifier})\s*", item)
        if column:
            names.add(column.group(1).strip("[]").replace("]]", "]").casefold())
    return frozenset(names)


def tsql_projection_has_exact_item(projection: str, expected_item: str) -> bool:
    """Check for an exact top-level projection item after lexical masking."""
    expected = " ".join(without_tsql_comments_or_literals(expected_item).split()).casefold()
    return any(
        " ".join(item.split()).casefold() == expected
        for item in split_tsql_projection_items(projection)
    )
