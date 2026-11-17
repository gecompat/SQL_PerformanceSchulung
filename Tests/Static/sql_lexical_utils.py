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
