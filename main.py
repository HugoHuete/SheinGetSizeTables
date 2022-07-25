import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request
from time import sleep
from PIL import Image
from glob import glob
import os


def main():
    # Get image names and urls from a csv file.
    data = pd.read_csv('urls.csv', sep=';')
    data["Name"] = data["Name"].apply(lambda name: 'img\\' + name + '.png')

    # open google chrome browser and go to us.shein.com
    options = Options()
    options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()
    driver.implicitly_wait(15)
    driver.get('https://us.shein.com/')

    # Close coupons element
    driver.find_element(By.XPATH, '/html/body/div[1]/div[5]/div[1]/div/i').click()

    # change languague to spanish
    bt_global = driver.find_element(By.CLASS_NAME, 'sui_icon_nav_global_24px')
    hover = ActionChains(driver).move_to_element(bt_global)
    hover.perform()  # hover to show language options
    driver.find_element(By.LINK_TEXT, 'Español').click()

    first_iteration = True

    # Iterate for each url and save size table image with each name
    for name, url, price in data.values:
        # Avoiding errors while getting to the url
        while True:
            try:
                driver.get(url)
                break
            except:
                continue

        soldout_sizes = get_soldout_sizes(driver)

        # click on size guide options
        driver.find_element(
            By.CLASS_NAME, 'product-intro__size-guide-t').click()

        # Set measures to cm. Only needed in first iteration
        if first_iteration:
            driver.find_element(By.XPATH, '//div[@class="common-detail__button"]//div[@class="common-detail__button-inner"]//*[contains(@data-unit,"CM")]').click()
            first_iteration = False

        # Search for table element and get all the rows 
        table = driver.find_element(By.XPATH, '//div[@class="common-sizeinfo is-modal"]//div[@class="common-sizetable"]')
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Use first element to know if its USA or EUR standard
        first_data_row = rows[1]  # Get first row with data
        standard_used = first_data_row.find_elements(By.TAG_NAME, 'td')[0].text  # Get first element

        # Delete rows with sizes that are soldout before screenshot
        del_soldout_sizes_rows(driver, rows, soldout_sizes)

        # Add both standards: USA y EUR
        driver.find_element(By.XPATH, '//div[@class="common-sizetable__units common-detail__units"]').click() # Desplegar las opciones
        size_options_box = driver.find_element(By.CLASS_NAME, 'common-sizetable__country-box')
        options = size_options_box.find_elements(By.TAG_NAME, 'li') # Extraer todas las opciones+

        # If standards is US add EUR, otherwise add EU
        option_to_add = 'EU' if standard_used[0:2] == 'US' else 'US'
        for option in options:
            if option.text == option_to_add:
                option.click()

        # Get screenshot of full table
        modify_table_width(driver, rows[0])
        table.screenshot(name)

        # Close table and save product images
        driver.find_element(By.XPATH, '/html/body/div[5]/div/i').click()
        prod_img_name = name[:-4] + ' $' + str(price)
        download_images(driver, prod_img_name)
    
    convert_webp_to_png()




def get_soldout_sizes(driver):
    soldout_sizes = []
    sizes_box = driver.find_element(By.XPATH, '//div[@class="product-intro__select-box"]//div[@class="product-intro__size"]//div[@class="product-intro__size-choose"]')
    soldout_elements = sizes_box.find_elements(By.XPATH, './/*[contains(@class,"product-intro__size-radio_soldout")]')
    
    for soldout_element in soldout_elements:
        soldout_size = soldout_element.find_element(By.CLASS_NAME, 'product-intro__size-radio-inner').text

        soldout_sizes.append(soldout_size.split(sep='(')[0])

    return soldout_sizes   


def del_soldout_sizes_rows(driver, rows, soldout_sizes):
    for row in rows:
        selected_size = row.find_element(By.XPATH, './/td[1]').text
        if selected_size in soldout_sizes:
            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, row)


def modify_table_width(driver, row):
    #first we need to identify the table lenght so we can modify the containers width
    table_width = row.get_property('scrollWidth')
    new_container_width = str(table_width + 120)

    # Find the container element and increment the width
    container_element = driver.find_element(By.XPATH, '//*[contains(@class,"S-dialog common-detail-sizeGuidemodal")]//*[contains(@class,"S-dialog__wrapper")]') 
    driver.execute_script(f"arguments[0].setAttribute('style', 'width:{new_container_width}px;')", container_element)
    

def download_images(driver, image_name):
    # Clickear en imagen para agrandarla
    driver.find_element(By.XPATH, '//div[@class="swiper-slide product-intro__main-item cursor-zoom-in swiper-slide-active"]').click()
    sleep(2)
    images =  driver.find_elements(By.XPATH, '//div[@class="productimg-extend__thumbnails"]//ul//li')

    
    # Hover in each of the side images and screenshot the big image
    counter = 0
    for image in images:
        hover = ActionChains(driver).move_to_element(image)
        hover.perform()  
        sleep(0.4)

        # Get full image url
        full_image_url = 'https:' + driver.find_element(By.XPATH, '//div[@class="productimg-extend__main-image"]//img').get_attribute("src")
        full_name = image_name +' (' + str(counter) + ').webp'

        urllib.request.urlretrieve(full_image_url, full_name)
        counter += 1

def convert_webp_to_png():
    webp_images = glob("img/*.webp")
    for img in webp_images:
        converted_img_name = img.split(sep="\\")[1].split(sep=".")[0] + ".png"  # Extrae solamente en el nombre del archivo
        Image.open(img).convert("RGB").save("img\\" + converted_img_name,"png")
        os.remove(img)


if __name__ == '__main__':
    main()
