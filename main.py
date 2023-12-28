import requests
import json
from bs4 import BeautifulSoup
import time 
import sqlite3

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
           "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8", "Accept": "application/json, text/javascript, */*; q=0.01", "X-Requested-With":"XMLHttpRequest"}

def telebot_channel(item):
    TOKEN = "token"  # Замените на ваш токен бота
    channel_id = 'id' # Замените на ваш channel_id or chat_id бота

    message = f'<b>📱Название</b>: {item["Название"]}\n<b>💰Цена</b>: <strong>{item["Цена"]}</strong>\n<b>🌟Состояние</b>: {item["Status"]}\n<b>ℹ️Информация</b>: \n{item["Информация"]}\n<b>📍Локация</b>: {item["Локация"]}\n<b>🔗Ссылка</b>:\n{item["Ссылка"]}'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        'chat_id': channel_id,
        'text': message,
        'parse_mode': 'HTML'  
    }
    response = requests.post(url, data=params)
    # print(response.text)

def create_database():
    # Создаем подключение к базе данных (файл my_database.db будет создан)
    db = sqlite3.connect('mydb.db')
    sql = db.cursor()
    
    # Создаем таблицу, если она не существует
    sql.execute('''CREATE TABLE IF NOT EXISTS Users (
        id TEXT
    )''')
    db.commit()
    sql.execute("SELECT COUNT(*) id FROM Users")
    print(sql.fetchall())


def informations(link):
    info_get = requests.get('https://www.olx.uz'+link, headers=headers)
    sop = BeautifulSoup(info_get.text, 'lxml')
    full_info = sop.find('div', class_="css-1t507yq er34gjf0").text.strip() # Получаем информацию о товаре
    return full_info

def main(db,sql):
    url = "https://www.olx.uz/elektronika/telefony/tashkent/q-Iphone/?currency=UZS&search%5Bphotos%5D=1&search%5Border%5D=created_at:desc&search%5Bfilter_enum_mobile_phone_manufacturer%5D%5B0%5D=2065"
    r = requests.get(url, headers= headers)
    soup = BeautifulSoup(r.text, 'lxml')
    all_item = soup.find_all('div', class_="css-1sw7q4x")
    for i in all_item:
        try:
            top = i.find('div', class_="css-3xiokn")
            id = i.get('id')
            if top is not None and top.get_text(strip=True): # проверка на "топ" если есть то пропускаем и не показываем его. Так как там старые лоты
                continue
            else:
                link = i.find('a', class_='css-rc5s2u').get('href').strip()
                name = i.find('h6', class_='css-16v5mdi er34gjf0').text.strip()
                price = i.find('p', class_='css-10b0gli er34gjf0').text.strip().replace('Договорная','')
                status = i.find('span', class_='css-3lkihg').get('title')
                
                loc = i.find('p', class_='css-veheph er34gjf0').text.strip()
                
                # print(status)
                sql.execute("SELECT id FROM Users WHERE id=?", (id,))
                if sql.fetchone() is None:
                    sql.execute("INSERT INTO Users VALUES (?)", (id,))
                    db.commit()
                    INFO = informations(link=link)
                    items = {
                        'ID':id,
                        'Название': name,
                        'Цена': price,
                        'Status':status,
                        'Локация': loc,
                        'Информация': INFO.replace('\n', ''),
                        'Ссылка':'https://www.olx.uz' + link }

                    # print(items)
                    telebot_channel(item=items)
                    time.sleep(1)
        except Exception as e:
            # print(f"Ошибка при обработке элемента: {e}")
            pass

if __name__ == '__main__':
    db = sqlite3.connect('mydb.db')
    sql = db.cursor()
    create_database()
    main(db,sql)
    while True:
        try:
            time.sleep(30)
            main(db,sql)
        except Exception as e:
            print(f"Ошибка при обработке элемента: {e}")
            pass
