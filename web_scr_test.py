#provided by realpython.com
import requests
from bs4 import BeautifulSoup

URL = "https://realpython.github.io/fake-jobs/"
page = requests.get(URL)
#print(page.status_code==200)
#print(page.text)
soup = BeautifulSoup(page.content, "html.parser")
#print(soup)
results = soup.find(id="ResultsContainer")
#print(results.prettify()) #print the html code
job_elements = results.find_all("div", class_="card-content")
#print(job_elements) #print div objects (object - html code from <div> to </div>)
print('Available vacancies:')
for el in job_elements:
    # print(el)
    links_el = el.find_all("a", class_="card-footer-item")
    learn_link, apply_link = links_el[0]['href'], links_el[1]['href']
    title_el = el.find("h2", class_="title")
    company_el = el.find("h3", class_="subtitle")
    location_el = el.find("p", class_="location")
    print(f'Position: {title_el.text.strip()}, company: {company_el.text.strip()}, location: {location_el.text.strip()}, Learn: {learn_link}, Apply: {apply_link}')
    print('\n')
print('\n'*2)

# empty result because the search is exact
# python_jobs = results.find_all("h2", string="Python")
# print(python_jobs)

# filtering via beautiful_soup
# python_jobs = results.find_all("h2", string= lambda text: "python" in text.lower())
# print(*[i.text for i in python_jobs], sep='\n')