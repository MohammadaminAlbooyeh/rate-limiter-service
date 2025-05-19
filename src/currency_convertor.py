import requests
from functools import cache, lru_cache   # if you dont use chaetools, you can use functools and lru_cache
from cachetools import cached, TTLCache


ttl_chache = TTLCache(maxsize=100, ttl=600)
@cached(ttl_chache)  # Cache the results of the function for 1000 calls
def get_exchange_rate(base_currency, target_currency):
    """
    This function takes two currencies as input and returns the exchange rate between them.
    """
    
    url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('Failed to get exchange rate')
    
    return response.json()['rates'][target_currency]

@cached(ttl_chache)  # Cache the results of the function for 1000 calls
def convert_currency(amount, exchange_rate):
    return amount * exchange_rate


# Testing the function
if __name__ == '__main__':
    amount = int(input('Enter the amount: '))
    exchange_rate = get_exchange_rate('USD', 'EUR')
    converted_amount = convert_currency(amount, exchange_rate)
    print(f'{amount} USD is {converted_amount: } EUR')