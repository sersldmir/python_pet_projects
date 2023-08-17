import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


def duration_extractor(raw_week: str) -> int:
    if ' weeks long' in raw_week:
        number_of_weeks=raw_week.replace(' weeks long', '')
    elif ' week long' in raw_week:
        number_of_weeks=raw_week.replace(' week long', '')
    duration=int(number_of_weeks)
    return duration

def work_load_extractor(raw_amount: str, duration:int=0) -> int:
    if ' worth of material' in raw_amount:
        workload_amount=raw_amount.replace(' hours worth of material', '')
        if '-' in workload_amount:
            num1, num2 = map(int, workload_amount.split('-'))
            return round((num1+num2)/2, 1)
        else:
            if duration == 0:
                return int(workload)
            else:
                return round(int(workload_amount)/duration, 1)
    elif ' hours a week' in raw_amount:
        workload_amount=raw_amount.replace(' hours a week', '')
        if '-' in workload_amount:
            num1, num2 = map(int, workload_amount.split('-'))
            return round((num1+num2)/2, 1)
        else:
            return int(workload_amount)
    
# beggining of the program and input
print('Greetings from Data Science online courses parser! I parse the classcentral.com')
while True:
    try:
        answer=input('How many pages of the website do you wish to parse?\n')
        number_of_pages=int(answer)
        assert number_of_pages > 0, 'Wrong input!!!'
    except AssertionError as err:
        print(err)
    except ValueError:
        print('Wrong input!!!')
    else:
        break

# creating the lists for all the necessary pieces of data, links, installing webdriver
courses=[]
duration_weeks=[]
amount_of_study_a_week=[]
start_date=[]
providers=[]
no_of_reviews=[]
ratings=[]
additional_suffix='?page='
site="https://www.classcentral.com/subject/data-science"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# gathering data
for page_num in range(1, number_of_pages+1):

    # getting the content of a page
    driver.get(site+additional_suffix+str(page_num))
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")


    # finding the name of the courses
    course_soup = soup.find_all("h2", {"class": "text-1 weight-semi line-tight margin-bottom-xxsmall", "itemprop": "name"})
    for element in course_soup:
        courses.append(element.text.strip())

    # finding the names of the providers
    providers_soup = soup.find_all("a", class_="hover-underline color-charcoal text-3 margin-left-small line-tight")
    for element in providers_soup:
        providers.append(element.text.strip())

    # finding and computing ratings
    rating_dict={
    'Zero': 0,
    'Zero and a half': 0.5,
    'One': 1,
    'One and a half': 1.5,
    'Two': 2,
    'Two and a half': 2.5,
    'Three': 3,
    'Three and a half': 3.5,
    'Four': 4,
    'Four and a half': 4.5,
    'Five': 5}
    rating_soup = soup.find_all("span", class_="cmpt-rating-medium")
    for element in rating_soup:
        raw_value=element['aria-label']
        transit=raw_value.replace(' out of five stars', '')
        ratings.append(rating_dict[transit])

    # finding the amount of reviews
    reviews_soup = soup.find_all("a", class_="hover-no-underline margin-bottom-xxsmall row vert-align-middle")
    for element in reviews_soup:
        test_review=element.find("span", class_="text-3 color-gray margin-left-xxsmall")
        if test_review is not None:
            no_of_reviews.append(int(test_review.text[:test_review.text.find(' ')]))
        else:
            no_of_reviews.append(None)

    # finding the start date
    start_date_soup = soup.find_all("ul", {"class":"margin-top-small"})
    for element in start_date_soup:
        dates_test = element.find("span", {"class":"text-3 margin-left-small line-tight", "aria-label":"Start date"})
        if dates_test is None:
            start_date.append(None)
        else:
            if dates_test.text.strip() == 'Self paced':
                start_date.append(None)
            else:
                start_date.append(datetime.strptime(dates_test['content'], "%Y-%m-%d").date())


    # finding the duration and amount of learning time per week requiered
    duration_info_soup = soup.find_all("ul", {"class":"margin-top-small"})
    for element in duration_info_soup:
        test_dur_info = element.find("span", {"class":"text-3 margin-left-small line-tight", "aria-label":"Workload and duration"})
        if test_dur_info is None:
            duration_weeks.append(None)
            amount_of_study_a_week.append(None)
        else:
            raw_value=test_dur_info.text.strip()
            if len(raw_value.split(', '))==2:
                raw_amount, raw_week = raw_value.split(', ')
                # extracting the amount of week info
                duration = duration_extractor(raw_week)
                # extracting the workload info
                workload = work_load_extractor(raw_amount, duration=duration)
                duration_weeks.append(duration)
                amount_of_study_a_week.append(workload)
            elif len(raw_value.split(', '))==1:
                if ' worth of material' or ' hours a week' in raw_value:
                    amount_of_study_a_week.append(work_load_extractor(raw_value))
                    duration_weeks.append(None)
                elif ' week long' or ' weeks long' in raw_value:
                    amount_of_study_a_week.append(None)
                    duration_weeks.append(duration_extractor(raw_value))


# putting the data into DataFrame
the_data_frame = pd.DataFrame({
    'Name of the course' : courses,
    'Provider' : providers,
    'Rating' : ratings,
    'Amount of reviews' : no_of_reviews,
    'Start date' : start_date,
    'Duration (weeks)' : duration_weeks,
    'Workload (hours a week)' : amount_of_study_a_week})

# saving and closing
print('The results are saved in the data_science.csv file in the current directory! Happy learning!')
the_data_frame.to_csv('data_science_courses.csv')