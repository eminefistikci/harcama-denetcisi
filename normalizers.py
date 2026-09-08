from functools import lru_cache

@lru_cache
def normalize_text(value):
    return value.strip().lower()

def normalize_currency(value) -> str :
    return value.strip().upper()

def month_key(transaction) -> str:
    return transaction.transaction_date.strftime("%Y-%m")

def merchant_key(transaction):
    return normalize_text(transaction.merchant)

def category_key(transaction):
    return normalize_text(transaction.category)