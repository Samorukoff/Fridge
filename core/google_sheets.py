import os
from dotenv import load_dotenv

import gspread
from google.oauth2.service_account import Credentials

#Загружаем переменные виртуального окружения
load_dotenv()

#Получаем API
creds = Credentials.from_service_account_file(os.getenv("CREDENTIALS", "credentials.json"),
                                    scopes=["https://www.googleapis.com/auth/spreadsheets"])
        
client = gspread.authorize(creds)
workbook_id = "1KopmjRrKL5m9KdLkdKx_yqegZccUftbWTn9Bg-I_c3k"
workbook = client.open_by_key(workbook_id)

#Таблица продавцов
seller_sheet = workbook.worksheet("seller_sheet")
#Таблица покупателей
customer_sheet = workbook.worksheet("customer_sheet")
#Таблица ленты товаров
feed_sheet = workbook.worksheet("feed_sheet")
#Таблица корзины
cart_sheet = workbook.worksheet("cart_sheet")
#Таблица заявок
request_sheet = workbook.worksheet("request_sheet")
#Таблица токенов для ссылок
link_sheet = workbook.worksheet("link_sheet")

