import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up WebDriver
driver = webdriver.Chrome()
url = 'https://peerlist.io/company'
driver.get(url)
# driver.implicitly_wait(20)
# time.sleep(3)

# print(driver.page_source)

time.sleep(60)

# Locate the grid element containing the companies
grid = driver.find_element(By.CLASS_NAME, "grid")

companies = grid.find_elements(By.TAG_NAME, "a")
# print(companies)
for company in companies:
    print("############################################")
    print(company.get_attribute("innerHTML"))
    print("********************************************")
    # divs = company.find_element(By.TAG_NAME, "div").find_elements(By.TAG_NAME, "div")
    # print(divs[0])
    # print(company.find_element(By.TAG_NAME, "div"))
# print(grid)

# # Corrected CSS selector for company names
# companies = grid.find_elements(By.CSS_SELECTOR, "p.text-gray-gray1k.font-semibold.text-sm.mb-0.5.group-hover\\:underline")

# # Print the company names
# for company in companies:
#     print(company.text)

# # Close the driver
# driver.quit()


# import http.client

# conn = http.client.HTTPSConnection("linkedin-data-api.p.rapidapi.com")

# headers = {
#     'x-rapidapi-key': "66e0bd9840mshf15ae1f92bc4eadp1a20adjsn43c9c9802b41",
#     'x-rapidapi-host': "linkedin-data-api.p.rapidapi.com"
# }

# conn.request("GET", "/get-company-by-domain?domain=apple.com", headers=headers)

# res = conn.getresponse()
# data = res.read()

# print(data.decode("utf-8"))
