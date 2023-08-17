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
    '3': 'https://uk.indeed.com',
    '4': 'https://au.indeed.com'}
    country_name_dict={'1':"New_Zeland", 
    '2':"Ireland",
    '3':"UK",
    '4':"Australia"}
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
        soup=BeautifulSoup(site.content, "lxml")
        job_cards=soup.find_all("div", class_="job_seen_beacon")
        for el in job_cards:
            # find links
            links_prep=el.find_all("td", class_="resultContent")
            for j in links_prep:
                raw_links=j.find_all("a")
                for q in raw_links:
                    link_lst.append(link_dict[answer]+q['href'])
            # find and filter dates
            dates_=el.find_all("span", class_="date")
            for i in dates_:
                i = i.text.replace('Posted','')
                date_lst.append(i)
            # find job titile and company description
            essential_description=el.find_all("a")
            tr_lst=[es_el.text for es_el in essential_description]
            if len(tr_lst)<2:
                tr_lst.append('None')
            if 'location' in tr_lst[1]:
                job_title, company = tr_lst[0], tr_lst[2]
            else:
                job_title, company = tr_lst[0], tr_lst[1]
            job_title_lst.append(job_title)
            companies_lst.append(company)

    # filtering links to leave only apply links
    apply_links=list(filter(lambda x: '/rc' in x or '/company' in x, link_lst))

    #packing into a DataFrame and export it in a csv file
    the_data_base=pd.DataFrame({'Position': job_title_lst, 'Company': companies_lst, 'Published': date_lst, 'Apply': apply_links})
    the_data_base.to_csv(country_name_dict[answer]+".csv", index=False)
    print(f'The results are saved in a csv file "{country_name_dict[answer]+".csv"}" in the current directory!')
    print('Have a nice a day and good luck finding a dream work from home job!')


if __name__=='__main__':
    main_parser()