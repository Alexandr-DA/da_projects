#!/usr/bin/python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

from datetime import datetime

import pandas as pd

# задаём данные для отрисовки
from sqlalchemy import create_engine

# Передадим ключи и подключимся к базе
db_config = {'user': 'my_user2',
             'pwd': 'my_user_password',
             'host': 'localhost',
             'port': 5432,
             'db': 'zen'}
engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                            db_config['pwd'],
                                                            db_config['host'],
                                                            db_config['port'],
                                                            db_config['db']))


#print('Формируем запрос')

query =     '''
                  SELECT * FROM dash_engagement
            '''
#print('Создаем датасет agg_engagement')
agg_engagement = pd.io.sql.read_sql(query, con = engine)


#print('Формируем запрос')
query =     '''
                  SELECT * FROM dash_visits
            '''
#print('Создаем датасет agg_visits')
agg_visits = pd.io.sql.read_sql(query, con = engine)


# задаём лейаут
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, compress=False)
app.layout = html.Div(children=[  

    # формируем html. Первое - Заголовок
    html.H1(children = 'Дашборд Дзен'),

    # Добавим текст
    html.Label('На данном Дашборде представлены 3 графика. Есть возможность отфильтровать данные по датам, по возрастным группам, по темам карточек. Обратите внимание, что столбчатая диаграмма учитывает лишь фильтрацию по датам'),
    
    html.Br(),

    # Добавим интерактивную часть - 3 фильтра
    html.Div([


            html.Div([
             
                  dcc.DatePickerRange(
                        style = {'height': '4vw'},
                        start_date = agg_engagement['dt'].dt.date.min(),
                        end_date = datetime(2020,12,31).strftime('%Y-%m-%d'),
                        display_format = 'YYYY-MM-DD',
                        id = 'dt_selector',       
                        ),
                  
            html.Br(),

                  dcc.Dropdown(
                        id = 'age_dropdown',
                        options = [{'label': x, 'value': x} for x in agg_visits['age_segment'].unique()],
                        value = agg_visits['age_segment'].unique(),
                        multi = True
                  ),
            ], className = 'six columns'),

            html.Div([
                  dcc.Dropdown(
                        id = 'item_topic_dropdown',
                        options = [{'label': x, 'value': x} for x in agg_visits['item_topic'].unique()],
                        value = agg_visits['item_topic'].unique(),
                        multi = True            
                  ),
            ], className = 'six columns'),

    ], className = 'row'),

    # Добавляем графики
    html.Div([
        
        html.Div([

            
            html.Label('График истории событий по темам карточек. Все типы событий, абослютные значения'), 
            
            dcc.Graph(
                style = {'height': '50vw'},
                id = 'history_absolute_visits'
            ),  
        ], className = 'six columns'),            

            html.Div([

                  html.Label('График разбитий событий по темам источников. Все типы событий, относительные значения'),    
        
                  dcc.Graph(
                  style = {'height': '25vw'},
                  id = 'pie_visits'
                  ),  
            ], className = 'six columns'),

            html.Div([

                  html.Label('График средней глубины взаимодействия (без разбивки на темы карточек или возрастные категории)'),    
        
                  dcc.Graph(
                  style = {'height': '25vw'},
                  id = 'engagement_graph'
                  ),  
            ], className = 'six columns')            
        
    ], className = 'row'),
])
# описываем логику дашборда
@app.callback(
    [Output('history_absolute_visits', 'figure'),
     Output('pie_visits', 'figure'),
     Output('engagement_graph', 'figure'),
    ],
    [Input('dt_selector', 'start_date'),
     Input('dt_selector', 'end_date'),
     Input('age_dropdown', 'value'),
     Input('item_topic_dropdown', 'value'),
    ])

# функция исполнения
def update_figures(start_date, end_date, age, topic):
      #фильтр по датам
      filtered_engagement = agg_engagement.query('dt >= @start_date and dt <= @end_date')
      filtered_visits = agg_visits.query('dt >= @start_date and dt <= @end_date')
      #фильтр по возрасту
      filtered_engagement = filtered_engagement.query('age_segment.isin(@age)')
      filtered_visits = filtered_visits.query('age_segment.isin(@age)')
      #фильтр по темам
      filtered_engagement = filtered_engagement.query('item_topic.isin(@topic)')
      filtered_visits = filtered_visits.query('item_topic.isin(@topic)')
      # группировка для построения графика
      agg_visits_grouped = filtered_visits.groupby(['item_topic','dt']).agg({'visits':'sum'}).reset_index()
      filtered_engagement = filtered_engagement.groupby('event').agg({'unique_users':'sum'}).reset_index().sort_values(by = 'unique_users', ascending = False)
      filtered_engagement = filtered_engagement.replace('show', '1. show')
      filtered_engagement = filtered_engagement.replace('click', '2. click')
      filtered_engagement = filtered_engagement.replace('view', '3. view')
      # построим график с накоплением
      history_absolute_visits = []
      for item_topic in agg_visits_grouped['item_topic'].unique():
            history_absolute_visits += [go.Scatter(y = agg_visits_grouped.query('item_topic == @item_topic')['visits'],
                                                   x = agg_visits_grouped.query('item_topic == @item_topic')['dt'],
                                                   mode = 'lines',
                                                   stackgroup = 'one',
                                                   name = item_topic)]

      # построим график пирожочек
      pie_visits = [go.Pie(labels = filtered_visits['source_topic'],
                           values = filtered_visits['visits'],
                           name = 'source_topic')]

      # построим график бар
      engagement_graph = [go.Bar(x = filtered_engagement['event'],
                                 y = filtered_engagement['unique_users'],
                                 name = 'engagement_graph')]

      # вернем что у нас получилось
      return (
            {
                'data': history_absolute_visits, # напишите код
                'layout': go.Layout(xaxis = {'title': 'Дата-Время'},
                                    yaxis = {'title': 'Визиты'})
             },
             {
                'data': pie_visits,
                'layout': go.Layout()
             },
             {
                'data': engagement_graph, # напишите код
                'layout': go.Layout(xaxis = {'title': 'Тип события'},
                                    yaxis = {'title': 'Кол-во событий'})
             },
             )
# поехали
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=3000)