from models import *
import itertools
from normalizers import *
from filters import *
from decimal import Decimal
from datetime import timedelta

def calculate_summary(transactions):
    summaries={}
    transaction_list = list(transactions)
    key_func = lambda x: x.currency
    transaction_list.sort(key = key_func)
    groups = list(itertools.groupby(transaction_list, key=key_func))

    for currency, group in groups:
        items = list(group)
        expenses = [item for item in items if item.transaction_type == "expense"]
        incomes= [item for item in items if item.transaction_type == "income"]
        refunds =[item for item in items if item.transaction_type == "refund"]

        transaction_count = len(items)
        total_expense = sum(item.amount for item in expenses)
        total_income = sum(item.amount for item in incomes)
        total_refund = sum(item.amount for item in refunds)
        net_expense = total_expense - total_refund
        cash_flow = total_income - net_expense
        max_expense = max(expenses, key=lambda x:x.amount, default=None)
        
        category_totals = {category: sum(item.amount for item in group) for category, group in itertools.groupby(sorted(expenses, key = lambda x:x.category), key=lambda x:x.category)}
        top_category = max(category_totals, key = category_totals.get)

        start_date = min(item.transaction_date for item in items)
        end_date=max(item.transaction_date for item in items)

        summaries[currency] = CurrencySummary(transaction_count=transaction_count,
                               total_expense=total_expense,
                               total_income=total_income,
                               total_refund=total_refund,
                               net_expense=net_expense,
                               cash_flow=cash_flow,
                               max_expense=max_expense,
                               top_category=top_category,
                               start_date=start_date,
                               end_date=end_date,
                               currency=currency)

    return summaries

def group_totals(transactions, key):
    totals ={}
    for key_item, group in itertools.groupby(sorted(transactions, key = key), key=key):
        items = list(group)
        total_expense = sum(item.amount for item in items if item.transaction_type == "expense")
        total_refund = sum(item.amount for item in items if item.transaction_type == "refund")
        net_expense = total_expense - total_refund

        totals[key_item] = {
            "expense": total_expense,
            "refund": total_refund,
            "net": net_expense,
            "count": len(items)
        }
    return totals

def build_category_report(transactions):
    transactions = list(transactions)

    key_func = lambda x:(x.category, x.currency)
    totals = group_totals(transactions, key_func)
    summaries = calculate_summary(transactions)

    category_report = []

    for (category, currency), stats in totals.items():
        count = stats["count"]
        expense = stats["expense"]
        refund = stats["refund"]
        net = stats["net"]
        percentage = (net * 100) / summaries[currency].net_expense if summaries[currency].net_expense > 0 else 0

        category_report.append({
                                "category": category,
                                "currency":currency,
                                "count":count,
                                "expense":expense,
                                "refund":refund,
                                "net":net,
                                "percentage":percentage
        })
    return sorted(category_report, key=lambda x: x["net"], reverse=True)

def build_monthly_report(transactions):
    transactions = list(transactions)
    key = lambda x : (month_key(x), x.currency)

    monthly_report = []
    for (month, currency), group in itertools.groupby(sorted(transactions, key=key), key=key):
        items = list(group)
        income = sum(item.amount for item in items if item.transaction_type =="income")
        refund = sum(item.amount for item in items if item.transaction_type=="refund")
        expense = sum(item.amount for item in items if item.transaction_type == "expense")
        net= expense-refund
        cash_flow = income-net

        monthly_report.append({
                                "month":month,
                                "currency":currency,
                                "income":income,
                                "refund":refund,
                                "expense":expense,
                                "net":net,
                                "cash_flow":cash_flow
        })
    return sorted(monthly_report, key=lambda x:x["month"])


def build_merchant_report(transactions,*, top=None):
    transactions = list(transactions)
    key = lambda x: (merchant_key(x), x.currency)

    merchant_report = []

    for (merchant, currency), group in itertools.groupby(sorted(transactions, key=key), key=key):
        items = list(group)
        total_expense = sum(item.amount for item in items if item.transaction_type == "expense")
        total_refund = sum(item.amount for item in items if item.transaction_type == "refund")
        net_expense = total_expense - total_refund
        transaction_count = len([item for item in items if item.transaction_type=="expense" or item.transaction_type == "refund"])

        merchant_report.append({
                                "merchant":merchant,
                                "currency":currency,
                                "total_expense": total_expense,
                                "total_refund": total_refund,
                                "net_expense": net_expense,
                                "transaction_count":transaction_count
        })
    merchant_report.sort(key= lambda x: x["total_expense"], reverse=True)

    if top is not None:
        return merchant_report[:top]
    return merchant_report


def search_transactions(transactions, predicate):
    return sorted(apply_filter(transactions, predicate), key = lambda x:x.transaction_date)

def find_recurring_payments(transactions):
    key = lambda x: (merchant_key(x), x.currency)
    recurring_payment=[]
    transactions = [t for t in transactions if t.transaction_type == "expense"]

    for (merchant, currency), group in itertools.groupby(sorted(transactions, key=key), key=key):
        items = list(group)
        if len(items) < 3:
            continue

        items.sort(key=lambda x:x.transaction_date)
        max_payment= max(item.amount for item in items)
        min_payment =min(item.amount for item in items)

        if (max_payment-min_payment) / min_payment > Decimal("0.05"):
            continue

        valid_intervals=True
        for i in range(len(items)-1):
            if 25 <= items[i+1].transaction_date.days - items[i].transaction_date.days <= 35:
                continue
            else:
                valid_intervals=False
                break

        if not valid_intervals:
            continue

        average_amount=sum(item.amount for item in items)/len(items)
        first_date=items[0].transaction_date
        last_date=items[-1].transaction_date

        recurring_payment.append({
                                "merchant": merchant,
                                "currency":currency,
                                "average_amount": average_amount,
                                "count":len(items),
                                "first_date":first_date,
                                "last_date":last_date,
                                "next_date":last_date+timedelta(days=30)
        })
    return recurring_payment

def find_possible_duplicates(transactions):
    key = lambda x:(x.transaction_date, merchant_key(x), x.transaction_type, x.amount, x.currency)
    possible_duplicates=[]

    for _, group in itertools.groupby(sorted(transactions, key=key), key=key):
        items = list(group)
        if len(items) > 1 and len({item.transaction_id for item in items}) > 1:
            possible_duplicates.append(items)
    return possible_duplicates


def find_anomalies(transactions,*,multiplier=Decimal("2.5"), min_amount=Decimal("500")):
    key = lambda x: (x.category, x.currency)
    anomalies=[]

    transactions = [t for t in transactions if t.transaction_type=="expense"]
    for _, group in itertools.groupby(sorted(transactions, key=key), key=key):
        items = list(group)
        if len(items) <4:
            continue

        items.sort(key=lambda x: x.amount)
        median = items[len(items)//2].amount if len(items)%2==1 else (items[len(items)//2 -1].amount + items[len(items)//2].amount) / Decimal(2)
        for item in items:
            if item.amount >= min_amount and item.amount >= median*multiplier:
                ratio = (item.amount /median) if median !=Decimal("0") else Decimal("0")
                anomalies.append({
                    "transaction": item,
                    "median": median,
                    "ratio": ratio
                })
    return anomalies
            
def calculate_diff(a, b):
    abs_diff = b-a
    perc_change = ((b-a)/a)*100 if a!=0 else None
    return {"a": a, "b":b,"diff": abs_diff, "perc_change": perc_change}

def compare_periods(transactions, period_a, period_b):
    filter_a = make_period_filter(*period_a)
    filter_b = make_period_filter(*period_b)

    tx_a = [t for t in transactions if filter_a(t)]
    tx_b = [t for t in transactions if filter_b(t)]

    sum_a = calculate_summary(tx_a)
    sum_b = calculate_summary(tx_b)

    category_a = build_category_report(tx_a)
    category_b = build_category_report(tx_b)

    currencies = set(sum_a.keys()) | set(sum_b.keys())
    results = {}
    for currency in currencies:
        sa = sum_a.get(currency)
        sb = sum_b.get(currency)

        cats_a = category_a.get(currency, {})
        cats_b = category_b.get(currency, {})
        all_cats = set(cats_a.keys()) | set(cats_b.keys())

        categories_diff = {
            cat: calculate_diff(
                cats_a.get(cat, Decimal("0")),
                cats_b.get(cat, Decimal("0"))
            )
            for cat in all_cats
        }

        results[currency] = {
            "income": calculate_diff(getattr(sa, "income", Decimal("0")), getattr(sb, "income", Decimal("0"))),
            "expense": calculate_diff(getattr(sa, "expense", Decimal("0")), getattr(sb, "expense", Decimal("0"))),
            "refund": calculate_diff(getattr(sa, "refund", Decimal("0")), getattr(sb, "refund", Decimal("0"))),
            "net_expense": calculate_diff(getattr(sa, "net_expense", Decimal("0")), getattr(sb, "net_expense", Decimal("0"))),
            "categories": categories_diff,
        }

    return results




    
