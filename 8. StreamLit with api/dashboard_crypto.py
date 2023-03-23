# импорты
import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px

# функции
# функция получения списка ассетов
def get_assets_list(assets_link):
    r = requests.get(assets_link)
    if r.status_code == 200:
        assets_list = [x['id'] for x in r.json()['data']]
        assets_list = tuple(assets_list)
        return assets_list
    else:
        print('Попробуйте позже')

# функция получения курсов
def get_courses(courses_link, asset = 'bitcoin', interval = 'd1', dt_start = datetime.date.today() - datetime.timedelta(days=10) , dt_end = datetime.date.today() ):
    dt_start = datetime.datetime.combine(dt_start, datetime.datetime.min.time())
    dt_start = round(datetime.datetime.timestamp(dt_start)*1000)
    dt_end = datetime.datetime.combine(dt_end, datetime.datetime.max.time())
    dt_end = round(datetime.datetime.timestamp(dt_end)*1000)
    courses_link = courses_link.format(asset = asset, interval = interval, dt_start = dt_start, dt_end = dt_end)
    r = requests.get(courses_link)
    return r.json()

# функция преобразовани данных
def transform_resp(resp):
    data = pd.DataFrame(resp['data'])
    data['priceUsd'] = data['priceUsd'].astype(float)
    return data

# функция для построения графика
def get_plot(data):
    fig = px.bar(data, x="date", y="priceUsd")
    fig.update_layout(
    xaxis_title="TIME",
    yaxis_title="PRICE",
    )
    return fig

#функция получения, преобразования и отрисовки 
def etl_data(dt_start, dt_end, asset, assets_link, courses_link, ):
    r = get_courses(courses_link, asset = asset, dt_start = dt_start, dt_end = dt_end)
    data = transform_resp(r)
    fig = get_plot(data)
    return fig

# переменные
assets_link = 'https://api.coincap.io/v2/assets'
courses_link = f'https://api.coincap.io/v2/assets/{{asset}}/history?interval={{interval}}&start={{dt_start}}&end={{dt_end}}'

# сохраним список полученных ассетов в виде кортеж
assets = get_assets_list(assets_link)

# рисуем страничку
with st.sidebar:
    
    dt_start = st.date_input(
    "Date from",
        datetime.datetime(2023, 3, 1))

    dt_end = st.date_input(
        "Date to",
        datetime.datetime(2023, 3, 31))

    option = st.selectbox(
        'Select an asset',
    assets)

# сделаем и выведем график
fig = etl_data(dt_start = dt_start, dt_end = dt_end, asset = option, assets_link=assets_link, courses_link=courses_link)

st.plotly_chart(fig, use_container_width=True)
