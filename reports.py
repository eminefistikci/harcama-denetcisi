from decimal import Decimal
from datetime import date
import json
from contextlib import contextmanager
import os

def format_table(report_data):
    if not report_data:
        return "No matching data found."

    items = (list(report_data.values()) if isinstance(report_data, dict) else report_data)

    if isinstance(items[0], list):
        items = [x for sub in items for x in sub]

    rows = [item.model_dump() if hasattr(item, "model_dump") else item for item in items]
    headers = list(rows[0].keys())

    str_rows=[[f"{r.get(h):.2f}" if isinstance(r.get(h), Decimal) else str(r.get(h, "-")) for h in headers] for r in rows]

    widths = [max(len(h), max(len(row[i]) for row in str_rows)) for i, h in enumerate(headers)]

    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    sep_line = "-+-".join("-" * w for w in widths)
    data_lines = [
        " | ".join(val.ljust(w) for val, w in zip(row, widths))
        for row in str_rows
    ]

    return "\n".join([header_line, sep_line, *data_lines])


def serialize_helper(o):
    if hasattr(o, "model_dump"):
        return o.model_dump(mode="json")
    elif isinstance(o, Decimal):
        return float(o)
    elif isinstance(o, date):
        return o.isoformat()
    else:
        return str(o)
    
def format_json(report_data):
    if not report_data:
        return "[]"

    return json.dumps(
        report_data,
        default= serialize_helper,
        indent=2
    )

def print_report(report_data, *, output_format):
    format_registry = {
        "table": format_table,
        "json": format_json
    }
    format_func = format_registry.get(output_format)
    if not format_func:
        raise ValueError(f"Invalid format: {output_format}")
    print(format_func(report_data))


@contextmanager
def atomic_writer(path):
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            yield f
        os.replace(temp_path, path)
    except Exception as exc:
        os.remove(temp_path)
        raise exc


def export_report(report_data, path, *, output_format):
    format_registry = {"table": format_table , "json": format_json}
    format_func = format_registry.get(output_format)
    if not format_func:
        raise ValueError(f"Invalid format: {output_format}")
    content = format_func(report_data)

    with atomic_writer(path) as f:
        f.write(content)

def format_rejected_rows(rejected_rows):
    lines=[]
    if not rejected_rows:
        return "No rejected rows. "
    for row in rejected_rows:
        message = f"{row.row_number}, {row.row_data.get("transaction_id")}, {",".join(row.error_messages)}"
        lines.append(message)
    return "\n".join(lines)