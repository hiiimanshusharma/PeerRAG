import os
import json
import time
import requests
import traceback
from tqdm import tqdm
from pathlib import Path
from slugify import slugify
from firecrawl import FirecrawlApp


from dotenv import load_dotenv

load_dotenv()

BASE_PATH = os.getenv('BASE_PATH')

class Crawler:

    def __init__(self):
        self.app = FirecrawlApp(api_key= os.getenv('FIRECRAWL_API_KEY'))

    def scraper(self, url):
        try:
            scrape_status = self.app.scrape_url(
                url,
                params={'formats': ['markdown', 'html']}
            )
            return scrape_status    
        except Exception as e:
            print(traceback.format_exc())
            raise Exception(f"Error scraping company profiles: {e}")
        
    def save_json(self, url, path):
        try:
            srape_data = self.scraper(url)
            Path(path).write_text(json.dumps(srape_data, indent=2))
        except Exception as e:
            print(traceback.format_exc())
            raise Exception(f"Error saving json: {e}")

# Scrape a website:
# url = 'https://peerlist.io/company?page={index}'
# path = 'companies_data_page{index}.json'
# for index in tqdm(range(21, 37)):
#   scraped_data = Crawler(url.format(index=index)).scrapeCompanyProfiles()
#   Path(path.format(index=index)).write_text(json.dumps(scraped_data, indent=2))


# def process_element(element):
#     # Your script to process each element
#     print(f"Processing element: {element}")
#     # Simulate API call here

# def process_elements_with_rate_limit(elements, batch_size, delay):
#     total_elements = len(elements)
#     for i in range(0, total_elements, batch_size):
#         # Process the current batch
#         batch = elements[i:i + batch_size]
#         for element in batch:
#             process_element(element)
        
#         # If this is not the last batch, sleep to avoid rate limit
#         if i + batch_size < total_elements:
#             print(f"Sleeping for {delay} seconds to avoid rate limit...")
#             time.sleep(delay)

# # Example usage
# elements = list(range(1, 101))  # Replace with your actual list
# batch_size = 10                 # Number of elements to process in one go
# delay = 60                      # Delay in seconds between batches

# process_elements_with_rate_limit(elements, batch_size, delay)


RATE_LIMIT = 20
TIME_WINDOW = 60  

def process_api_requests(company_profiles):
    # for i in range(, 380,):
    company_batch = company_profiles[199:200]  # Process 20 items at a time
    for company in company_batch:
        company_uri = company['company_link']
        url  = 'https://peerlist.io/{company_url}/people' 
        company_name = slugify(company['company_name'])
        print(f"Processing company: {company_name}")
        path = f"{BASE_PATH}/data/company_people_data/{company_name}.json"
        print(f"Saving data to: {path}")
        Crawler().save_json(
            url = url.format(company_url=company_uri), 
            path = f"{BASE_PATH}/data/company_people_data/{company_name}.json"
        )

        # After processing the batch, wait for the time window to reset
        # if i + RATE_LIMIT < 380:
        #     time.sleep(TIME_WINDOW)


def scrape_company_peoples():
    try:
        company_data = Path(f'{BASE_PATH}/data/company_profiles/companies_data.json').read_text()
        company_profiles = json.loads(company_data)
        # company_uri = company_profiles[0]['company_link']
        process_api_requests(company_profiles)
        # for company in company_profiles:
            # company_uri = company['company_link']
            # url  = 'https://peerlist.io/{company_url}/people' 
            # Crawler().save_json(
            #     url = url.format(company_url=company_uri), 
            #     path = f"{BASE_PATH}/data/company_people_data/{company['company_name']}.json"
            # )
        # url  = 'https://peerlist.io/{company_url}/people' 
        # Crawler().save_json(
        #     url = url.format(company_url=company_uri), 
        #     path = f"{BASE_PATH}/data/company_people_data/{company_profiles[0]['company_name']}.json"
        # )
        return "Succesfully scraped company profiles"
    except Exception as e:
        print(traceback.format_exc())
        raise Exception(f"Error scraping company profiles: {e}")
    

def scrape_people_resume(people):
    url  = 'https://peerlist.io{uri}/resume'
    print(f"Processing people: {people['name']}")
    Crawler().save_json(
            url = url.format(uri=people['profile_uri']), 
            path = f"{BASE_PATH}/data/people_resume{people['profile_uri']}.json"
        )

    
company_data = Path('/home/himanshu/peer-scr/data/master_data/companies_data_with_people.json').read_text()

company_profiles = json.loads(company_data)

peoples = []


for index, company in enumerate(company_profiles):
    if index < 200:
        peoples.extend(company['people'])
    else:
        break

    
if __name__ == '__main__':
    peoples_sublist = peoples[655: 658]
    for people in peoples_sublist:
        scrape_people_resume(people)










