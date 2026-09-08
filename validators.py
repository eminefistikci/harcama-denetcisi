from models import Transaction, RejectedRow
from pydantic import ValidationError

def validate_headers(headers):
    required_headers = ["transaction_id", "transaction_date", "merchant","category", "transaction_type", "amount", "currency"]
    for header in required_headers:
        if header not in headers:
            raise ValueError(f"Required header {header} is missing.")

def validation_error_to_messages(error):
    error_messages = []
    for item in error.errors():
        loc = item["loc"][0]
        msg = item["msg"]
        error_messages.append(f"{loc}: {msg}")
    return error_messages

def validate_transaction_row(row, line_number, seen_ids)-> Transaction | RejectedRow:
    if row.get("transaction_id") in seen_ids:
        return RejectedRow(row_number= line_number, row_data=row, error_messages=["Duplicate transaction_id"])
    try:
        row = Transaction.model_validate(row)
        seen_ids.add(row.transaction_id)
        return row
    except ValidationError as exc:
        return RejectedRow(row_number=line_number, row_data= row, error_messages=validation_error_to_messages(exc))


def is_rejected(value):
    return isinstance(value, RejectedRow)