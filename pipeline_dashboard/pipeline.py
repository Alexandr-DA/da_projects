#!/usr/bin/python
# -*- coding: utf-8 -*-
# грузим библиотеки
import sys
import getopt
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine


if __name__ == "__main__":

    #input params setup
    unixOptions = "s:e:"  
    gnuOptions = ["start_dt=", "end_dt="] 

    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]    #excluding script name

    try:  
        arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
    except getopt.error as err:  
        # output error, and return with an error code
        print (str(err))
        sys.exit(2)

    start_dt = ''
    end_dt = ''
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-s", "--start_dt"):
            start_dt = currentValue
        elif currentArgument in ("-e", "--end_dt"):
            end_dt = currentValue


    # Передаем параметры подключения
    db_config = {'user': 'my_user2',
                'pwd': 'my_user_password',
                'host': 'localhost',
                'port': 5432,
                'db': 'zen'}


    # Подключаемся к базе
    connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                                         db_config['pwd'],
                                                                           db_config['host'],
                                                                           db_config['port'],
                                                                           db_config['db'])



    engine = create_engine(connection_string)

    # Создаем запрос
    query = ''' SELECT *
                FROM log_raw 
                WHERE
                TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' 
                BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
            '''.format(start_dt, end_dt)
    # Создаем датафрейм
    log_raw = pd.io.sql.read_sql(query, con = engine, index_col = 'event_id')
    log_raw['dt'] = pd.to_datetime(log_raw['ts']/1000, unit='s').dt.round('min')
    #log_raw.to_csv('/tmp/log_raw_data.csv')
        #Делаем дэш по визитам

    agg_visits = log_raw.groupby(['item_topic', 'source_topic', 'age_segment','dt']).agg({'event': 'count'}).reset_index()
    
    # Переименовываем столбцы 

    agg_visits.columns = ['item_topic', 'source_topic','age_segment', 'dt', 'visits']
    agg_visits.to_csv('/tmp/agg_visits.csv')
    # делаем второй деш

    agg_engagement = log_raw.groupby(['dt','item_topic','event','age_segment']
                                                ).agg({'user_id': 'nunique'}).reset_index()

    # Переименовываем столбцы 

    agg_engagement.columns = ['dt','item_topic', 'event', 'age_segment', 'unique_users']
    agg_engagement.to_csv('/tmp/agg_engagement.csv')

# Передача запроса в цикле
    tables = {'dash_visits':agg_visits, 'dash_engagement':agg_engagement}
    for table_name, table_data in tables.items():   

        query = '''
                  DELETE FROM {} WHERE dt::TIMESTAMP
        	BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
                '''.format(table_name, start_dt, end_dt)
        engine.execute(query)

        table_data.to_sql(name = table_name, con = engine, if_exists = 'append', index = False)

    print('Все ок')