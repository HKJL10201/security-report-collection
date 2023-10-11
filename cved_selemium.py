from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import pyperclip
import time
import os

# Use chromedriver_autoinstaller to ensure the latest version of ChromeDriver is installed
chromedriver_autoinstaller.install()

# Open the website
result_dir='cved'
root = 'https://www.cvedetails.com'


def process1month(year,month,month_idx):
    url='https://www.cvedetails.com/vulnerability-list/year-%d/month-%d/%s.html'%(year,month_idx,month)
    results_folder=os.path.join(result_dir,str(year),month)
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    idx=1
    last_page=False
    while True:
        # Initialize the browser driver (no need to specify the path to ChromeDriver)
        driver = webdriver.Chrome()
        driver.get(url)
        # Locate and interact with the button using its HTML attributes or XPath
        # Here, we'll assume the button has an 'id' attribute
        # button = driver.find_element(By.ID, 'button_id')  # Replace 'button_id' with the actual button ID
        button = driver.find_element(By.CSS_SELECTOR, 'a.text-center.me-4')
        # Click the button to trigger the JavaScript action
        button.click()
        time.sleep(1) # wait for the response
        # Retrieve the content from the clipboard using pyperclip
        clipboard_content = pyperclip.paste()
        # print("Clipboard Content:", clipboard_content)
        with open(os.path.join(results_folder,'%d_%s_%d.log'%(year,month,idx)),'w',newline='',encoding='utf-8') as wt:
            wt.write(clipboard_content)
        print(idx,end='')
        idx+=1

        possible_btn = driver.find_elements(By.CSS_SELECTOR, 'a.p-0')
        next_url = None
        for btn in possible_btn:
            try:
                next_btn=btn.find_element(By.CSS_SELECTOR, 'i.fas.fa-chevron-right.btn.btn-sm.btn-primary.text-white.ssc-btn-primary.py-1.px-3.m-0')
                href = btn.get_attribute('href')
                # next_url=root+href
                next_url=href
                break
            except NoSuchElementException:
                continue

        if next_url==None: # find the last page
            if last_page:
                driver.quit()
                break
            else:
                try:
                    # Find all <a> elements with the specified title attribute
                    all_page_btn = driver.find_elements(By.CSS_SELECTOR, 'a[title="List of security vulnerabilities, CVEs"]')

                    # Check if there are any matching elements
                    if all_page_btn:
                        # Get the 'href' attribute of the last <a> element in the list
                        last_page_btn = all_page_btn[-1]
                        href = last_page_btn.get_attribute('href')
                        next_url=href
                        last_page=True

                    else:
                        print("No elements with the specified title found on the page")
                        driver.quit()
                        break

                except NoSuchElementException:
                    # Handle the case where the elements are not found
                    print("Elements not found on the page")
        
        # Close the browser
        driver.quit()
        url=next_url
        # print('>>> Next URL: '+url)
        # time.sleep(3)

def main():
    # years=list(range(2013,2024))
    years=[2023]
    print(years)
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for year in years:
        for month_idx,month in enumerate(months):
            if month_idx>8:
                break
            print(year,month)
            process1month(year,month,month_idx+1)

main()
# process1month(2020,'October',10)
# process1month(2019,'November',11)
# process1month(2019,'December',12)