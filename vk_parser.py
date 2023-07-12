import vk_api
import pandas as pd
import logging
from time import sleep

TOKEN = "a8deab08a8deab08a8deab0840abcdd1f4aa8dea8deab08ccef076817f3e91e31e22ec2"
GROUPS = {"pn6":50_000, 
          "shkogwarts":40_000,
          "momdarinka":50_000, 
          "nevsep":50_000, 
          "caramel6":50_000, 
          "styd.pozor":50_000,
          "quality_journal":40_000,
          "bestory":20_000,
          "pikabu":50_000
          }

def retrieve_posts(vkapi, group, offset):
    """Достать посты из группы
    ---------------------------------
    Аргументы: 
    vkapi - объект апи вк;
    group - айди группы
    ---------------------------------
    Выход: список текстов постов"""
    return vkapi.wall.get(owner_id=group, count=100, offset=offset)["items"]

def retrieve_comments(vkapi, group, post):
    """Достать до 100 комментариев из поста
    -------------------------------------
    Аргументы: 
    vkapi - объект апи вк; 
    group - айди группы;
    post - айди поста;
    -------------------------------------
    Выход: список комментариев к посту"""

    comments_items = vkapi.wall.getComments(owner_id=group, post_id=post, count=100, need_likes=1)["items"]
    res = []
    print(f"Number of comments:{len(comments_items)}")
    for comment in comments_items:
        try:
            res.append({comment["text"]:comment['likes']['count']})
        except KeyError:
            res.append({comment["text"]:0})
    return res

def main():
    logger = logging.getLogger('vk_api_getter')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    vk_session = vk_api.VkApi(token=TOKEN, api_version="11.9.9", app_id="51608316")
    vkapi = vk_session.get_api()
    logger.info("We got the api!")
    part = 1
    for group_short, number_of_posts in GROUPS.items():
        offset = 0
        data = pd.DataFrame({"post":["test"], "comments":["test"]})
        group_info = vkapi.groups.getById(group_id=group_short)
        # print(group_info)
        id_group = group_info["groups"][0]["id"]
        logger.info(f"Got group id of {group_short}!")
        while offset<number_of_posts:
            posts = retrieve_posts(vkapi=vkapi, group=-id_group, offset=offset)
            sleep(0.5)
            logger.info("100 posts are retrieved!")
            offset+=100
            for post in posts:
                comments = retrieve_comments(vkapi=vkapi, group=-id_group, post=post["id"])
                logger.info("Comments are retrieved!")
                data.loc[len(data)] = [post["text"], comments]
                logger.info("Sleeping!")
                sleep(0.5)
        data.to_csv(f"vk_part{part}"+".csv")
        logger.info("Part of data saved!")
        part+=1
    logger.info("Everything is collected!")

if __name__ == "__main__":
    main()