"""Small lexical helpers for static T-SQL source contracts."""
from __future__ import annotations


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
