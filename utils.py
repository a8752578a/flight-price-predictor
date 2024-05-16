import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def get_historical_prices(price):
    historical_prices = pd.DataFrame()
    curr_data = pd.DataFrame([[datetime.today().date(), price]], columns=['date', 'price'])
    historical_prices = pd.concat([historical_prices, curr_data])
    curr_price = price
    for i in range(1, 60):
        next_price_low = curr_price * 0.9
        next_price_top = curr_price * 1.1
        curr_price = np.random.uniform(next_price_low, next_price_top)
        curr_data = pd.DataFrame([[datetime.today().date() - timedelta(days=i), curr_price]], columns=['date', 'price'])
        historical_prices = pd.concat([historical_prices, curr_data])

    historical_prices = historical_prices.sort_values(by='date', ascending=True)
    historical_prices = historical_prices.reset_index(drop=True)
    return historical_prices
        
    