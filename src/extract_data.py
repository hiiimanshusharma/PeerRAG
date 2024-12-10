import os
import json
import traceback
from pathlib import Path
from slugify import slugify
from bs4 import BeautifulSoup


class ExtractCompany:

    def __init__(self, path):
        self.path = path

    def soupify(self):
        html_content = json.load(Path(self.path).open('r'))['html']
        return BeautifulSoup(html_content, 'html.parser')
    
    def extractCompanies(self):
        try:
            soup = self.soupify()
            companies = soup.find_all('div', class_="mt-0.5")
            company_data = []
            for company in companies:
                try:
                    company_link = company.find('a', class_="p-4")['href']
                except:
                    company_link = "No link available"
                company_name = company.find('p', class_="text-gray-gray1k").string
                try:
                    company_img = company.find("img", class_="w-10")['src']
                except:
                    company_img = ""
                company_dsc = company.find('p', class_="text-primary").string

                company_data.append(
                    {
                        "company_link": company_link,
                        "company_name":company_name, 
                        "company_logo": company_img, 
                        "company_description": company_dsc
                    }
                )
            return company_data
        except Exception as e:
            raise Exception(f"Error extracting companies: {e}")
        

    def extractPeople(self):
        try:
            data = {}
            soup = self.soupify()
            data['location'] = soup.find('span', class_="text-gray-gray1k font-semibold text-xs capitalize flex items-center text-gray").p.string if soup.find('span', class_="text-gray-gray1k font-semibold text-xs capitalize flex items-center text-gray") else "No location available"
            data['website'] = soup.find('div', class_="flex items-center justify-center gap-6 mt-4 mb-4 text-center mx-auto").a['href'] if soup.find('div', class_="flex items-center justify-center gap-6 mt-4 mb-4 text-center mx-auto") else "No website available"
            groups = soup.find_all('ul', class_="grid grid-cols-1 sm:grid-cols-2 gap-4")
            people_list = []
            for group in groups:
                peoples = group.find_all('li')
                for people in peoples:
                    # try:
                    #     position = people.find('p', class_="text-gray text-xs paragraph-clamp").string
                    # except:
                    #     position = "No position available"
                    people_list.append({
                        "name": people.find('h3', class_="text-sm").string,
                        "profile_pic": people.find('img', class_="w-10")['src'],
                        "profile_uri": people.find('a', class_="flex")['href'],
                        "position": people.find('p', class_="text-gray text-xs paragraph-clamp").string if people.find('p', class_="text-gray text-xs paragraph-clamp") else "No position available",  
                    })

            data['people'] = people_list
            return data
        except Exception as e:
            print(traceback.format_exc())
            raise Exception(f"Error extracting people: {e}")
        
    def extractResume(self):
        try:
            data = {}
            soup = self.soupify()
            # data['resume'] = soup.find('div', class_="text-sm text-gray-gray1k").string
            if soup.find('div', class_="flex flex-col gap-4 py-10 px-4 sm:px-6").div.find('h2', class_="text-sm font-normal text-gray-gray1k sm:text-center"):
                data['title'] = soup.find('div', class_="flex flex-col gap-4 py-10 px-4 sm:px-6").div.find('h2', class_="text-sm font-normal text-gray-gray1k sm:text-center").string
            else:
                data['title'] = ""
            if soup.find('div', class_="flex flex-col gap-4 py-10 px-4 sm:px-6").div.find('div', class_="flex gap-1 items-center"):
                data['portfolio'] = soup.find('div', class_="flex flex-col gap-4 py-10 px-4 sm:px-6").div.find('div', class_="flex gap-1 items-center").a['title']
            else:
                data['portfolio'] = ""
            if len(soup.find('div', class_="w-full flex items-center justify-center").find_all('a')) > 0:
                links = soup.find('div', class_="w-full flex items-center justify-center").find_all('a')
                data['links'] = []
                for link in links:
                    data['links'].append({
                        "link_name": link['title'],
                        "link_url": link['href']
                    })
            else:
                data['links'] = []
            data['Education'] = []
            data['Experience'] = {"total_experience": "", "companies": []}
            profile_sections = soup.find('div', class_="lg:py-10 pt-8 pb-10 w-full px-4 sm:px-6").div.find_all('div', class_="mb-10 sm:pb-0 pb-4 sm:mb-20")
            for section in profile_sections:
                section_name = section.find('p', class_="text-gray-gray1k font-semibold text-base").string

                if section_name == "Experience":
                    total_experience = section.find('span', class_="bg-gray-gray1 text-light py-0.5 px-2 text-xs font-semibold rounded ml-2 sm:ml-4").string
                    data['Experience']['total_experience'] = total_experience

                    groups = section.find('div', class_="mt-6").find_all('div', class_="group")
                    for group in groups:
                        company_name = group.find('p', class_="text-gray-gray1k font-normal text-sm group-hover/company:underline truncate")
                        if group.find('div', class_="flex items-center gap-2 overflow-hidden"):
                            if group.find('div', class_="flex items-center gap-2 overflow-hidden").find('img'):
                                company_img =group.find('div', class_="flex items-center gap-2 overflow-hidden").find('img')['src']
                            else:
                                company_img = ""
                        else:
                            company_img = ""
                        if company_name:
                            company_name_txt = company_name.string
                            detail = group.find('div', class_="pl-8 relative w-full transition-colors duration-200 flex flex-col items-center pb-10")
                            if detail:
                                if detail.find('div', class_="w-full flex relative pt-2").find('div', class_="w-full flex"):
                                    detail_tag = detail.find('div', class_="w-full flex relative pt-2").find('div', class_="w-full flex").div.div.div.div.div
                                    role = detail_tag.div.p.string
                                    exp_duration = detail_tag.find('p', class_="text-light font-normal text-xs").strong.get_text()
                                else:
                                    role = ""
                                    exp_duration = ""
                            else:
                                if group.find('div', class_="pl-8 relative w-full transition-colors duration-200 flex flex-col items-center"):
                                    detail = group.find('div', class_="pl-8 relative w-full transition-colors duration-200 flex flex-col items-center")
                                    detail_tag = detail.find('div', class_="w-full flex relative pt-2").find('div', class_="w-full flex").div.div.div.div.div
                                    role = detail_tag.div.p.string
                                    exp_duration = detail_tag.find('p', class_="text-light font-normal text-xs").strong.get_text()
                                else:
                                    role = ""
                                    exp_duration = ""
                            data['Experience']['companies'].append({
                                "company_name": company_name_txt,
                                "company_logo": company_img,
                                "role": role,
                                "exp_duration": exp_duration
                            })
                        else:
                            continue
                        
                elif section_name == "Education":
                    edu_sections = section.find_all('div', class_="flex w-full justify-between items-start group gap-2")
                    for edu_section in edu_sections:
                        edu = edu_section.div
                        institute_name = edu.div.p.string
                        course_name = edu.find('p', class_="text-gray-gray1k font-normal text-xs").string
                        course_duration = edu.find('p', class_="text-light font-normal text-xs").string
                        data['Education'].append({
                            "institute_name": institute_name,
                            "course_name": course_name,
                            "course_duration": course_duration
                        })
            return data
        except Exception as e:
            raise Exception(f"Error extracting resume: {e}")
        

company_data = Path('/home/himanshu/peer-scr/data/master_data/companies_data_with_people.json').read_text()

company_profiles = json.loads(company_data)

person = company_profiles[0]['people'][0]
path = f"/home/himanshu/peer-scr/data/people_resume/{person['profile_uri']}.json"
ec = ExtractCompany(path)
resume_info = ec.extractResume()
print(resume_info)

for index, company_profile in enumerate(company_profiles):

    # print(company_profile)
    if index < 200:
        for people in company_profile['people']:
            path = f"/home/himanshu/peer-scr/data/people_resume/{people['profile_uri']}.json"
            ec = ExtractCompany(path)
            resume_info = ec.extractResume()
            people['resume'] = resume_info
    #     path = f"/home/himanshu/peer-scr/data/company_people_data/{slugify(company_profile['company_name'])}.json"
    #     ec = ExtractCompany(path)
    #     people_info = ec.extractPeople()
    #     company_profile['location'] = people_info['location']
    #     company_profile['website'] = people_info['website']
    #     company_profile['people'] = people_info['people']
    # else:
    #     break
    
output_file_path = Path("/home/himanshu/peer-scr/data/master_data/companies_people_resume.json")

with output_file_path.open('w', encoding='utf-8') as json_file:
    json.dump(company_profiles, json_file, indent=4)

print(f"People data saved to {output_file_path}")
