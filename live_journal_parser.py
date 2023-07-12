import requests
import re
import logging
import bs4
import csv
import json

from pathlib import Path
from bs4 import BeautifulSoup
from time import sleep
from typing import Tuple
from typing import Union


def initialize() -> Union[None, dict]:
    log_path = Path("log/log_data.json")
    if log_path.is_file():
        with open("log/log_data.json") as file:
            progress = json.load(file)
        return progress
    else:
        return None
    
    
def parse_init(progress:dict, logging_func:bool) -> Tuple[str, str, int, list, list, Union[int, None]]:
    
    if logging_func:
        print(f'Topic number: {progress["topic_name_num"]}')
        print(f'Topic query: {progress["topic_query"]}')
        print(f'Call counter: {progress["call_counter"]}')
        print(f'Links: {progress["links"]}')
        print(f'Likes: {progress["likes"]}')
        print(f'Link number: {progress["link_num"]}')

    return progress["topic_name_num"], progress["topic_query"], \
           progress["call_counter"], progress["links"], progress["likes"], progress["link_num"]


def save_progress(topic_name_num:int, topic_query:str, call_counter:Union[int, None],
                  links:list, likes:list, link_num:Union[None, int] = None) -> None:
    
    dic = {"topic_name_num":topic_name_num,
           "topic_query":topic_query,
           "call_counter":call_counter,
           "links":links,
           "likes":likes,
           "link_num":link_num}
    
    with open("log/log_data.json", "w") as file:
        json.dump(dic, file)




def get_query_params(link:str, logging_func:bool = False) -> list:

    topic_id = int(re.findall(r"(?<=%3A)\d*(?=%7D$)", link)[0])
    page = int(re.findall(r"(?<=\d)\d(?=medius__)", link)[0])
    control_number = int(re.findall(r"(?<=%5B%)\d*(?=%)", link)[0])
    call_pointer = int(re.findall(r"(?<=%3A)\d*(?=%2C)", link)[0])
    if logging_func:
        print(f"Topic_id {topic_id}")
        print(f"Page {page}")
        print(f"Control_number {control_number}")
        print(f"Call_pointer {call_pointer}")
    return topic_id, page, control_number, call_pointer


def get_post_links_likes(api_response:str, logging_func:bool = False) -> Tuple[list, list]:

    links = re.findall(r"(?<=\"link\":\")\S+\/\d+\.html\?media(?=\")", api_response)
    likes = re.findall(r"(?<=\"likeCount\"\:)\d+(?=,)", api_response)

    if logging_func:
        if len(links)!=1:
            print(f"Extracted links: {links[1:]}")
            print(f"Extracted likes: {likes[1:]}")
        else:
            print(f"Extracted links: {links}")
            print(f"Extracted likes: {likes}")

    if len(links)!=1:
        return links[1:], likes[1:]
    else:
        return links, likes
    

def extract_text(soup:bs4.BeautifulSoup) -> str:

    # заголовок поста
    header_soup = soup.find_all("h1", {'class': ['mdspost-title'], 'ng-non-bindable': ''})

    # текст поста
    post_soup = soup.find_all("div", {"class":"mdspost-text-container aentry-post__text aentry-post__text--view"})

    text_crumbs_soup = BeautifulSoup(str(post_soup), "lxml")
    text_tags = text_crumbs_soup.find_all(["p", "b", "mark", "small", "del", "ins", "sub", 
                                 "sup",  "i", "strong", "em", "h1", "h2", "h3", 
                                 "h4", "h5", "h6", "div", "head", "hr", "q",
                                 "pre", "section", "title"])
    
    post_text = '.\n'.join([word.text.strip() for word in text_tags if re.match(r"[а-яёА-ЯЁ]{3,}", word.text.strip())])
    whole_text = '.\n'.join([header.text.strip() for header in header_soup]) + ".\n" + post_text
    return whole_text

def extract_comments(soup:bs4.BeautifulSoup) -> list:

    script_soup = str(soup.find_all("script", {"type":"text/javascript"}))

    comment_pattern = r"(?<=\"article\":\").*?(?=\",\"noid\")"

    comments = []

    for raw_comment in re.findall(comment_pattern, script_soup):
        comment_soup = BeautifulSoup(raw_comment, "lxml")
        processed_comment_soup = comment_soup.find_all(["p", "b", "mark", "small", "del", "ins", "sub", 
                                    "sup",  "i", "strong", "em", "hr", "q", "pre"])
        comment = ' '.join([comment_piece.text.strip() for comment_piece in processed_comment_soup if comment_piece!=""])
        comments.append(comment)

    full_comments = [comment for comment in comments if comment!=""]

    return full_comments

def extract_author(soup:bs4.BeautifulSoup) -> str:

    autor_span = soup.find_all('span', attrs={'class':['aentry-head__info', 'aentry-head__username']})
    a_link = BeautifulSoup(str(autor_span), 'lxml').find('a', attrs={'class':'i-ljuser-username'})
    return a_link['href']


TOPIC_LIMIT = 900_000
TOPICS = {
    "грибы":"https://l-api.livejournal.com/__api/?callback=jQuery56072134medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22192%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607213%7D",
    "знаменитости":"https://l-api.livejournal.com/__api/?callback=jQuery56072134medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2217%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607213%7D",
    "игры":"https://l-api.livejournal.com/__api/?callback=jQuery56072144medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2218%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607214%7D",
    "литература":"https://l-api.livejournal.com/__api/?callback=jQuery56072155medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2221%22%5D%2C%22offset%22%3A35%2C%22limit%22%3A10%7D%2C%22id%22%3A5607215%7D",
    "музыка":"https://l-api.livejournal.com/__api/?callback=jQuery56072155medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2222%22%5D%2C%22offset%22%3A35%2C%22limit%22%3A10%7D%2C%22id%22%3A5607215%7D",
    "праздники":"https://l-api.livejournal.com/__api/?callback=jQuery56072151medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22154%22%5D%2C%22offset%22%3A0%2C%22limit%22%3A25%7D%2C%22id%22%3A5607215%7D",
    "рыбалка":"https://l-api.livejournal.com/__api/?callback=jQuery56072184medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22156%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607218%7D",
    "спорт":"https://l-api.livejournal.com/__api/?callback=jQuery56072184medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2223%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607218%7D",
    "театр":"https://l-api.livejournal.com/__api/?callback=jQuery56072185medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22157%22%5D%2C%22offset%22%3A35%2C%22limit%22%3A10%7D%2C%22id%22%3A5607218%7D",
    "фантастика":"https://l-api.livejournal.com/__api/?callback=jQuery56072185medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2224%22%5D%2C%22offset%22%3A35%2C%22limit%22%3A10%7D%2C%22id%22%3A5607218%7D",
    "фотография":"https://l-api.livejournal.com/__api/?callback=jQuery56072187medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22158%22%5D%2C%22offset%22%3A55%2C%22limit%22%3A10%7D%2C%22id%22%3A5607218%7D",
    "юмор":"https://l-api.livejournal.com/__api/?callback=jQuery56072176medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22138%22%5D%2C%22offset%22%3A45%2C%22limit%22%3A10%7D%2C%22id%22%3A5607217%7D",
    "архитектура":"https://l-api.livejournal.com/__api/?callback=jQuery56072194medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22148%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607219%7D",
    "животные":"https://l-api.livejournal.com/__api/?callback=jQuery56072194medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2227%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607219%7D",
    "природа":"https://l-api.livejournal.com/__api/?callback=jQuery56072194medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2228%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607219%7D",
    "птицы":"https://l-api.livejournal.com/__api/?callback=jQuery56072194medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22159%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607219%7D",
    "путешествия":"https://l-api.livejournal.com/__api/?callback=jQuery56072194medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2229%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607219%7D",
    "цветы":"https://l-api.livejournal.com/__api/?callback=jQuery56072194medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22160%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607219%7D",
    "компьютеры":"https://l-api.livejournal.com/__api/?callback=jQuery56072224medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2248%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607222%7D",
    "корабли":"https://l-api.livejournal.com/__api/?callback=jQuery56072224medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22155%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607222%7D",
    "космос":"https://l-api.livejournal.com/__api/?callback=jQuery56072214medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2249%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607221%7D",
    "лингвистика":"https://l-api.livejournal.com/__api/?callback=jQuery56072214medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22161%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607221%7D",
    "производство":"https://l-api.livejournal.com/__api/?callback=jQuery56072214medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2251%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607221%7D",
    "техника":"https://l-api.livejournal.com/__api/?callback=jQuery56072214medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2252%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607221%7D",
    "технологии":"https://l-api.livejournal.com/__api/?callback=jQuery56072204medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2253%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607220%7D",
    "энергетика":"https://l-api.livejournal.com/__api/?callback=jQuery56072204medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2254%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607220%7D",
    "здоровье":"https://l-api.livejournal.com/__api/?callback=jQuery56072234medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2233%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607223%7D",
    "Коронавирус":"https://l-api.livejournal.com/__api/?callback=jQuery56072234medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22152%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607223%7D",
    "косметика":"https://l-api.livejournal.com/__api/?callback=jQuery56072234medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2231%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607223%7D",
    "медицина":"https://l-api.livejournal.com/__api/?callback=jQuery56072224medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2232%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607222%7D",
    "спорт":"https://l-api.livejournal.com/__api/?callback=jQuery56072224medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2223%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607222%7D",
    "дети":"https://l-api.livejournal.com/__api/?callback=jQuery56072254medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2243%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607225%7D",
    "образование":"https://l-api.livejournal.com/__api/?callback=jQuery56072254medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%228%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607225%7D",
    "отношения":"https://l-api.livejournal.com/__api/?callback=jQuery56072254medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22137%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607225%7D",
    "психология":"https://l-api.livejournal.com/__api/?callback=jQuery56072244medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22139%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607224%7D",
    "семья":"https://l-api.livejournal.com/__api/?callback=jQuery56072244medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2244%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607224%7D",
    "Еда":"https://l-api.livejournal.com/__api/?callback=jQuery56072244medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2225%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607224%7D",
    "напитки":"https://l-api.livejournal.com/__api/?callback=jQuery56072234medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22147%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607223%7D",
    "дача":"https://l-api.livejournal.com/__api/?callback=jQuery56072264medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2236%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607226%7D",
    "дизайн":"https://l-api.livejournal.com/__api/?callback=jQuery56072264medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2237%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607226%7D",
    "мода":"https://l-api.livejournal.com/__api/?callback=jQuery56072264medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2238%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607226%7D",
    "отзывы":"https://l-api.livejournal.com/__api/?callback=jQuery56072264medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22140%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607226%7D",
    "ремонт":"https://l-api.livejournal.com/__api/?callback=jQuery56072264medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2239%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607226%7D",
    "рукоделие":"https://l-api.livejournal.com/__api/?callback=jQuery56072264medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22141%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607226%7D",
    "философия":"https://l-api.livejournal.com/__api/?callback=jQuery56072254medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2241%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607225%7D",
    "город":"https://l-api.livejournal.com/__api/?callback=jQuery56072284medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%224%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607228%7D",
    "недвижимость":"https://l-api.livejournal.com/__api/?callback=jQuery56072284medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%227%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607228%7D",
    "общество":"https://l-api.livejournal.com/__api/?callback=jQuery56072284medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%229%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607228%7D",
    "политика":"https://l-api.livejournal.com/__api/?callback=jQuery56072274medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2210%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607227%7D",
    "работа":"https://l-api.livejournal.com/__api/?callback=jQuery56072274medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2212%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607227%7D",
    "финансы":"https://l-api.livejournal.com/__api/?callback=jQuery56072274medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2214%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607227%7D",
    "экология":"https://l-api.livejournal.com/__api/?callback=jQuery56072274medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%2215%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607227%7D",
    "экономика":"https://l-api.livejournal.com/__api/?callback=jQuery56072274medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%22144%22%5D%2C%22offset%22%3A25%2C%22limit%22%3A10%7D%2C%22id%22%3A5607227%7D"
}

def main():

    logger = logging.getLogger('live_journal_parser')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)


    init_dict = initialize()
    logger.debug(f"\n---------------------------------------------------\nINITIALIZING PARSER\n---------------------------------------------------\n")
    sleep(2)

    # to track if we loaded data from log file and not to do it again (when it is done in loops)
    initialized_query = False
    initialized_data = False
    initialized_call_counter = False
    initialized_link_counter = False
    



    # parsing loaded data
    if init_dict is not None:
        t_num_pointer, query, call, links_f, likes_f, link_num_f  = parse_init(init_dict, True)

    topic_num_pointer = 0 if init_dict is None else t_num_pointer

    for topic_name_num in range(topic_num_pointer, len(TOPICS.keys())):

        topic_name = list(TOPICS.keys())[topic_name_num]

        if not initialized_query:
            topic_query = TOPICS[topic_name] if init_dict is None else query
            initialized_query = True
        else:
            topic_query = TOPICS[topic_name]


        logger.debug(f"\n---------------------------------------------------\nWORKING WITH TOPIC {topic_name}\n---------------------------------------------------\n")
        sleep(1)

        # initiate file if not present
        if not Path(f"data/{topic_name}.csv").is_file():
            logger.debug(f"\n---------------------------------------------------\nINITIATING FILE\n---------------------------------------------------\n")
            sleep(1)
            with open(f"data/{topic_name}.csv", "w") as file:
                writer = csv.writer(file)
                writer.writerow(["url", "author", "likes", "text", "comments"])
            logger.debug(f"\n---------------------------------------------------\nFILE INITIATED!\n---------------------------------------------------\n")
            sleep(1)
        else:
            logger.debug(f"\n---------------------------------------------------\nFILE ALREADY INITIATED!\n---------------------------------------------------\n")
            sleep(1)


        # data to parse
        if not initialized_data:
            posts_links = [] if init_dict is None else links_f
            posts_likes = [] if init_dict is None else likes_f
            initialized_data = True
        else:
            posts_links = []
            posts_likes = []


        # get params for the query
        topic_id, page, control_number, call_pointer = get_query_params(topic_query, logging_func=True)
        work_horse = f"https://l-api.livejournal.com/__api/?callback=jQuery{topic_id}{page}medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%{control_number}%22%5D%2C%22offset%22%3A{call_pointer}%2C%22limit%22%3A10%7D%2C%22id%22%3A{topic_id}%7D"
        

        # initiate query counter and extinguisher
        if not initialized_call_counter:
            if (init_dict is None) or (init_dict is not None and link_num_f is None):
                not_extinguish = True
                call_counter = 1 if init_dict is None else call
                logger.debug(f"\n---------------------------------------------------\nEXTRACTING LINKS!\n---------------------------------------------------\n")
                sleep(1)
                initialized_call_counter = True
            else:
                not_extinguish = False
                call_counter = None
                logger.debug(f"\n---------------------------------------------------\nWE HAVE THE LINKS! PARS'EM!\n---------------------------------------------------\n")
                sleep(1)
                initialized_call_counter = True
        else:
            call_counter = 1
            not_extinguish = True

        while not_extinguish:
            response = requests.get(work_horse)
            links, likes = get_post_links_likes(response.text, logging_func=True)
            posts_links.extend(links)
            posts_likes.extend(likes)
            if len(links)==1:
                not_extinguish=False
                logger.debug("\n---------------------------------------------------\nAPI REFUSES TO GIVE MORE! WORKING ON THE POSTS NOW!\n---------------------------------------------------\n")
                sleep(1)
                break
            if call_counter==TOPIC_LIMIT-1:
                not_extinguish=False
                logger.debug("\n---------------------------------------------------\nREACHED TOPIC LIMIT! WORKING ON THE POSTS NOW!\n---------------------------------------------------\n")
                sleep(1)
                break
            logger.debug(f"\n---------------------------------------------------\nSLEEPING ON CALL_COUNTER {call_counter}\n---------------------------------------------------\n")
            sleep(5)
            call_counter+=1
            page+=1
            call_pointer+=10
            work_horse = f"https://l-api.livejournal.com/__api/?callback=jQuery{topic_id}{page}medius__get_public_items_categories&request=%7B%22jsonrpc%22%3A%222.0%22%2C%22method%22%3A%22medius.get_public_items_categories%22%2C%22params%22%3A%7B%22cat_ids%22%3A%5B%{control_number}%22%5D%2C%22offset%22%3A{call_pointer}%2C%22limit%22%3A10%7D%2C%22id%22%3A{topic_id}%7D"
            save_progress(topic_name_num, work_horse, call_counter, posts_links, posts_likes)
            logger.debug("\n---------------------------------------------------\nSAVING PROGRESS!\n---------------------------------------------------\n")
            sleep(1.5)
            logger.debug("\n---------------------------------------------------\nMOVING ON!\n---------------------------------------------------\n")
            sleep(1)

        # initialize link_counter
        if not initialized_link_counter:
            if (init_dict is None) or (init_dict is not None and link_num_f is None):
                link_counter = 0
                initialized_link_counter = True
            else:
                link_counter = link_num_f + 1 # to avoid duplicates
                initialized_link_counter = True
        else:
            link_counter = 0

        for num_link in range(link_counter, len(posts_likes)):
            try:
                number = re.compile(r"\d+")
                id_of_post = re.findall(number, posts_links[num_link])[0]
                logger.debug(f"\n---------------------------------------------------\nWORKING ON POST WITH ID {id_of_post}\n---------------------------------------------------\n")
                sleep(1)
                post_response = requests.get(posts_links[num_link])
                soup = BeautifulSoup(post_response.text, "lxml")
                logger.debug("\n---------------------------------------------------\nEXTRACTING AUTHOR\n---------------------------------------------------\n")
                sleep(1)
                author = extract_author(soup)
                logger.debug("\n---------------------------------------------------\nEXTRACTING TEXTS\n---------------------------------------------------\n")
                sleep(1)
                text = extract_text(soup)
                logger.debug("\n---------------------------------------------------\nEXTRACTING COMMENTS\n---------------------------------------------------\n")
                sleep(1)
                comments = extract_comments(soup)
                logger.debug("\n---------------------------------------------------\nWRITING ROW\n---------------------------------------------------\n")
                sleep(1)
                with open(f"data/{topic_name}.csv", "a") as file:
                    writer = csv.writer(file)
                    writer.writerow([posts_links[num_link], author, posts_likes[num_link], text, comments])
                logger.debug("\n---------------------------------------------------\nROW WRITTEN!\n---------------------------------------------------\n")
                sleep(1)
                save_progress(topic_name_num, work_horse, call_counter, posts_links, posts_likes, num_link)
                logger.debug("\n---------------------------------------------------\nSAVING PROGRESS!\n---------------------------------------------------\n")
                sleep(1.5)
                logger.debug("\n---------------------------------------------------\nMOVING ON!\n---------------------------------------------------\n")
                sleep(1)
            except IndexError:
                break

            logger.debug(f"\n---------------------------------------------------\nDONE WITH TOPIC {topic_name}!\n---------------------------------------------------\n")
            sleep(1)
            logger.debug(f"\n---------------------------------------------------\nMOVING ON!\n---------------------------------------------------\n")
            sleep(2)
    
    logger.debug(f"\n---------------------------------------------------\nPARSING DONE!\n---------------------------------------------------\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
