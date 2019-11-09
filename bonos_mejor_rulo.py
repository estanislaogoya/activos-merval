import requests
from pandas.io.json import json_normalize
import pandas as pd
import sys
from data import bonoClaseMap, headers

bonos_domain = 'https://api.portfoliopersonal.com/api/Cotizaciones/WatchList/12967?plazoId=3'

response = requests.get(bonos_domain, headers=headers)

df = json_normalize(response.json()['payload'])

def mapKeyToVal(x):
    return bonoClaseMap.get(x)
df['ticker_class'] = df['ticker'].apply(lambda x: mapKeyToVal(x))
df = df[df['ticker_class'] != 'descarte']

def getTickerName(x):
    if (x[-1] == 'D'):
        return x[:-1]
    else:
        return x

df['ticker_name'] = df['ticker'].apply(lambda x: getTickerName(x))

asset = set()

for x in df['ticker']:
    if(x[-1] == "D"):
        asset.add(x[:-1])
    else:
        asset.add(x)


assets = []
pesos = []
dolares = []
dolares_c = []

for a in asset:
    df_1 = df[df['ticker_name'] == a]
    p_pesos = df_1.loc[df_1['ticker_class'] == 'pesos']
    p_pesos = p_pesos['precioCompra'].values
    p_dolares = df_1.loc[df_1['ticker_class'] == 'dolares']
    p_dolares = p_dolares['precioVenta'].values
    pc_dolares = df_1.loc[df_1['ticker_class'] == 'dolares']
    pc_dolares = pc_dolares['precioCompra'].values
    if (p_pesos == 0.0 or p_dolares == 0.0 or pc_dolares == 0.0):
        pass
    else:
        assets.append(a)
        pesos.append(p_pesos)
        dolares.append(p_dolares)
        dolares_c.append(pc_dolares)


dataset = pd.DataFrame({'Asset': assets, 'PCompra Pesos': pesos, 'PVenta Dolares': dolares, 'PCompra Dolares': dolares_c})


def getExchangeRate(sys_args):
    if len(sys_args) != 1:
        return float(sys.argv[1])
    else:
        return 58 #Hardcoded

tc_v = getExchangeRate(sys.argv)

entry_usd = 11000 #Hardcoded

dataset['dolar_mep'] = dataset['PCompra Pesos'] / dataset['PVenta Dolares']
dataset['spread'] = (tc_v - dataset['dolar_mep']) / tc_v
dataset['cant_bon_usd'] = entry_usd / dataset['PVenta Dolares']
dataset['cant_bon_usd'] = dataset['cant_bon_usd'].apply(lambda x: x.astype(int))
dataset['mont_bon_ars'] = (dataset['cant_bon_usd']-(1000/dataset['PVenta Dolares'])) * dataset['PCompra Pesos']
dataset['exit_usd'] = (dataset['mont_bon_ars'] / tc_v)
dataset['mont_bon_usd'] = (1000/dataset['PVenta Dolares']) * dataset['PCompra Dolares']
dataset['gain_usd'] = dataset['exit_usd'] + dataset['mont_bon_usd'] - entry_usd
dataset = dataset.sort_values(by=['gain_usd'], ascending=False)

print(dataset)
