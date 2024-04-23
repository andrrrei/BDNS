# __________ #
import pygsheets
import pandas as pd
import  datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=['https://www.googleapis.com/auth/drive']
    )
drive_service = build("drive", "v3", credentials)

import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
CREDENTIALS_FILE = 'credentials.json'  # имя файла с закрытым ключом
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
sheets_service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

gc = pygsheets.authorize(service_file = 'credentials.json')

# Считывание ID таблицы ответов на форму
table1 = '1VCBrFI6nnEU-omIzAlIuhqDrY74JusRBQ5EDXlAfnkI'
# Считывание даты, с которой нужно брать данные
date_period_str = input("Введите дату, начиная с которой отсчитывать период: ")
date_period_obj = datetime.datetime.strptime(date_period_str, '%d.%m.%Y')


base = gc.open_by_key(table1)
df_base = base[0]
df = df_base.get_as_df()
# Отсеиваем только нужный период
df['Отметка времени'] = pd.to_datetime(df['Отметка времени'], format = '%d.%m.%Y %H:%M:%S')
df = df.loc[df['Отметка времени'] >= date_period_obj]
df2 = df.loc[df['Выберите причину продления'] == 'Истечение срока действия подверждающих документов']
# Считали данные таблицы в датафрейм, вытаскиваем только нужные нам (продление), сортируем
# Если людей на продление нет, завершаем работу
if df2.empty:
    print("Нет людей на продление в этом периоде")
    exit(1)
df2 = df2.sort_values(['ФИО']).reset_index(drop=True)
new_df = df2['ФИО'].str.split(expand=True)
new_df.columns=['Фамилия','Имя','Отчество']
x, y = new_df.shape
for i in range(0, int(x)):
    new_df.iat[i, 0] = str(new_df.iat[i, 0]) + str(new_df.iat[i, 1])[0] + str(new_df.iat[i, 2])[0]
new_df = new_df['Фамилия']
new_df.rename('Название файла')
df2 = df2.iloc[:,[21, 22]]
final_df = pd.concat([new_df, df2], axis=1)
final_df.rename(columns={'Тип справки': 'Документы'}, inplace=True)
indexes = range(1, len(final_df) + 1)
final_df.insert(loc=0, column='X', value=indexes)
final_df['X'] = final_df['X'].astype(str)

csv_data = final_df.to_csv (r' my_data.csv', index= False)
