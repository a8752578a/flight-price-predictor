from ryanair import Ryanair
from ryanair.types import Flight
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from ryanair import Ryanair
from ryanair.types import Flight
import pandas as pd

from arima import predict_prices
from ryanair_api import get_flights, convert_to_df

routes_df = pd.read_csv('routes.csv', encoding='ISO-8859-1', delimiter=";")

# Initialize the app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Airplane Ticket Price Predictor", style={
        'fontFamily': 'Arial',
        'fontWeight': 'bold',
        'fontSize': '24px',
        'textAlign': 'center',
        'marginBottom': '20px'  # Adds space below the title
    }),
    dcc.Dropdown(
        id='origin-dropdown',
        options=[{'label': i, 'value': i} for i in sorted(routes_df['origin_city'].unique())],
        value='Budapest,BUD',
        multi=False,
        style={'fontFamily': 'Arial'}
    ),
    dcc.Dropdown(
        id='destination-dropdown',
        options=[],
        value='London,STN',
        multi=False,
        style={'fontFamily': 'Arial'}
    ),
    dcc.DatePickerSingle(
        id='date-picker-from',
        min_date_allowed=datetime.today() + timedelta(days=1),
        max_date_allowed=datetime.today() + timedelta(days=100),
        initial_visible_month=datetime.today(),
        date=datetime.today() + timedelta(days=1),
        display_format='YYYY.MM.DD'
    ),
    dcc.DatePickerSingle(
        id='date-picker-to',
        min_date_allowed=datetime.today() + timedelta(days=1),
        max_date_allowed=datetime.today() + timedelta(days=100),
        initial_visible_month=datetime.today(),
        date=datetime.today() + timedelta(days=1),
        display_format='YYYY.MM.DD'
    ),
    html.Button('Submit', id='submit-button', n_clicks=0, style={'fontFamily': 'Arial'}),
    html.Button('Sort by Price', id='sort-button', n_clicks=0, style={'fontFamily': 'Arial'}),
    dash_table.DataTable(
        id='flights-table',
        columns=[
            {'name': 'departureTime', 'id': 'departureTime'},
            {'name': 'flightNumber', 'id': 'flightNumber'},
            {'name': 'origin', 'id': 'origin'},
            {'name': 'originFull', 'id': 'originFull'},
            {'name': 'destination', 'id': 'destination'},
            {'name': 'destinationFull', 'id': 'destinationFull'},
            {'name': 'price', 'id': 'price'},
            {'name': 'currency', 'id': 'currency'}
        ],
        style_table={'margin': 'auto', 'overflowX': 'scroll'},
        style_cell={'textAlign': 'center', 'fontFamily': 'Arial', 'border': '1px solid black'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#ffffff'},
        style_data_conditional=[
            {
                # 'if': {'row_index': 'selected'},
                'backgroundColor': 'rgba(255, 0, 0, 0.2)',
                'fontWeight': 'bold'
            }
        ],
        data=[],
        row_selectable='single',
        # selected_rows=[],
        page_size=10
    ),
    dcc.Graph(id='line-chart', style={'fontFamily': 'Arial'})
], style={})


@app.callback(
    [Output('date-picker-to', 'min_date_allowed'), Output('date-picker-to', 'max_date_allowed'), ],
    [Input('date-picker-from', 'date'), Input('date-picker-to', 'date')]
)
def update_min_date_allowed_to(selected_date_from, selected_date_to):
    if selected_date_from is not None:
        selected_date_from = datetime.fromisoformat(selected_date_from).date()
        selected_date_to = datetime.fromisoformat(selected_date_to).date()

        return selected_date_from, selected_date_from + timedelta(days=100)
    else:
        return datetime.today() + timedelta(days=1), datetime.today() + timedelta(days=100)


@app.callback(
    [Output('date-picker-from', 'min_date_allowed'), Output('date-picker-from', 'max_date_allowed')],
    [Input('date-picker-to', 'date')]
)
def update_max_date_allowed_from(selected_date):
    if selected_date is not None:
        selected_date = datetime.fromisoformat(selected_date).date()
        return datetime.today() + timedelta(days=1), selected_date
    else:
        return datetime.today() + timedelta(days=1), datetime.today() + timedelta(days=100)


# Callback to update destination dropdown based on origin dropdown selection
@app.callback(
    Output('destination-dropdown', 'options'),
    Input('origin-dropdown', 'value')
)
def set_destination_options(selected_origin):
    destinations = routes_df[routes_df['origin_city'] == selected_origin]['destination_city'].unique()
    return [{'label': i, 'value': i} for i in destinations]


# Callback to update the flights table based on form submission or sorting
@app.callback(
    [Output('flights-table', 'data'), Output('flights-table', 'columns'), Output('flights-table', 'selected_rows')],
    [Input('submit-button', 'n_clicks'), Input('sort-button', 'n_clicks')],
    [State('origin-dropdown', 'value'),
     State('destination-dropdown', 'value'),
     State('date-picker-from', 'date'),
     State('date-picker-to', 'date'),
     State('flights-table', 'data')]
)
def update_flights_table(submit_clicks, sort_clicks, origin, destination, date_from, date_to, current_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [], [], []
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_input == 'submit-button':
        # flights_df = get_flights(origin.split(',')[1], destination.split(',')[1], date_from, date_to)
        flights_df = convert_to_df(origin, destination, datetime.fromisoformat(date_from).date(),
                                   datetime.fromisoformat(date_to).date())
        if not flights_df.empty and not 'Message' in flights_df.columns:
            flights_df['price'] = flights_df['price'].astype(float)
            flights_df['departureTime'] = pd.to_datetime(flights_df['departureTime'], format='ISO8601')
            flights_df.sort_values('departureTime', inplace=True)
        columns = [{'name': col, 'id': col} for col in pd.DataFrame(flights_df).columns]
        return flights_df.to_dict('records'), columns,  []

    elif triggered_input == 'sort-button':
        if not current_data:
            return [], []
        flights_df = pd.DataFrame(current_data)
        if not 'Message' in flights_df.columns:
            flights_df['price'] = flights_df['price'].astype(float)
            flights_df.sort_values('price', inplace=True)
        columns = [{'name': col, 'id': col} for col in pd.DataFrame(flights_df).columns]
        return flights_df.to_dict('records'), columns, []

    return [], []


# Callback to update the line chart based on selected row in the table
@app.callback(
    Output('line-chart', 'figure'),
    [Input('flights-table', 'selected_rows')],
    [State('flights-table', 'data')]
)
def update_graph(selected_rows, current_data):
    if selected_rows is None or not current_data or selected_rows == [] or 'Message' in current_data[0]:
        return px.line(title='Fare Prices Over Time', labels={'x': 'Departure Time', 'y': 'Price'})
    else:
        selected_row = selected_rows[0]
        flight_data = pd.DataFrame(current_data).iloc[selected_row]
        prediction_df = predict_prices(datetime.fromisoformat(str(flight_data['departureTime'])).date(),
                                       flight_data['price'])
        fig = px.line(prediction_df, x='date', y='price', title='Fare Prices Over Time')

        # ezeket probaltam es nem mukodnek

        # current_date = datetime.now().date()
        # current_date_index = prediction_df.loc[prediction_df['date'] == current_date].index[0]
        # print(current_date_index)

        # fig.add_hline(y=flight_data['price'], line_dash='dash', line_color='blue', annotation_text='')
        # fig.add_vline(x=current_date, line_dash='dash', line_color='red', annotation_text='Current Date')
        # fig.update_traces(marker=dict(color='blue', line=dict(color='blue')),
        #                   selector=dict(type='scatter', x=prediction_df['date'] <= current_date))
        # fig.update_traces(marker=dict(color='green', line=dict(color='green')),
        #                   selector=dict(type='scatter', x=prediction_df['date'] > current_date))

        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'xaxis_title': 'Date',
            'yaxis_title': 'Price',
            'font': {'family': 'Arial'}
        })
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
