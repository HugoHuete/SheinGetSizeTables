from numpy import concatenate
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


def main():
    # Get image names and urls from a csv file.
    data = pd.read_csv('urls.csv', sep=';')

    # open google chrome browser and go to us.shein.com
    driver = webdriver.Chrome()
    driver.get('https://us.shein.com/')

    # cerrar pantalla de cupones
    btCloseCoupons = driver.find_element(By.CLASS_NAME, 'S-dialog__closebtn')
    btCloseCoupons.click()

    # change languague to spanish
    btGlobal = driver.find_element(By.CLASS_NAME, 'sui_icon_nav_global_24px')
    hover = ActionChains(driver).move_to_element(btGlobal)
    hover.perform()  # hover to show language options
    driver.find_element(By.LINK_TEXT, 'Español').click()


    # Iterate for each url and save size table image with each name
    for name, url in data.values:
        driver.get(url)
        image_name = 'img\\' + name + '.png'
        sleep(2.5)


        # soldout_sizes = get_soldout_sizes(driver)

        # click on size guide options
        driver.find_element(
            By.CLASS_NAME, 'product-intro__size-guide-t').click()
        sleep(1)

        # Search for table element and look in the first value of the first column to see if it uses USA or EUR sizes
        table = driver.find_element(
            By.XPATH, '//div[@class="common-sizeinfo is-modal"]//div[@class="common-sizetable"]')
        row = table.find_elements(By.TAG_NAME, 'tr')[1]  # Get first row with data
        first_col_data = row.find_elements(By.TAG_NAME, 'td')[0]  # Get first element


        # Agregar ambas medidas: USA y EUR
        other_size = driver.find_element(By.XPATH, '//div[@class="common-sizetable__units common-detail__units"]') # Desplegar las opciones
        other_size.click()
        sleep(1)

        size_options_box = driver.find_element(By.CLASS_NAME, 'common-sizetable__country-box')
        sleep(1)
        options = size_options_box.find_elements(By.TAG_NAME, 'li') # Extraer todas las opciones

        if first_col_data.text[0:2] in ('EU', 'CN'):
            for option in options:
                if option.text == 'US':
                    option.click()
        else:
            for option in options:
                if option.text == 'EU':
                    option.click()
        
        table.screenshot(image_name)


# def get_soldout_sizes(driver):
#     soldout_sizes = []
#     sizes_box = driver.find_element(By.XPATH, '//div[@class="product-intro__select-box"]//div[@class="product-intro__size"]//div[@class="product-intro__size-choose"]')
#     soldout_elements = sizes_box.find_elements(By.XPATH, '//*[contains(@class,"product-intro__size-radio_soldout")]')
    
#     for soldout_element in soldout_elements:
#         soldout_size = soldout_element.find_element(By.CLASS_NAME, 'product-intro__size-radio-inner').text
#         soldout_sizes.append(soldout_size)

#     print(soldout_sizes)    



if __name__ == '__main__':
    main()
