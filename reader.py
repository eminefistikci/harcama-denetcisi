from validators import *
from models import *
import csv
import itertools

def iter_csv_rows(path):
    with open(path, "r") as file:
        reader = csv.DictReader(file)
        validate_headers(reader.fieldnames)
        row_num = 2
        for row in reader:
            yield (row_num, row)
            row_num += 1

def iter_validation_results(path):
    seen_ids = set()

    for row_num, row in iter_csv_rows(path):
        yield validate_transaction_row(row,row_num, seen_ids)

def iter_transactions(path, *, on_rejected=None):
    for item in iter_validation_results(path):
        if not is_rejected(item):
            yield item
        else:
            if on_rejected is not None:
                on_rejected(item)
            continue

def iter_many_transactions(paths, *, on_rejected=None):
    for path in paths:
        yield from iter_transactions(path, on_rejected=on_rejected)

def preview_transactions(transactions, limit):
    return list(itertools.islice(transactions, limit))