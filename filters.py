numbers= [1,2,3]

"""
it = iter(numbers)
try:
    next(it)
except StopIteration:
    print("Akıs bitti")"""

def count_up(start, stop):
    for i in range(start, stop):
        yield i