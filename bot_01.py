from seleniumbase import Driver

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import requests
import re

import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

url = 'https://www.truck2hand.com/category/cat_truck/'

response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')

page_number_text = soup.find('div', class_='css-1w2hcdj').text
page_number_arr = re.findall(r'\d+', page_number_text)
page_number_str = ''.join(page_number_arr)
page_number = int(page_number_str)
page_number

data = []

def export_to_excel(data):
    df = pd.DataFrame(data)

    excel_filename = 'output_excel.xlsx'
    current_date = datetime.now()
    sheet_name = current_date.strftime('%Y-%m-%d')

    try:
        if os.path.exists(excel_filename):
            os.remove(excel_filename)
    except PermissionError:
        print(f"ไม่สามารถลบไฟล์ {excel_filename} ได้เนื่องจากไฟล์ถูกใช้งานอยู่")

    # สร้างไฟล์ Excel ใหม่
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Data written to {excel_filename} in sheet {sheet_name}.")

def run():
    for i in range(page_number):
        try :
            url = 'https://www.truck2hand.com/category/cat_truck/?page=' + str(i+1)

            response = requests.get(url)
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            product_list = soup.find_all('div', class_='css-lq688s')
            print(f'หน้าที่ {str(i+1)}/{str(page_number)}' )
            print(f'พบจำนวน {str(len(product_list))} รายการ')

            for item in product_list:
                val = {}
                product_link = item.find('a', class_='tracking_AppListingCard-LinkListingItem-VerticalCard')
                if product_link :
                    val['product_link'] = product_link.get('href')
                    data.append(val)
            
            print(f'จำนวนสะสม {str(len(data))} รายการ')
            print('------------------------')

        except Exception as e:
            # จับข้อผิดพลาดอื่นๆ
            print(f"เกิดข้อผิดพลาด : {e}")

    unique_data = []
    for item in data:
        if item not in unique_data:
            unique_data.append(item)

    len(unique_data)

    error_list = []

    i=0

    for data_list in unique_data :

        try :
            url = 'https://www.truck2hand.com' + data_list['product_link']
            data_list['product_link'] = url
            print(f'{str(i+1)}/{str(len(unique_data))} : {url}')

            response = requests.get(url)
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            val_img = []
            img_list = soup.find_all('div', class_='thumbnail')

            for img_list_item in img_list :
                img_link = img_list_item.find('img').get('src')
                # print(img_link)
                val_img.append(img_link)
            
            data_list['img_link'] = val_img

            product_price = soup.find('div', class_='css-lf0cfo')
            data_list['ราคา'] = product_price.text

            product_detail = soup.find('div', class_='css-1dyfksc')
            product_detail_li = product_detail.find_all('li')

            for product_detail_item in product_detail_li :
                data_list[product_detail_item.find('div', class_='name').text] = product_detail_item.find('div', class_='value').text

            product_info = soup.find('div', class_='css-1qol0vc')
            data_list['ข้อมูลเพิ่มเติม'] = product_info.text
            
            seller_link = soup.find('a', class_='SellerProfileButton').get('href')
            data_list['seller_link'] = seller_link
            
        except Exception as e:
            # จับข้อผิดพลาดอื่นๆ
            print(f"เกิดข้อผิดพลาด : {e}")
            data_list['Error Message'] = e
            error_list.append(data_list)
            

        i+=1

        # # ทดสอบ 10 รายการ
        # if i == 10 :
        #     break

    print(error_list)

    export_to_excel(data)

if __name__ == "__main__":

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    run()
    end = time.strftime('%Y-%m-%d %H:%M:%S')
    
    print('------------------------')
    print(f'Start : {now}')
    print(f'Stop : {end}')
    print('------------------------')
    