import pandas as pd
import yfinance as yf
import os.path

YEAR = 4 # Cantidad de caracteres en un año.

# Esta función valida que el input sea un número.
def input_number(message):
  while True:
    try:
       user_input = int(input(message))       
    except ValueError:
       print("El input debe ser un número")
       continue
    else:
       return user_input 
       break 

raw_data_path = os.path.abspath(os.pardir) + "/data/raw/"

# Cargar los tickers que se quieran descargar al correr el script
tickers = []
for  ticker in range(input_number("¿Cuántos tickers quieres traer? ")):
    tickers.append(input('Ticker {}: '.format(ticker+1)))

starting_date = str(input_number("¿Desde que año traer la data? "))+'-01-01'
prices = pd.DataFrame(columns=tickers) # Inicializo el data frame, por ahora con el nombre de las columnas pero sin valores

# Traigo precios de cierre diarios desde la fecha deseada y los guardo en un csv por separado
for ticker in tickers:
    prices[ticker] = yf.download(ticker,start=starting_date)['Adj Close']
    prices[ticker].to_csv(raw_data_path+'{}{}.csv'.format(ticker,starting_date[:YEAR]))
