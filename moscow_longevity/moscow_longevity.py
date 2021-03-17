import streamlit as st
import numpy as np
import pandas as pd
import os
import re
import copy
import base64

st.title('Московское долголетие')

multiple_files = st.file_uploader(
    "Прикрепите файлы csv",
    accept_multiple_files=True
)
list_event = pd.DataFrame({'Идентификатор конференции': 0,
                           'Тема': '','Время начала': 0,
                           'Время завершения': '',
                           'Электронная почта пользователя': 0,
                           'Продолжительность (минуты)': 0,
                           'Участники': 0,
                           'Unnamed: 7': 0}, index=[0])

db_users = pd.DataFrame({'Имя (настоящее имя)': 0, 
                         'Электронная почта пользователя': 0, 
                         'Время входа': 0,
                         'Время выхода': 0, 
                         'Продолжительность (минуты)': 0, 
                         'Гость': 0, 
                         'id_conference': 0,
                         'topic': 0}, index=[0])


conf_list = []  
for i in multiple_files:
    j = copy.copy(i)
    k = copy.copy(i)
    h = copy.copy(i)
    topic = re.findall(r'G-\d+', pd.read_csv(i, nrows=1).fillna(0)['Тема'][0])[0]
    id_conference = 'conf_' + str(pd.read_csv(j, nrows=1).fillna(0)['Время начала'][0].replace(' ', '_').replace('.', '_').replace(':', '_'))
    conf_list.append(id_conference)
    cur_event = pd.read_csv(k, nrows=1)
    list_event = pd.concat([cur_event, list_event])
    globals()[id_conference] = pd.read_csv(h, skiprows=2).fillna(0)
    globals()[id_conference]['id_conference'] = id_conference
    globals()[id_conference]['topic'] = topic
    

for i in conf_list:
    db_users = pd.concat([db_users, globals()[i]])
db_users = db_users[1:]

def shedule_time(row):
    if row['topic'] == 'G-02024918':
        row['schedule_start'] = str(row['Время входа'])[:10] + ' 10:30:00 AM'
        row['schedule_end'] = str(row['Время входа'])[:10] + ' 11:30:00 AM'
    elif row['topic'] == 'G-02024919':
        row['schedule_start'] = str(row['Время входа'])[:10] + ' 12:00:00 PM'
        row['schedule_end'] = str(row['Время входа'])[:10] + ' 01:00:00 PM'
    elif row['topic'] == 'G-02024921':
        row['schedule_start'] = str(row['Время входа'])[:10] + ' 03:00:00 PM'
        row['schedule_end'] = str(row['Время входа'])[:10] + ' 04:00:00 PM'
    elif row['topic'] == 'G-02024922':
        row['schedule_start'] = str(row['Время входа'])[:10] + ' 04:30:00 PM'
        row['schedule_end'] = str(row['Время входа'])[:10] + ' 05:30:00 PM'
    return row

db_users = db_users.apply(shedule_time, axis = 1)

try:
    db_users['Время входа'] = pd.to_datetime(db_users['Время входа'])#, format='%d.%m.%Y %H:%M:%S %p')
    db_users['Время выхода'] = pd.to_datetime(db_users['Время выхода'])#, format='%d.%m.%Y %H:%M:%S %p')
    db_users['schedule_start'] = pd.to_datetime(db_users['schedule_start'])#, format='%d.%m.%Y %H:%M:%S %p')
    db_users['schedule_end'] = pd.to_datetime(db_users['schedule_end'])#, format='%d.%m.%Y %H:%M:%S %p')
except:
    pass

def real_time(row):
    if row['Время входа'] <=  row['schedule_start']:
        row['real_start'] = row['schedule_start']
    elif row['Время входа'] >=  row['schedule_end']:
        row['real_end'] = row['schedule_end']
    else:
        row['real_start'] = row['Время входа']
    
    if row['Время выхода'] >=  row['schedule_end']:
        row['real_end'] = row['schedule_end']
    elif row['Время выхода'] <=  row['schedule_start']:
        row['real_end'] = row['schedule_start']
    else:
        row['real_end'] = row['Время выхода']
    return row

try:
    db_users = db_users.apply(real_time, axis = 1)
    db_users['real_time'] = db_users['real_end'] - db_users['real_start']
    db_users['real_time_min'] = db_users['real_time']/ np.timedelta64(1, "s")/60
    db_users = db_users.drop_duplicates()
    db_users = db_users.drop_duplicates()#.info()
    db_users['academ_hour'] = db_users['real_time_min'].apply(lambda x: 1 if x >= 45 else 0)
    bad_names = ['ТЦСО', 'ОСКАД']
    for i in bad_names:
        db_users_clear = db_users[~db_users['Имя (настоящее имя)'].str.contains(i)]
    db_users_clear = db_users_clear[db_users_clear['Гость'] == 'Да']
except:
    pass



def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'
if st.button('Скачать сырые данные в CSV'):
    tmp_download_link = download_link(db_users, 'mos_dolg_raw.csv', 'Нажмите, чтобы скачать свой файл!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

if st.button('Скачать очищенные данные в CSV'):
    tmp_download_link = download_link(db_users_clear, 'mos_dolg_clear.csv', 'Нажмите, чтобы скачать свой файл!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)