import gspread
from oauth2client.service_account import ServiceAccountCredentials
from keys import GS_COUNTER_URL
import datetime


def next_available_row(sheet):
    str_list = list(filter(None, sheet.col_values(1)))
    return str(len(str_list) + 1)


url = GS_COUNTER_URL

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']


def append_row(content):
    credentials = ServiceAccountCredentials.from_json_keyfile_name("Qbot link-5a85108c008a.json", scope)

    gc = gspread.authorize(credentials)
    ws = gc.open_by_url(url).sheet1
    next_row = next_available_row(ws)
    ws.update_acell("A{}".format(next_row), content[0])
    ws.update_acell("B{}".format(next_row), content[1])
