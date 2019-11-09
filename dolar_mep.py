import requests
from pandas.io.json import json_normalize
import pandas as pd
import sys

headers = {
    "Content-Type": "application/json",
    "AuthorizedClient": "321321321",
    "ClientKey": "pp123456",
    "Referer": "https://api.portfoliopersonal.com/Content/html/proxy.html",
    "Sec-Fetch-Mode": "cors",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
}

bonos_domain = 'https://api.portfoliopersonal.com/api/Cotizaciones/WatchList/12967?plazoId=3'

response = requests.get(bonos_domain, headers=headers)

df = json_normalize(response.json()['payload'])

bonoClaseMap = {'A2E2C' : 'descarte',
'A2E3C' : 'descarte',
'A2E7C' : 'descarte',
'A2E8C' : 'descarte',
'A2J9C' : 'descarte',
'AA21C' : 'descarte',
'AA22C' : 'descarte',
'AA25C' : 'descarte',
'AA26C' : 'descarte',
'AA37C' : 'descarte',
'AA46C' : 'descarte',
'AC17C' : 'descarte',
'AE48C' : 'descarte',
'AO20C' : 'descarte',
'AY24C' : 'descarte',
'DIA0C' : 'descarte',
'DICAC' : 'descarte',
'DICYC' : 'descarte',
'PARAC' : 'descarte',
'PARYC' : 'descarte',
'A2E2D' : 'dolares',
'A2E3D' : 'dolares',
'A2E7D' : 'dolares',
'A2E8D' : 'dolares',
'A2J9D' : 'dolares',
'AA21D' : 'dolares',
'AA25D' : 'dolares',
'AA26D' : 'dolares',
'AA37D' : 'dolares',
'AA46D' : 'dolares',
'AC17D' : 'dolares',
'AE48D' : 'dolares',
'AO20D' : 'dolares',
'AY24D' : 'dolares',
'DIA0D' : 'dolares',
'DICAD' : 'dolares',
'DICPD' : 'dolares',
'DICYD' : 'dolares',
'DIY0D' : 'dolares',
'PAA0D' : 'dolares',
'PARAD' : 'dolares',
'PARYD' : 'dolares',
'PAY0D' : 'dolares',
'A2E2' : 'pesos',
'A2E7' : 'pesos',
'AA21' : 'pesos',
'AA25' : 'pesos',
'AA26' : 'pesos',
'AA37' : 'pesos',
'AA46' : 'pesos',
'AC17' : 'pesos',
'AN18' : 'pesos',
'AO20' : 'pesos',
'AY24' : 'pesos',
'DIA0' : 'pesos',
'DICA' : 'pesos',
'DICY' : 'pesos',
'DIY0' : 'pesos',
'PAA0' : 'pesos',
'PARA' : 'pesos',
'PARY' : 'pesos',
'PAY0' : 'pesos'}

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
pesos_v = []
dolares = []
dolares_c = []

for a in asset:
    df_1 = df[df['ticker_name'] == a]
    p_pesos = df_1.loc[df_1['ticker_class'] == 'pesos']
    p_pesos = p_pesos['precioCompra'].values
    pv_pesos = df_1.loc[df_1['ticker_class'] == 'pesos']
    pv_pesos = pv_pesos['precioVenta'].values
    p_dolares = df_1.loc[df_1['ticker_class'] == 'dolares']
    p_dolares = p_dolares['precioVenta'].values
    pc_dolares = df_1.loc[df_1['ticker_class'] == 'dolares']
    pc_dolares = pc_dolares['precioCompra'].values
    if (p_pesos == 0.0 or p_dolares == 0.0 or pc_dolares == 0.0):
        pass
    else:
        assets.append(a)
        pesos.append(p_pesos)
        pesos_v.append(pv_pesos)
        dolares.append(p_dolares)
        dolares_c.append(pc_dolares)


dataset = pd.DataFrame({'Asset': assets, 'PCompra Pesos': pesos, 'PVenta Pesos': pesos_v, 'PVenta Dolares': dolares, 'PCompra Dolares': dolares_c})


#def getExchangeRate(sys_args):
#    if len(sys_args) != 1:
#        return float(sys.argv[1])
#    else:
#        return 58 #Hardcoded

def getExchangeRate(sys_args):
    if len(sys_args) != 1:
        return float(sys.argv[1])
    else:
        return 64 #Hardcoded

def getEntryArs(sys_args):
    if len(sys_args) != 1 and len(sys_args) != 2 :
        return int(sys.argv[2])
    else:
        return 39000 #Hardcoded

tc_v = getExchangeRate(sys.argv)

entry_ars = getEntryArs(sys.argv)

dataset['cant_bon_ars'] = (entry_ars/dataset['PVenta Pesos'])
dataset['exit_usd'] = (dataset['cant_bon_ars'] * dataset['PCompra Dolares'])
dataset['dolar_mep'] = dataset['PVenta Pesos'] / dataset['PCompra Dolares']
dataset['spread'] = (tc_v - dataset['dolar_mep']) / tc_v
print(dataset)
