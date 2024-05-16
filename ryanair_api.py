import requests
from datetime import datetime, timedelta
import pandas as pd


def get_flights(origin, destination, date_from, date_to):
    # flights = api.get_cheapest_flights(airport=origin, date_from=date,
    #                                    date_to=date, destination_airport=destination)
    url = "https://services-api.ryanair.com/farfnd/v4/oneWayFares?&departureAirportIataCode=" + str(origin) \
          + "&outboundDepartureDateFrom=" + str(datetime.fromisoformat(date_from).strftime("%Y-%m-%d")) \
          + "&outboundDepartureDateTo=" + str(datetime.fromisoformat(date_to).strftime("%Y-%m-%d")) \
          + "&arrivalAirportIataCode=" + destination
    try:
        # Make HTTP GET request
        response = requests.get(url)
        # Parse response content as JSON
        response_json = response.json()

        # Example processing - returning the parsed JSON
        fare = response_json.get('fares')[0]  # Assuming there's only one fare in the response
        flight_dict = {
            'departureTime': fare['outbound']['departureDate'],
            'flightNumber': fare['outbound']['flightNumber'],
            'origin': fare['outbound']['departureAirport']['iataCode'],
            'originFull': fare['outbound']['departureAirport']['city']['name'],
            'destination': fare['outbound']['arrivalAirport']['iataCode'],
            'destinationFull': fare['outbound']['arrivalAirport']['city']['name'],
            'price': fare['summary']['price']['value'],
            'currency': fare['summary']['price']['currencyCode']
        }
        f_df = pd.DataFrame([flight_dict])
        return f_df
    except Exception as e:
        print("Asafdg")
        return f"Error: {str(e)}"


def dates_between(date_from, date_to):
    dates_list = []
    current_date = date_from

    while current_date <= date_to:
        dates_list.append(current_date)
        current_date += timedelta(days=1)

    return dates_list


def convert_to_df(origin, destination, date_from, date_to):
    dates = dates_between(date_from, date_to)
    flights_df = pd.DataFrame(columns=['departureTime', 'flightNumber', 'origin', 'originFull', 'destination',
                                       'destinationFull', 'price', 'currency'])

    for date in dates:
        date = date.strftime("%Y-%m-%d")
        flight = get_flights(origin.split(',')[1], destination.split(',')[1], date, date)
        if isinstance(flight, str) and flight == 'Error: list index out of range':
            continue

        flights_df = pd.concat([flights_df, flight], ignore_index=True)

    if flights_df.empty:
        data = {'Message': ['No flights on the given dates for these places']}
        flights_df = pd.DataFrame(data)

    return flights_df
