import chromedriver_binary 
from selenium import webdriver
from selenium.webdriver.common.by import By

def submit_form(url, textbox_value):
    # Create a new instance of the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    # Navigate to the website
    driver.get(url)
    
    # Find the form element
    forms = driver.find_elements(By.TAG_NAME, 'form')
    print(forms)

    textbox_val = forms[1].find_element(By.TAG_NAME, 'input')
    print(textbox_val.text)
    textbox_val.send_keys(textbox_value)
    button = forms[1].find_element(By.TAG_NAME, 'button')
    button.click()
    
    # # Find the textbox element within the form and fill it with the textbox_value
    # textbox = form.find_element_by_name('textbox_name')
    # textbox.send_keys(textbox_value)
    
    # # Find the button element within the form and click it
    # button = form.find_element_by_name('button_name')
    # button.click()
    
    # # Retrieve the resulting page
    # resulting_page = driver.page_source
    
    # Close the browser
    driver.quit()
    
    # return resulting_page

# Usage example
url = 'https://www.istoric-preturi.info/search'
textbox_value = '5942289000119'
resulting_page = submit_form(url, textbox_value)
print(resulting_page)
# Print the resulting page
print(resulting_page)