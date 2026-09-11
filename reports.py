from pydantic import model_dump_json
from decimal import Decimal
import datetime
from datetime import date
import json
from contextlib import contextmanager
import os

def format_table(report_data):
    if not report_data:
        return "No matching data found."

    headers = [str(k) for k in (report_data[0].model_dump().keys() if hasattr(report_data[0], "model_dump")
               else report_data[0].keys())] #!!
    
    max_weight = []

    formatted_rows = []
    for row in report_data:
        if len(row) > max_weight:
            max_weight = len(row)

        if hasattr(row, "model_dump"):
            row = row.model_dump()

        row_values=[]
        for val in row.values():

            if isinstance(val, (Decimal, float)):
                formatted_val = f"{val:.2f}"
            elif isinstance(val, (date, datetime)):
                formatted_val = val.isoformat()
            else:
                formatted_val = str(val)
            row_values.append(formatted_val)
        formatted_rows.append(row_values)

    """
    widths = [
        max(len(h), max(len(val) for val in col))
        for h, col in zip(headers, zip(*formatted_rows))
    ]

    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    separator_line = "-+-".join("-" * w for w in widths)
    data_lines = [
        " | ".join(val.ljust(w) for val, w in zip(row, widths))
        for row in formatted_rows
    ]

    return "\n".join([header_line, separator_line, *data_lines])
    """

#sütunları hizala


def format_json(report_data):
    if not report_data:
        return "No report data"
    if hasattr(report_data[0], "model_dump"):
        data = [model.model_dump(mode = "json") for model in report_data]
        return json.dumps(data, indent=2)
    elif isinstance(report_data[0], dict):
        return json.dumps(report_data, default = str, indent =2)

def print_report(report_data, *, output_format):
    format_registry = {"table": format_table , "json": format_json}
    format_func = format_registry.get(output_format)
    if not format_func:
        raise ValueError(f"Invalid format: {output_format}")
    print(format_func(report_data))


@contextmanager
def atomic_writer(path):
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w") as f:
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