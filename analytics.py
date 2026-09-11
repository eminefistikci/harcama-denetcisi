from models import *
import itertools

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
            "net": net_expense
        }
    return totals

def build_category_report(transactions):
    key_func = lambda x:(x.category, x.currency)
    totals = group_totals(transactions, key_func)
    currency_totals = {}
    for (category, currency), stats in totals:
        net = stats["net"]
        expense = stats["expense"]
        


    
