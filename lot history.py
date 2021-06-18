from selenium import webdriver
from time import sleep
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import time
import xlwt
from selenium.webdriver.common.keys import Keys
from download_ftp import *

pd.set_option('display.max_colwidth', None)

url_top = 'http://cvplblip03/WIP4_5/LotHistory.aspx?LotNum='


def read_lot(excel_path):
    df = pd.read_excel(excel_path, sheet_name=0)
    # print(df)
    lot_all = df["mtlot"]
    lot_list_all = list(set(list(lot_all)))
    # print(lot_all)
    print(lot_list_all)
    return lot_list_all

def launch_the_chrome_driver(url, sleep_time):
    option = webdriver.ChromeOptions()
    # option.add_argument("headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
    driver.get(url)
    sleep(sleep_time)
    driver.maximize_window()
    return driver


def search_lot(driver, lotlists, sleep_time):
    adh_lot = []
    for lot in lotlists:
        if isinstance(lot, str):
            lot_input = driver.find_element_by_name("txtLotNum")
            lot_input.send_keys(Keys.CONTROL+'a')
            lot_input.send_keys(Keys.DELETE)
            lot_input.send_keys(lot)
            # sleep(sleep_time)
            query_btn = driver.find_element_by_name("cmdRefresh")
            query_btn.click()
            # print("1. searching......")
            sleep(sleep_time)
            sh_td_list = driver.find_elements_by_xpath("//*[@id='flexMainHist']/tbody/tr/td[contains(text(), '5005')]")
            if sh_td_list:
                for each_sh_td in sh_td_list:
                    try:
                        handler = each_sh_td.find_element_by_xpath("./../td[contains(text(), 'AD')]")
                        print(handler.text)
                        adh_lot.append([handler.text, lot])
                        break
                        # print(adh_lot)
                    except:
                        # print(adh_lot)
                        continue

    return adh_lot
if __name__ == '__main__':
    lotlist = read_lot("C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal II\\CFL.xlsx")
    driver_top = launch_the_chrome_driver(url_top, 1)

    handler_lot = search_lot(driver=driver_top, lotlists=lotlist, sleep_time=1)
    print(handler_lot)
    wb = xlwt.Workbook()
    ws = wb.add_sheet('ADH')
    i = 0
    for each in handler_lot:
        ws.write(i, 0, each[0])
        ws.write(i, 1, each[1])
        i += 1
    wb.save("handler.xls")

