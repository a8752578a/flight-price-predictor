from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from utils import get_historical_prices
from datetime import datetime, timedelta
import pandas as pd

def predict_prices(date, price):
    # api = Ryanair(currency=curr)
    # if not retour:
    #     flights = api.get_cheapest_flights(from_airport, from_date, to_date, destination_airport=to_airport)
    # else:
    #     flights = api.get_cheapest_return_flights(from_airport, from_date, to_date, destination_airport=to_airport)
    # flight: Flight = flights[0]
    # price = flight.price

    historical_prices = get_historical_prices(price)

    model = ARIMA(historical_prices['price'], order=(4, 2, 4))
    model = model.fit()
    model.summary()

    start = len(historical_prices)
    end = len(historical_prices) + (date - datetime.today().date()).days

    preds = pd.DataFrame()
    pred = model.predict(start=start, end=end, typ='levels').rename('ARIMA Predictions')
    curr_date = 0
    for item in pred:
        curr_data = pd.DataFrame([[datetime.today().date() + timedelta(days=curr_date), item]],
                                 columns=['date', 'price'])
        preds = pd.concat([preds, curr_data])
        curr_date += 1

    preds = pd.concat([historical_prices, preds])
    preds = preds.sort_values(by='date', ascending=True)
    preds = preds.reset_index(drop=True)
    # fig = px.line(x=preds['date'], y=preds['price'])
    # fig.show()
    return preds