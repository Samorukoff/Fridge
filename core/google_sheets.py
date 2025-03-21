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

feed_sheet = workbook.worksheet("feed_sheet")
cart_sheet = workbook.worksheet("cart_sheet")
