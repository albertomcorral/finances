import numpy as np                               # vectors and matrices
import pandas as pd                              # tables and data manipulations
import matplotlib.pyplot as plt


def macd(prices, small_span, large_span, macd_span):                                    # The function takes the datarame where iloc[0] is the list of prices, and three spans of time
    prices['fast_ema'] = prices.iloc[:,0].ewm(span=small_span, adjust=False).mean()     # fast average, smaller span of days
    prices['slow_ema'] = prices.iloc[:,0].ewm(span=large_span, adjust=False).mean()     # slow average, larger span of days
    prices['macd_signal'] = prices['fast_ema'] - prices['slow_ema']                     # macd signal
    prices['macd_ema'] = prices['macd_signal'].ewm(span=macd_span, adjust=False).mean() # macd exponential moving average
    prices['macd_oscillator']=prices['macd_signal']-prices['macd_ema']
    prices['macd_position']=np.where(prices['macd_signal']>prices['macd_ema'],1,0)      # Calculates when macd_signal is over macd_ema
    prices['macd_signal']=prices['macd_position'].diff()                                # Indicates with +1/-1 when to buy/sell
    prices['position']=np.where(prices['macd_signal']>prices['macd_ema'],1,0)
    prices['signal']=prices['position'].diff()
    return prices                                                                       # the function returns the expanded dataframe

def plotMacd(prices):
    plt.figure()
    prices.iloc[:,0].plot(style='b')
    prices.loc[prices['signal'] == 1, prices.columns[0]].plot(style='g^ ')
    prices.loc[prices['signal'] == -1, prices.columns[0]].plot(style='rv ')
    plt.savefig('{}-PricesMACD.png'.format(prices.columns[0]))
    plt.figure()
    prices['macd_signal'].plot(style='b')
    prices['macd_ema'].plot(style='c')
    prices['macd_signal'].loc[prices['signal'] == 1].plot(style='g^ ')
    prices['macd_signal'].loc[prices['signal'] == -1].plot(style='rv ')
    plt.savefig('{}-MACDSignal.png'.format(prices.columns[0]))
    return

def portfolio(prices, starting_capital, positions, commission, stoploss_percentage):
    
    portfolio = pd.DataFrame(index=prices.index)
    df = pd.DataFrame(index=prices.index)
    prices = stoploss (prices, stoploss_percentage)                             # llamo a la funcion stop loss para modificar la señal
    portfolio['signal'] = prices['signal'].clip(-1,1).fillna(0)                 # traigo la señal y lleno los NA con 0
    portfolio['cash'] = np.ones(len(portfolio.index)) * starting_capital        # Inicializo cash con starting_capital
    portfolio['holdings'] = np.zeros(len(portfolio.index))                      # Inicializo holdings con 0
    portfolio['qty_stocks'] = np.zeros(len(portfolio.index))                    # Inicializo la cantidad de stocks por fecha con 0

    for i in portfolio.index:                                                   # Recorro el portfolio por fecha
        df['holdings_sftd'] = portfolio['holdings'].shift().fillna(0)           # Creo un vector shifted para traer el valor de la fecha anterior
        df['cash_sftd'] = portfolio['cash'].shift().fillna(starting_capital)    # Creo un vector shifted para traer el valor de la fecha anterior
        df['qty_stocks_sftd'] = portfolio['qty_stocks'].shift().fillna(0)       # Creo un vector shifted para traer el valor de la fecha anterior

        if portfolio['signal'].loc[i] == 0:                                     # Si no hay que operar
            portfolio['qty_stocks'].loc[i] = df['qty_stocks_sftd'].loc[i]       # igualo la cantidad de stocks
            portfolio['holdings'].loc[i] = df['qty_stocks_sftd'].loc[i] * prices.iloc[:,0].loc[i]   # Actualizo holdings con el precio actual
            portfolio['cash'].loc[i] = df['cash_sftd'].loc[i]                   # Igual el cash

        elif portfolio['signal'].loc[i] == 1:                                   # si hay que comprar
            portfolio['qty_stocks'].loc[i] = min(positions, np.floor(df['cash_sftd'].loc[i] / (prices.iloc[:,0].loc[i] * (1+ commission))))     # calculo la cantida de stocks a comprar como el minimo entre positions y lo que me alcanza con el cash anterior
            portfolio['holdings'].loc[i] = portfolio['qty_stocks'].loc[i] * prices.iloc[:,0].loc[i]     # Calculo los holidngs en base a la cantida de stock a comprar
            portfolio['cash'].loc[i] = df['cash_sftd'].loc[i] - portfolio['holdings'].loc[i] * (1+commission)   # Resto del cash anterior los holdings por la comisión


        elif portfolio['signal'].loc[i] == -1:                                  # si hay que vender
            portfolio['holdings'].loc[i] = 0                                    # Actualizo los holdings a cero
            portfolio['qty_stocks'].loc[i] = 0                                  # Actualizo la cantidad de stocks a cero
            portfolio['cash'].loc[i] = df['cash_sftd'].loc[i] + df['qty_stocks_sftd'].loc[i] * prices.iloc[:,0].loc[i] * (1-commission)     # Actualizo el cash con lo que recupero

        else: # error
            return -1

    portfolio['total_capital']= portfolio['holdings'] + portfolio['cash']       # Calculo el total capital como la suma de los holdings más el cash
    portfolio['return']=portfolio['total_capital'].pct_change().fillna(0)       # Calculo el retorno día a día como porcentaje del cambio de total_capital

    return portfolio                                                            # Devuelvo el dataframe de portfolio

def stoploss (prices,stoploss_percentage):


    df = pd.DataFrame(index=prices.index)
    df['local_max'] = prices['signal'].cumsum()
    df = df.fillna(0)
    df['local_max'].loc[prices['signal'] == 1] = prices.iloc[:,0]                   # Traigo los valores de las acciones al momento de comprar
    local_max = 0
    for i in prices.loc[prices['signal'].cumsum()+prices['signal'] != 0].index:     # Descarto donde no tengo acciones y tampoco opero para tener menos ciclos. 
                                                                                    # La + trae las fechas donde vendo
        if prices['signal'].loc[i] == -1:                                           # Si la señal era de vender, anulo el maximo historico local
            local_max = 0
        elif prices.iloc[:,0].loc[i] > local_max:                                   # Si tengo acciones, y el valor actual es mayor al historico local, lo actualizo
            local_max = prices.iloc[:,0].loc[i]

        df['local_max'].loc[i] = local_max                                          # Guardo el maximo historico local de referencia

    df['percentage'] = np.where(df['local_max'] != 0, -(df['local_max']-prices.iloc[:,0])/df['local_max'] , 0)      # Calculo el cambio porcentual con respecto al maximo
    prices['signal'] = np.where(df['percentage'] <= -stoploss_percentage , -1 , prices['signal'])                                   # Donde el cambio es mayor a stoploss_percentage, doy la orden de venta
    
    #If there are more than one consecutive identical order
    last_operation = 0
    for i in prices.loc[prices['signal'] != 0].index:                            # Recorro los indices donde la señal indica operaciones
        if prices['signal'].loc[i] == last_operation:                            # Si la señal es la misma que la anterior
            prices['signal'].loc[i] = 0                                          # ... la anulo
        else:
            last_operation = prices['signal'].loc[i]                             # ... y sino guardo la nueva operación

    return prices