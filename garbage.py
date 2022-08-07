# scrape work from home jobs in the following countries: New Zeland, Ireland, Great Britain(UK), Australia
# and save the work in the csv file

import requests
from bs4 import BeautifulSoup
import pandas as pd

def main_parser():
    country_site_dict={'1':"https://nz.indeed.com/jobs?q=work%20from%20home", 
    '2':"https://ie.indeed.com/jobs?q=work%20from%20home",
    '3':"https://uk.indeed.com/jobs?q=work%20from%20home",
    '4':"https://au.indeed.com/jobs?q=work%20from%20home"}
    link_dict={'1': 'https://nz.indeed.com',
    '2': 'https://ie.indeed.com',
    '3': 'https://uk.indeed.com/',
    '4': 'https://au.indeed.com/'}
    print("""Greetings from the English world parser!
    I can find work from home jobs in the following countries:
    1) New Zeland
    2) Ireland
    3) Great Britain(UK)
    4) Australia""")
    while True:
        answer=input('Choose your location by typing a number\n')
        if answer in ['1','2', '3', '4']:
            break
        else:
            print('Wrong choice!')
    while True:
        try:
            page_count=int(input('How many pages do you want to parse? Input a positive integer\n'))
            assert page_count>0, 'Must be positive!'
        except AssertionError as err:
            print(err)
        except ValueError:
            print('INTEGER!!!')
        else:
            break
    print('\n')
    additional_page_suffix='&start='
    job_title_lst=[]
    companies_lst=[]
    date_lst=[]
    link_lst=[]
    for page_num in range(0, (page_count*10), 10):
        URL=country_site_dict[answer]+additional_page_suffix+str(page_num)
        site=requests.get(URL)
        #print(site.status_code)
        #print(site.content)
        soup=BeautifulSoup(site.content, "lxml")
        #print(soup.prettify())
        job_cards=soup.find_all("div", class_="job_seen_beacon")
        link_lst=[]
        for i in job_cards:
            links_prep=i.find_all("td", class_="resultContent")
            for j in links_prep:
                raw_links=j.find_all("a")
                for q in raw_links:
                    link_lst.append(q['href'])
        apply_links=list(filter(lambda x: '/rc' in x, link_lst))
        print(*apply_links, sep='\n')
        print(len(apply_links))

if __name__=='__main__':
    main_parser()