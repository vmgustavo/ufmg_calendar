from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd
import re

import os

# SET CONSTANTS
feriado_only = True

path = os.path.dirname(os.path.abspath('calendar_read.py'))

ufmg_calendar_link = 'https://ufmg.br/a-universidade/calendario-academico'
year = '2019'
all_month_link_list = [ufmg_calendar_link + '?ano=%s&mes=%s' % (year, month) for month in range(1, 13)]
driver = webdriver.Chrome(str(path) + '\\chromedriver.exe')

event_info_list = []
for month_link in all_month_link_list:
    # month_link = all_month_link_list[0]
    try:
        driver.get(month_link)
        vis_mode = '//*[@id="conteudo"]/div[2]/div[2]/div/a[2]/span[1]'
        WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.XPATH, vis_mode)))
        driver.find_element_by_xpath(vis_mode).click()
    finally:
        print('SEARCHING FOR ELEMENTS UNDER\n%s' % month_link)
        all_elements = driver.find_elements_by_xpath('//*[@class]')

        event_info_list.extend([(elem.get_attribute('data-info-init-date'),
                                 elem.get_attribute('data-info-end-date'),
                                 elem.get_attribute('data-info-location'),
                                 elem.get_attribute('data-info-title'))
                                for elem in all_elements if 'calendar__description' in elem.get_attribute('class')])

# CONVERT DATETIME STRING TO BETTER FORMAT
df = pd.DataFrame(data=event_info_list, columns=['init-date', 'end-date', 'loc', 'title'])
df['init-date'] = df['init-date'].apply(
    lambda x: re.sub(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z', r'\g<3>/\g<2>/\g<1>', x))
df['end-date'] = df['end-date'].apply(
    lambda x: re.sub(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z', r'\g<3>/\g<2>/\g<1>', x))

# FIND IF Feriado OR Recesso
df = df.join(pd.DataFrame(data=[bool(re.match(r'(\bFeriado\b|\bRecesso\b)', elem)) for elem in df['title']],
                          columns=['Feriado/Recesso']))

# FILTER LOCATION Belo Horizonte
df = df[df['loc'].str.contains('Belo Horizonte')].drop('loc', axis=1)

# DROP DUPLICATES
df = df.drop_duplicates()

# DROP IF NOT Feriado/Recesso
if feriado_only:
    df = df[df['Feriado/Recesso']]

# GOOGLE CALENDAR FORMATTING
# ['Subject', 'Start Date', 'End Date', 'All Day Event', 'Description']
subject_list = []
for elem in df['Feriado/Recesso']:
    if elem:
        subject_list.append('Feriado/Recesso')
    else:
        subject_list.append('Evento (Ler Descrição)')

gcal = pd.DataFrame(
    data=[(subject_list[idx], df['init-date'].iloc[idx], df['end-date'].iloc[idx], True, df['title'].iloc[idx]) for idx
          in range(len(df))],
    columns=['Subject', 'Start Date', 'End Date', 'All Day Event', 'Description'])

# SAVE CSV FILE
gcal.to_csv('ufmg_calendar.csv')
