from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
import os


def format_date(s):
    return datetime.strptime(s, '%Y%m%dT%H%M%SZ').strftime('%d/%m/%Y')


def dump_csv(dframe, filename):
    # GOOGLE CALENDAR FORMATTING
    # ['Subject', 'Start Date', 'End Date', 'All Day Event', 'Description']
    subject_list = list()
    for elem in dframe['Feriado/Recesso']:
        if elem:
            subject_list.append('Feriado/Recesso')
        else:
            subject_list.append('Evento (Ler Descrição)')

    gcal = pd.DataFrame(
        data=[(subject_list[idx], dframe['init-date'].iloc[idx],
               dframe['end-date'].iloc[idx], True, dframe['title'].iloc[idx])
              for idx in range(len(dframe))],
        columns=['Subject', 'Start Date', 'End Date', 'All Day Event', 'Description'])

    # SAVE CSV FILE
    gcal.to_csv(filename)
    print(f'Dump file to {os.path.abspath(filename)}')


def main():
    ufmg_calendar_link = 'https://ufmg.br/a-universidade/calendario-academico'
    year = datetime.now().year
    all_month_link_list = [ufmg_calendar_link + '?ano=%s&mes=%s' % (year, month) for month in range(1, 13)]

    event_info = list()
    for month_link in all_month_link_list:
        print(month_link)
        gotpage = False
        page = None
        while not gotpage:
            try:
                page = requests.get(month_link)
                gotpage = True
            except (ConnectionError, requests.exceptions.ConnectionError) as e:
                stime = 1
                print(e.__class__.__name__ + f' | Trying again in {stime}s')
                sleep(stime)
                gotpage = False
        soup = BeautifulSoup(page.text, 'html.parser')
        events = soup.find_all(class_='calendar__description')
        n_events = len(events)
        print(f'Found {n_events} events')
        if not n_events > 0:
            continue
        event_info.extend([(elem.get('data-info-init-date'), elem.get('data-info-end-date'),
                            elem.get('data-info-location'), elem.get('data-info-title'))
                           for elem in events])

    # CONVERT DATETIME STRING TO BETTER FORMAT
    df = pd.DataFrame(data=event_info, columns=['init-date', 'end-date', 'loc', 'title'])
    df['init-date'] = df['init-date'].apply(format_date)
    df['end-date'] = df['end-date'].apply(format_date)

    # FIND IF Feriado OR Recesso
    df = df.join(pd.DataFrame(data=[bool(re.match(r'(\bFeriado\b|\bRecesso\b)', elem)) for elem in df['title']],
                              columns=['Feriado/Recesso']))

    # FILTER LOCATION Belo Horizonte
    df = df[df['loc'].str.contains('Belo Horizonte')].drop('loc', axis=1)

    # DROP DUPLICATES
    df = df.drop_duplicates()

    # DROP IF NOT Feriado/Recesso
    df_feariado = df[df['Feriado/Recesso']]
    df_evento = df[~df['Feriado/Recesso']]

    dump_csv(df_evento, filename='eventos.csv')
    dump_csv(df_feariado, filename='feriados.csv')


if __name__ == '__main__':
    main()
