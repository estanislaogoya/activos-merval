import requests
from pandas.io.json import json_normalize
import pandas as pd
from data import bonoClaseMap, headers, stocksClaseMap, monthClaseMap

options_domain = 'https://api.portfoliopersonal.com/api/Cotizaciones/WatchList/12955?cotizacionSimplificada=true&plazoId=2'

stocks_domain = 'https://api.portfoliopersonal.com/api/Cotizaciones/WatchList/12964?plazoId=3'

response_options = requests.get(options_domain, headers=headers)

now = pd.Timestamp.now()

df = json_normalize(response_options.json()['payload'])

response_options = requests.get(stocks_domain, headers=headers)

df_stocks = json_normalize(response_options.json()['payload'])

def mapKeyToVal(x):
    return stocksClaseMap.get(x)

def mapNameToMonth(x):
    return monthClaseMap.get(x)

def getTicker(x):
    return x[0:3]
def getOrderType(x):
    return x[3:4]
def getMonth(x):
    if hasNumbers(x[-2:]):
        return x[-1:]
    else:
        return x[-2:]
    
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def getPrice(x):
    idx = 0
    for i, c in enumerate(x):
        if c.isdigit():
            firstdig = i
            break
    
    for i, c in enumerate(x):
        if c.isdigit() or c == '.':
            idx = idx + 1
    return x[firstdig:(firstdig+idx)]

df_tick = df['ticker'].apply(getTicker)
df_type = df['ticker'].apply(getOrderType)
df_month = df['ticker'].apply(getMonth)
df_price = df['ticker'].apply(getPrice)

df_2 = pd.concat([df_tick, df_type, df_month, df_price], axis=1, sort=False, keys=["ticker_name","order_type","month","price"])                  

df = pd.concat([df, df_2], axis=1, sort=False)
df["price"] = pd.to_numeric(df["price"])

df = df[df.cantVenta != 0]
df['total_price'] = df.precioVenta + df.price
df['time'] = now

df['ticker_name_2'] = df['ticker_name'].apply(lambda x: mapKeyToVal(x))
df = df[df['ticker_name_2'] != '']

df_stocks = df_stocks[df_stocks['cantCompra']>0]
df_stocks = df_stocks[['ticker','precioCompra']]

df_stocks['ticker_name_2'] = df_stocks['ticker']

df_merged = pd.merge(df, df_stocks, how='left', on='ticker_name_2')

df_merged['contract_date'] = df_merged['month'].apply(lambda x: mapNameToMonth(x))
df_merged['exp_gain'] = (df_merged['total_price'] / df_merged['precioCompra_y']) - 1
df_merged = df_merged[df_merged['cantVenta']>0]
df_merged = df_merged[df_merged['order_type'] == 'C']

#Calculo diferencia de dias entre fecha del contrato vs hoy
df_merged['diff_days'] = (df_merged['contract_date'] - df_merged['time']) / pd.offsets.Day(1)

#Calculo tasa implicita ((total_price/cantVenta)-1)*365/diff_days
df_merged['implicit_rate'] = (df_merged['exp_gain'] * 365) / df_merged['diff_days']

df_merged.sort_values(by=['implicit_rate'], ascending=True)

df_merged.to_excel("opciones_raw.xlsx")


#df.groupby(['ticker_name','month','order_type'], sort=False)['total_price'].min()