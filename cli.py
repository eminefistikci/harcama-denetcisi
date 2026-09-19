import argparse
from datetime import date
from decimal import Decimal
from .filters import *
from .reader import *
from .reports import *
from .analytics import *

def main():
    parser=build_parser()
    args=parser.parse_args()
    args.func(args)

def build_parser():
    parser = argparse.ArgumentParser(description = "harcama-denetcisi")
    subparsers = parser.add_subparsers(dest="command", required = True)

    validate_parser=subparsers.add_parser("validate", help="validates the file and the format")
    validate_parser.add_argument("file", help="path of the csv file")
    validate_parser.add_argument("--format", choices =["table", "json"], default ="table", help="output format")
    validate_parser.set_defaults(func=cmd_validate)

    summary_parser =subparsers.add_parser("summary", help="shows the summary")
    summary_parser.add_argument("file", help="path of the csv file")
    summary_parser.add_argument("--format", choices =["table", "json"], default="table")
    summary_parser.add_argument("--start-date")
    summary_parser.add_argument("--end-date")
    summary_parser.add_argument("--currency")
    summary_parser.add_argument("--merchant")
    summary_parser.add_argument("--category", action="append")
    summary_parser.add_argument("--min-amount")
    summary_parser.add_argument("--max-amount")
    summary_parser.set_defaults(func=cmd_summary)

    category_report_parser=subparsers.add_parser("category-report")
    category_report_parser.add_argument("file", help="path of the csv file")
    category_report_parser.add_argument("--format", choices =["table", "json"], default="table")
    category_report_parser.add_argument("--start-date")
    category_report_parser.add_argument("--end-date")
    category_report_parser.add_argument("--min-amount")
    category_report_parser.add_argument("--max-amount")
    category_report_parser.add_argument("--currency")
    category_report_parser.set_defaults(func=cmd_category_report)

    monthly_report_parser=subparsers.add_parser("monthly-report")
    monthly_report_parser.add_argument("file", help="path of the csv file")
    monthly_report_parser.add_argument("--format", choices =["table", "json"], default="table")
    monthly_report_parser.add_argument("--category", action="append")
    monthly_report_parser.add_argument("--min-amount")
    monthly_report_parser.add_argument("--max-amount")
    monthly_report_parser.add_argument("--start-date")
    monthly_report_parser.add_argument("--end-date")
    monthly_report_parser.set_defaults(func=cmd_monthly_report)

    merchant_report_parser=subparsers.add_parser("merchant-report")
    merchant_report_parser.add_argument("file")
    merchant_report_parser.add_argument("--format", choices=["table", "json"], default="table")
    merchant_report_parser.add_argument("--start-date")
    merchant_report_parser.add_argument("--end-date")
    merchant_report_parser.add_argument("--min-amount")
    merchant_report_parser.add_argument("--max-amount")
    merchant_report_parser.add_argument("--currency")
    merchant_report_parser.add_argument("--category")
    merchant_report_parser.add_argument("--top", type=int, default=None)
    merchant_report_parser.set_defaults(func=cmd_merchant_report)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("file")
    search_parser.add_argument("--format", choices=["table", "json"], default="table")
    search_parser.add_argument("--query")
    search_parser.add_argument("--description")
    search_parser.add_argument("--start-date")
    search_parser.add_argument("--end-date")
    search_parser.add_argument("--category", action="append")
    search_parser.add_argument("--min-amount")
    search_parser.add_argument("--max-amount")
    search_parser.set_defaults(func=cmd_search)

    duplicates_parser=subparsers.add_parser("duplicates")
    duplicates_parser.add_argument("file")
    duplicates_parser.add_argument("--format", choices=["table", "json"], default="table")
    duplicates_parser.set_defaults(func=cmd_duplicates)

    recurring_parser=subparsers.add_parser("recurring")
    recurring_parser.add_argument("file")
    recurring_parser.add_argument("--format", choices=["table", "json"], default="table")
    recurring_parser.set_defaults(func=cmd_recurring)

    anomalies_parser=subparsers.add_parser("anomalies")
    anomalies_parser.add_argument("file")
    anomalies_parser.add_argument("--format", choices=["table", "json"], default="table")
    anomalies_parser.add_argument("--multiplier", type=Decimal, default=Decimal("2.5"))
    anomalies_parser.add_argument("--min-amount", type=Decimal, default=Decimal("500"))
    anomalies_parser.set_defaults(func=cmd_anomalies)

    compare_parser=subparsers.add_parser("compare")
    compare_parser.add_argument("file")
    compare_parser.add_argument("--format", choices=["table", "json"], default="table")
    compare_parser.add_argument("--period1", nargs=2, required=True)
    compare_parser.add_argument("--period2", nargs=2, required=True)
    compare_parser.set_defaults(func=cmd_compare)

    export_parser=subparsers.add_parser("export")
    export_parser.add_argument("file")
    export_parser.add_argument("--report", required=True)
    export_parser.add_argument("--output", required=True)
    export_parser.add_argument("--format", choices=[ "json"], default="json")
    export_parser.add_argument("--top", type=int, default=None)
    export_parser.add_argument("--currency", help="Filter by currency")
    export_parser.add_argument("--start-date")
    export_parser.add_argument("--end-date")
    export_parser.add_argument("--category", action="append")
    export_parser.add_argument("--min-amount")
    export_parser.add_argument("--max-amount")
    export_parser.set_defaults(func=cmd_export)

    return parser


def build_filter_from_args(args):
    raw_date = getattr(args, "start_date",None)
    start_date = date.fromisoformat(raw_date) if raw_date else None

    raw_date=getattr(args, "end_date",None)
    end_date=date.fromisoformat(raw_date) if raw_date else None

    raw_categories = getattr(args, "category", None)
    categories = set(raw_categories) if raw_categories else None

    raw_type=getattr(args,"type",None)
    transaction_types = {raw_type} if raw_type else None

    raw_currency = getattr(args,"currency",None)
    currencies = {raw_currency} if raw_currency else None

    merchant =getattr(args,"merchant",None)

    search_text = (
        getattr(args, "query", None)
        or getattr(args, "description", None)
        or getattr(args, "search_text", None)
    )

    raw_val = getattr(args, "min_amount",None)
    min_amount=Decimal(raw_val) if raw_val else None

    raw_val=getattr(args,"max_amount",None)
    max_amount=Decimal(raw_val) if raw_val else None

    return make_transaction_filter(start_date=start_date, 
                            end_date=end_date, 
                            categories=categories, 
                            transaction_types=transaction_types, 
                            currencies=currencies, 
                            merchant=merchant, 
                            search_text=search_text, 
                            min_amount=min_amount, 
                            max_amount=max_amount)


def load_filtered_transactions(args):
    rejected_rows = []
    raw_transactions = iter_transactions(args.file, on_rejected=rejected_rows.append)

    predicate = build_filter_from_args(args)
    valid_transactions = list(apply_filter(raw_transactions, predicate))

    return valid_transactions, rejected_rows

def cmd_validate(args):
    valid_transactions=[]
    rejected_rows=[]

    for item in iter_validation_results(args.file):
        if is_rejected(item):
            rejected_rows.append(item)
        else:
            valid_transactions.append(item)

    print(f"Total row number: {len(rejected_rows) + len(valid_transactions)}")
    print(f"Number of valid rows: {len(valid_transactions)}")
    print(f"Number of rejected rows: {len(rejected_rows)}")

    if rejected_rows:
        print(format_rejected_rows(rejected_rows))
    else:
        print("No rejected rows.")

def cmd_summary(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    result = calculate_summary(valid_transactions)
    print_report(result, output_format=args.format)

    summary_data={
        "summaries": result,
        "rejected_count": len(rejected_rows)
    }
    print_report(summary_data, output_format=args.format)

def cmd_category_report(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    category_report = build_category_report(valid_transactions)
    print_report(category_report, output_format=args.format)

def cmd_monthly_report(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    monthly_report = build_monthly_report(valid_transactions)
    print_report(monthly_report, output_format=args.format)

def cmd_merchant_report(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    merchant_report = build_merchant_report(valid_transactions, top=args.top)
    print_report(merchant_report, output_format=args.format)

def cmd_search(args):
    predicate=build_filter_from_args(args)
    rejected_rows=[]
    transactions=iter_transactions(args.file, on_rejected=rejected_rows.append)
    results=search_transactions(transactions, predicate)
    print_report(results, output_format=args.format)

def cmd_recurring(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    recurring_payments = find_recurring_payments(valid_transactions)
    print_report(recurring_payments, output_format=args.format)

def cmd_duplicates(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    possible_duplicates = find_possible_duplicates(valid_transactions)
    print_report(possible_duplicates, output_format=args.format)

def cmd_anomalies(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    anomalies = find_anomalies(valid_transactions, multiplier=args.multiplier, min_amount=args.min_amount)
    print_report(anomalies, output_format=args.format)

def cmd_compare(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    results = compare_periods(valid_transactions, args.period1, args.period2)
    print_report(results, output_format=args.format)

def cmd_export(args):
    valid_transactions, rejected_rows = load_filtered_transactions(args)
    match args.report:
        case "summary":
            result=calculate_summary(valid_transactions)
        case "category-report":
            result=build_category_report(valid_transactions)
        case "monthly-report":
            result=build_monthly_report(valid_transactions)
        case "merchant-report":
            result=build_merchant_report(valid_transactions, top=args.top)
        case _:
            raise ValueError("Unsupported report type")
        
    export_report(result, args.output, output_format=args.format)


