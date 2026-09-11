from decimal import Decimal
import functools

def make_transaction_filter(*, start_date=None, 
                            end_date=None, 
                            categories=None, 
                            transaction_types=None, 
                            currencies=None, 
                            merchant=None, 
                            search_text=None, 
                            min_amount=None, 
                            max_amount=None):

    def inner(transaction):
        if start_date is not None and transaction.date < start_date:
            return False
        if end_date is not None and transaction.date > end_date:
            return False
        if categories is not None and transaction.category.lower() not in [c.lower() for c in categories]:
            return False
        if transaction_types is not None and transaction.transaction_type not in transaction_types:
            return False
        if currencies is not None and transaction.currency not in currencies:
            return False
        if merchant is not None and transaction.merchant.lower() != merchant.lower():
            return False
        if search_text is not None and search_text.lower() not in transaction.merchant.lower() and search_text.lower() not in transaction.description.lower():
            return False
        if min_amount is not None and Decimal(transaction.amount) < Decimal(min_amount):
            return False
        if max_amount is not None and Decimal(transaction.amount) > Decimal(max_amount):
            return False
        return True

    return inner

def compose_filters(*predicates):
    def inner(transaction):
        for predicate in predicates:
            if not predicate(transaction):
                return False
        return True
    return inner

def apply_filter(transactions, predicate):
    for transaction in transactions:
        filter(predicate, transaction)

def is_in_period(transaction, *, start_date, end_date):
    return transaction.date >= start_date and transaction.date <= end_date

def make_period_filter(start_date, end_date):
    return functools.partial(is_in_period, start_date= start_date, end_date= end_date)