import json
import pandas as pd
import time
import talib
from HuobiDMService import HuobiDM
from sendEmail import qqEmail


def BuyK30(closed,ma3,rsi,macd,adx):
    position = 0
    priceD1 = 0
    step1 = False

    if ma3[-1]<ma3[-2]<ma3[-3] and ma3[-6]<ma3[-5]<ma3[-4]<ma3[-3]:
        priceD1 = max(closed[-6:-1])
        rsiD1 = max(rsi[-6:-1])
        macdD1 = max(macd[-6:-1])
        adxD1 = max(adx[-6:-1])
        if rsiD1 >70 and adxD1>30 and macdD1>1:
            for i in range(10, 200):
                if ma3[-i - 2] < ma3[-i - 1] < ma3[-i] and ma3[-i + 2] < ma3[-i + 1] < ma3[-i]:
                    priceD2 = max(closed[-i - 3:-i + 2])
                    macdD2 = max(macd[-i - 3:-i + 2])
                    if macdD2 > macdD1 and priceD2 < priceD1:
                        rsiD2 = max(rsi[-i - 3:-i + 2])
                        adxD2 = max(adx[-i - 3:-i + 2])
                        step1 = True
                        break
    if step1:
        position = 0.3
        if adxD2 > adxD1:
            position += 0.2
        if rsiD2 > rsiD1:
            position += 0.1

    return [position,priceD1]


def BuyKoperation(account_info,dm,last_price,contract_size,position,priceD1):
    price = last_price * (1 - 0.001)
    volume_add = int(account_info['margin_available']*last_price*5*position/contract_size)
    status ='error'
    retryC=0
    while (status !='ok'):
        try:
            response=dm.send_contract_order(symbol='ETH', contract_type='quarter', contract_code='ETH200925',
                                              client_order_id='', price='', volume=volume_add, direction='sell',
                                              offset='open', lever_rate=5, order_price_type='optimal_10_ioc')
            status=response['status']
        except:
            retryC += 1
            if (retryC == 20):
                qqEmail('BuyK is error!')
                with open("test_account_info.json", "w") as dump_f:
                    json.dump(account_info, dump_f)
                print('connect ws error!')
                return
            continue
    if (status =='ok'):time.sleep(5)

    account_info['volume'] += volume_add
    account_info['margin_frozen'] += account_info['margin_available'] * position
    account_info['margin_available'] -= account_info['margin_available'] * position
    account_info['cost_price'] = price
    account_info['stop_price'] = min(priceD1*1.005,price*1.02)
    account_info['direction'] = 'sell'




def SellKoperation(account_info,position,dm):
    volume_reduce = int(account_info['volume'] * position)

    status = 'error'
    retryC = 0
    while (status != 'ok'):
        try:
            response=dm.send_contract_order(symbol='ETH', contract_type='quarter', contract_code='ETH200925',
                                   client_order_id='', price='', volume=volume_reduce, direction='buy',
                                   offset='close', lever_rate=5, order_price_type='optimal_10_ioc')
            status = response['status']
        except:
            retryC += 1
            if (retryC == 20):
                qqEmail('SellK is error!')
                with open("test_account_info.json", "w") as dump_f:
                    json.dump(account_info, dump_f)
                print('connect ws error!')
                return
            continue
    if (status == 'ok'): time.sleep(5)
    account_info['margin_available'] += account_info['margin_frozen'] * position
    account_info['margin_frozen'] -= account_info['margin_frozen'] * position
    account_info['volume'] -= account_info['volume'] * position

    if position == 1:
        account_info['cost_price'] = 0
        account_info['direction'] = 0
        account_info['stop_price'] = 0


def reduceStop_priceK(account_info,closed,highed):
    ma5 = talib.SMA(closed, timeperiod=5)
    if ma5[-1]<ma5[-2]<ma5[-3] and ma5[-6]<ma5[-5]<ma5[-4]<ma5[-3]:
        holdPlace = max(highed[-6:-1])
        if holdPlace < account_info['stop_price'] * 0.99:
            account_info['stop_price'] = holdPlace


def SellK30(closed,ma3,macd):
    position = 0
    if ma3[-1] > ma3[-2] > ma3[-3] and ma3[-6] > ma3[-5] > ma3[-4] > ma3[-3]:
        priceD1 = min(closed[-6:-1])
        macdD1 = min(macd[-6:-1])
        for i in range(8, 100):
            if ma3[-i - 2] > ma3[-i - 1] > ma3[-i] and ma3[-i + 2] > ma3[-i + 1] > ma3[-i]:
                priceD2 = min(closed[-i - 3:-i + 2])
                macdD2 = min(macd[-i - 3:-i + 2])
                if macdD2<macdD1 and priceD2>priceD1:
                    return 1
    return position

def StopK1(account_info,price):
    if price>account_info['stop_price']:
        return True
    return False



def BuyD30(closed,lowed,rsi,ma60):
    position = 0
    priceD1 = 0
    priceD2 = 0
    ma5 = talib.SMA(lowed, timeperiod=5)
    if closed[-1]>ma60[-1]:
        return [0,0,0]
    if ma5[-1] > ma5[-2] > ma5[-3] and ma5[-7] > ma5[-6] > ma5[-5] > ma5[-4] > ma5[-3]:
        priceD1 = min(closed[-6:-1])
        for i in range(10, 100):
            if closed[-i]>ma60[-i]:
                return [0,0,0]
            if ma5[-i - 4] > ma5[-i - 3] >ma5[-i - 2] > ma5[-i - 1] > ma5[-i] and ma5[-i + 3] > ma5[-i + 2] > ma5[-i + 1] > ma5[-i]:
                priceD2 = min(closed[-i - 3:-i + 2])
                rsiD2 = min(rsi[-i - 3:-i + 2])
                if rsiD2<30 and priceD1>priceD2:
                    position =0.5
                break
    return [position,priceD1,priceD2]


def BuyDoperation(account_info,dm,last_price,contract_size,position,priceD1,priceD2):

    volume_add = int(account_info['margin_available'] * last_price * 5 * position / contract_size)
    status = 'error'
    retryC = 0
    while (status != 'ok'):
        try:
            response=dm.send_contract_order(symbol='ETH', contract_type='quarter', contract_code='ETH200925',
                                   client_order_id='', price='', volume=volume_add, direction='buy',
                                   offset='open', lever_rate=5, order_price_type='optimal_10_ioc')
            status = response['status']
        except:
            retryC += 1
            if (retryC == 20):
                qqEmail('BuyD is error!')
                with open("test_account_info.json", "w") as dump_f:
                    json.dump(account_info, dump_f)
                print('connect ws error!')
                return
            continue
    if (status == 'ok'): time.sleep(5)

    account_info['volume'] += volume_add
    account_info['margin_frozen'] += account_info['margin_available'] * position
    account_info['margin_available'] -= account_info['margin_available'] * position
    if account_info['first_buy']==0:
        account_info['cost_price'] = last_price* 0.98
        account_info['stop_price'] = max(priceD2, priceD1* 0.99)
        account_info['direction'] = 'buy'
        account_info['first_buy'] = 1


def SellDoperation(account_info,position,dm):
    volume_reduce = int(account_info['volume'] * position)

    status = 'error'
    retryC = 0
    while (status != 'ok'):
        try:
            response=dm.send_contract_order(symbol='ETH', contract_type='quarter', contract_code='ETH200925',
                                   client_order_id='', price='', volume=volume_reduce, direction='sell',
                                   offset='close', lever_rate=5, order_price_type='optimal_10_ioc')
            status = response['status']
        except:
            retryC += 1
            if (retryC == 20):
                qqEmail('SellD is error!')
                with open("test_account_info.json", "w") as dump_f:
                    json.dump(account_info, dump_f)
                print('connect ws error!')
                return
            continue
    if (status == 'ok'): time.sleep(5)

    account_info['margin_available'] += account_info['margin_frozen'] * position
    account_info['margin_frozen'] -= account_info['margin_frozen'] * position
    account_info['volume'] -= account_info['volume'] * position
    if position == 1:
        account_info['cost_price'] = 0
        account_info['stop_price'] = 0
        account_info['direction'] = 0
        account_info['first_buy'] = 0



def addStop_priceD(account_info,closed,lowed):
    ma5 = talib.SMA(closed, timeperiod=5)
    if ma5[-1]>ma5[-2]>ma5[-3] and ma5[-6]>ma5[-5]>ma5[-4]>ma5[-3]:
        holdPlace = min(lowed[-6:-1])
        if account_info['stop_price']==0 or holdPlace > account_info['stop_price'] * 1.02:
            account_info['stop_price'] = holdPlace



def addCost_priceD(account_info, closed, lowed):
    position = 0
    ma5 = talib.SMA(closed, timeperiod=5)
    if ma5[-1] > ma5[-2] > ma5[-3] and  ma5[-5] > ma5[-4] > ma5[-3]:
        holdPlace = min(lowed[-6:-1])
        if holdPlace > account_info['cost_price'] * 1.03 and account_info['first_buy'] == 1:
            position = 0.3
            account_info['cost_price'] = account_info['cost_price'] * 1.03
            account_info['first_buy'] = 2
    return position



def SellD30(closed,ma3,ma60,rsi,macd,adx,account_info):
    position = 0

    if ma3[-1]<ma3[-2] and max(rsi[-3:])>80 and max(rsi[-3:])>rsi[-1]:
        position = max(position,0.5)

    if ma3[-1]<ma60[-1] and ma3[-2]>=ma60[-2]:
        position = max(position,1)


    if ma3[-1] < ma3[-2] < ma3[-3] and ma3[-5] < ma3[-4] < ma3[-3]:
        priceD1 = max(closed[-6:-1])
        macdD1 = max(macd[-6:-1])
        adxD1 = max(adx[-6:-1])
        if adxD1 > 30 and macdD1 > 1:
            for i in range(10, 200):
                if ma3[-i - 2] < ma3[-i - 1] < ma3[-i] and ma3[-i + 2] < ma3[-i + 1] < ma3[-i]:
                    priceD2 = max(closed[-i - 3:-i + 2])
                    macdD2 = max(macd[-i - 3:-i + 2])
                    adxD2 = max(adx[-i - 3:-i + 2])
                    if macdD2 > macdD1 and priceD2 < priceD1 and adxD2>adxD1:
                        position = max(position,1)
                        break

    if closed[-1]<account_info['stop_price']:
        position = max(position, 0.5)
        account_info['stop_price'] = 0


    return position


def StopD1(account_info,price):
    if price<=account_info['cost_price']:
        return True
    return False

with open("test_account_info.json", 'r') as load_f:
    account_info = json.load(load_f)

# account_info = {'margin_available':0,'margin_frozen':0,'volume':0,'cost_price':0,'stop_price':0,'direction':0,'firstBuy':0}


URL = 'https://api.btcgateway.pro'
ACCESS_KEY = ''
SECRET_KEY = ''
count = 0
retryCount =0

id_30 =0

while (1):
    try:
        dm = HuobiDM(URL, ACCESS_KEY, SECRET_KEY)
        kline_30min = (dm.get_contract_kline(symbol='ETH_CQ', period='30min',size=300))['data']

        contract_info = dm.get_contract_info(symbol="ETH", contract_type="quarter")['data']
        contract_size = contract_info[0]['contract_size']
        contract_account_info = dm.get_contract_account_info("ETH")['data']
        account_info['margin_available'] = contract_account_info[0]['margin_available']
        account_info['margin_frozen'] = contract_account_info[0]['margin_position']
        contract_position_info  = dm.get_contract_position_info("ETH")['data']
        if contract_position_info==[]:
            account_info['volume'] = 0
            account_info['direction']=0
            last_price =kline_30min[-1]['close']
        else:
            account_info['volume'] = contract_position_info[0]['available']
            account_info['direction'] = contract_position_info[0]['direction']
            last_price = contract_position_info[0]['last_price']


    except:
        retryCount += 1
        if(retryCount == 20):
            qqEmail('info_get is error!')
            with open("test_account_info.json", "w") as dump_f:
                json.dump(account_info, dump_f)
            print('connect ws error!')
            break
        continue

    retryCount=0


    if account_info['direction'] == 'buy' and StopD1(account_info, last_price):
        SellDoperation(account_info, 1, dm)


    if account_info['direction'] == 'sell' and StopK1(account_info, last_price):
        SellKoperation(account_info, 1, dm)



    kline_30 = (pd.DataFrame.from_dict(kline_30min))[['id', 'close', 'high', 'low', 'open', 'amount']]
    id = kline_30['id'].values
    id = (id[-1] / 1800)
    if id >id_30:
        id_30 = id

        closed = kline_30['close'].values
        closed = closed[:-1]
        opened = kline_30['open'].values
        opened = opened[:-1]
        highed = kline_30['high'].values
        highed = highed[:-1]
        lowed = kline_30['low'].values
        lowed = lowed[:-1]

        ma3 = talib.SMA(closed, timeperiod=3)
        ma60 = talib.SMA(closed, timeperiod=60)
        rsi = talib.RSI(closed, timeperiod=14)
        macd, signal, hist = talib.MACD(closed, fastperiod=12, slowperiod=26, signalperiod=9)
        adx = talib.ADX(highed, lowed, closed, timeperiod=12)

        if account_info['direction'] == 'buy':
            addStop_priceD(account_info, closed, lowed)
            positionBuyD = addCost_priceD(account_info, closed, lowed)
            if positionBuyD > 0:
                BuyDoperation(account_info,dm,last_price,contract_size, positionBuyD, 0, 0)
            positionSellD = SellD30(closed, lowed, ma3, ma60, rsi, macd, adx, account_info)
            if positionSellD > 0:
                SellDoperation(account_info, positionSellD,dm)


        if account_info['direction'] == 'sell':
            reduceStop_priceK(account_info, closed, highed)
            positionSellK = SellK30(closed, ma3, macd)
            if positionSellK > 0:
                SellKoperation(account_info, positionSellK,dm)


        [positionBuyK, priceKD] = BuyK30(closed, ma3, rsi, macd, adx)
        if positionBuyK > 0:
            if account_info['direction'] == 'buy':
                SellDoperation(account_info, 1,dm)
            BuyKoperation(account_info,dm,last_price,contract_size, positionBuyK, priceKD)

        [positionBuyD, priceD1, priceD2] = BuyD30(closed, lowed, rsi, ma60)
        if positionBuyD > 0:
            if account_info['direction'] == 'sell':
                SellKoperation(account_info, 1,dm)
            BuyDoperation(account_info,dm,last_price,contract_size, positionBuyD, priceD1, priceD2)



    count +=1

    if(count%300==0):
        print(account_info['margin_available'] + account_info['margin_frozen'])

    time.sleep(30)
