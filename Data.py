try:
    import mysql.connector  # using mysql connector should install it first(python 2.7/3.3/3.4)
except ImportError:
    print('Please Install MySQL Connector(Python) First.')
    raise SystemExit()
try:
    from yahoo_finance import Share
except ImportError:
    import pip

    pip.main(['install', 'yahoo_finance'])
    from yahoo_finance import Share

try:
    import pandas as pd
    from pandas import DataFrame
except ImportError:
    import pip

    pip.main(['install', 'pandas'])
    import pandas as pd

try:
    import pandas_datareader as pdr
    from pandas_datareader import data, wb
except ImportError:
    import pip

    pip.main(['install', 'pandas_datareader'])
    import pandas_datareader as pdr
    from pandas_datareader import data, wb

try:
    from sqlalchemy import create_engine
except ImportError:
    import pip

    pip.main(['install', 'sqlalchemy'])
    from sqlalchemy import create_engine

try:
    from datetime import *
except ImportError:
    import pip

    pip.main(['install', 'datetime'])
    from datetime import *

import time

PassWord = 'fflovexx123'
User = 'root'
Host = '127.0.0.1'
Port = '3306'
Database = 'SEProject'

try:
    cnx = mysql.connector.connect(user=User, password=PassWord, host=Host)  # using configuration of sever
except mysql.connector.Error:
    print('Can Not Connect With Database Sever.')
    raise SystemExit()

cursor = cnx.cursor()

Stocks = ['AAPL', 'GOOGL', 'NVDA', 'YHOO', 'AMZN','MSFT','BAC', 'NKE', 'NFLX', 'FB']

# using mysql to create real time data
create_RealtimeData = '''CREATE TABLE IF NOT EXISTS realtimedata               
                       (
                          `time` DATETIME,
                          `sym` CHAR(20),
                          `price` REAL,
                          `volume` INTEGER,
                          PRIMARY KEY(sym,time)
                         );'''

# using mysql to creat historical data
create_HistoricalData = '''CREATE TABLE IF NOT EXISTS historicaldata
                       (
                        `date` DATE,
                        `open` REAL,
                        `high` REAL,
                        `low` REAL,
                        `close` REAL,
                        `volume` INTEGER,
                        `adj close` INTEGER,
                        `sym` CHAR(20),
                        PRIMARY KEY(sym,date)
                        );'''
cursor.execute('CREATE DATABASE IF NOT EXISTS ' + Database)  # creat database if not exists
cursor.execute('USE ' + Database)  # select the database
cursor.execute(create_RealtimeData)  # create table
cursor.execute(create_HistoricalData)  # create table

# end and start dates for the historical quotes
end = date.today()
start = end - timedelta(days=365)  # this calculates exactly a year back from today

# stroing stock packet (json) for each stock
apple = Share('AAPL')
google = Share('GOOGL')
nvidia = Share('NVDA')
yahoo = Share('YHOO')
amazon = Share('AMZN')
microsoft = Share('MSFT')
BoA = Share('BAC')
nike = Share('NKE')
netflix = Share('NFLX')
FB= Share('FB')


print('Reading Data and Putting them in Database.Quit with Ctrl+C')
try:
    # using yahoo finance api to save data into a pandas dataframe
    df_apple = pdr.get_data_yahoo('AAPL', start, end)
    df_google = pdr.get_data_yahoo('GOOGL', start, end)
    df_nvidia = pdr.get_data_yahoo('NVDA', start, end)
    df_yahoo = pdr.get_data_yahoo('YHOO', start, end)
    df_amazon = pdr.get_data_yahoo('AMZN', start, end)
    df_microsoft = pdr.get_data_yahoo('MSFT', start, end)
    df_BoA = pdr.get_data_yahoo('BAC', start, end)
    df_nike = pdr.get_data_yahoo('NKE', start, end)
    df_netflix = pdr.get_data_yahoo('NFLX', start, end)
    df_FB = pdr.get_data_yahoo('FB', start, end)



    # function to get a row for stock symbols to insert into the table
    def get_series(sym, df_sym):
        x = []
        for i in range(len(df_sym)):
            x.append(sym)
        return x


    # returnrs cyrrent price and volume quotes for a given symbol in a dataframe
    def get_price_RT(sym):
        Time_now = str(datetime.fromtimestamp(time.time()))
        t = pd.DataFrame(
            {'time': Time_now, 'sym': sym, 'price': [Share(sym).get_price()], 'volume': [Share(sym).get_volume()]},
            index=[Time_now])
        return t


    # adds dataframe into the csv each time the function is called
    def add_to_csv_RT(documents, df):
        with open(documents, 'a') as f:
            df.to_csv(f, columns=['time', 'sym', 'price', 'volume'], header=False, index=False)


    a = get_series('AAPL', df_apple)
    b = get_series('GOOGL', df_google)
    c = get_series('NVDA', df_nvidia)
    d = get_series('YHOO', df_yahoo)
    e = get_series('AMZN', df_amazon)
    f = get_series('MSFT',df_microsoft)
    g = get_series('BAC',df_BoA)
    h = get_series('NKE',df_nike)
    i = get_series('NFLX',df_netflix)
    j = get_series('FB',df_FB)

    df_apple['sym'] = a
    df_google['sym'] = b
    df_nvidia['sym'] = c
    df_yahoo['sym'] = d
    df_amazon['sym'] = e
    df_microsoft['sym']= f
    df_BoA['sym']= g
    df_nike['sym']= h
    df_netflix['sym']= i
    df_FB['sym']= j


    engine = create_engine('mysql+mysqlconnector://' + User + ':' + PassWord + '@' + Host + ':' + Port + '/' + Database,
                           echo=False)
    frames = [df_apple, df_google, df_nvidia, df_yahoo, df_amazon, df_microsoft, df_BoA, df_nike, df_netflix, df_FB]
    for i in range(0, 10):
        result = frames[i]
        result.to_csv(Stocks[i] + '_histdata.csv')
        if i == 0:
            result.to_sql(name='historicaldata', con=engine, if_exists='replace')
        else:
            result.to_sql(name='historicaldata', con=engine, if_exists='append')

            # ============= code for real-time quotes ===   =====
    j = 0
    while True:
        if j == 0:
            list1 = []
            f = pd.DataFrame({'time': list1, 'sym': list1, 'price': list1, 'volume': list1})
            f.set_index('time', inplace=True)
            for cnt in range(0, 10):
                f.to_csv(Stocks[cnt] + '_rtdata.csv', columns=['time', 'sym', 'price', 'volume'], index=False)
            j = 1

        else:
            if j == 1:
                j = 2
            for i in Stocks:
                p = get_price_RT(i)
                add_to_csv_RT(documents=i + '_rtdata.csv', df=p)
                if j == 2 and i == Stocks[0]:
                    p.to_sql(name='realtimedata', con=engine, if_exists='replace', index=False)
                else:
                    p.to_sql(name='realtimedata', con=engine, if_exists='append', index=False)
        time.sleep(60)
        google.refresh()
        nvidia.refresh()
        yahoo.refresh()
        amazon.refresh()
        apple.refresh()
        microsoft.refresh()
        BoA.refresh()
        nike.refresh()
        netflix.refresh()
        FB.refresh()









except KeyboardInterrupt:
    print('User Asked to Quit')
    raise SystemExit()
finally:
    cnx.close()  # close the connector
