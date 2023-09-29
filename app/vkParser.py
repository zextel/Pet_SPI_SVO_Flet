import requests
import httpx

from pprint import pprint
from selenium import webdriver
from typing import List

LIMITS = httpx.Limits(max_connections=5, max_keepalive_connections=5)
CLIENT = httpx.Client(limits=LIMITS)


class VK_Parser:
    def __init__(self, client_id, app_state):
        self.app_state = app_state
        self.client_id = client_id
        self.user_id = "-1"
        self.user_token = "-1"

    def auth(self) -> bool:
        """
        Производит авторизацию посредством OAuth. Возвращает булево значение - успешна-ли авторизация или нет.
        Если успешна - данные сохраняются в экземпляре класса в полях user_id и user_token
        """
        REQUEST_URL = f"https://oauth.vk.com/authorize?client_id={self.client_id}&display=page&redirect_uri=https://oauth.vk.com/blank.html&response_type=token"

        try:
            driver = webdriver.Chrome()
            driver.get(REQUEST_URL)

            while not driver.current_url.startswith(
                "https://oauth.vk.com/blank.html"
            ):
                pass
            if driver.current_url.startswith(
                "https://oauth.vk.com/blank.html"
            ):
                self.user_token = (
                    driver.current_url.split("#")[1]
                    .split("&")[0]
                    .split("=")[1]
                )
                self.user_id = (
                    driver.current_url.split("#")[1]
                    .split("&")[-1]
                    .split("=")[1]
                )
                driver.minimize_window()
                return True
            return False
        except:
            self.user_id = "-1"
            self.user_token = "-1"
            return False

    def logout(self):
        self.user_id = "-1"
        self.user_token = "-1"
        return True

    def retreive_posts(self, token: str, group_ids: List) -> List:
        count = 100

        for group_id in group_ids:
            api_url = f"https://api.vk.com/method/wall.get?owner_id=-{group_id}&count={count}&access_token={token}&v=5.131"
            response = requests.get(api_url)
            data = response.json()

            if "response" in data:
                posts = data["response"]["items"]
                for post in posts:
                    # Extract relevant information from each post
                    post_id = post["id"]
                    text = post["text"]
                    # ... extract other fields as needed
                    print(f"Post ID: {post_id}")
                    print(f"Text: {text}")
                    print("---")
            else:
                print("Error occurred while retrieving posts.")

    async def parse(self, publics_data, persons_data):
        ids = list(
            map(lambda x: x.replace("https://vk.com/id", ""), persons_data)
        )
        ids.extend(
            list(
                map(
                    lambda x: x.replace("https://vk.com/public", "-").replace(
                        "https://vk.com/club", "-"
                    ),
                    publics_data,
                )
            )
        )
        temp_result = {}
        try:
            for owner_id in ids:
                api_url = f"https://api.vk.com/method/wall.get?owner_id={owner_id}&count=100&access_token={self.user_token}&v=5.131"
                response = CLIENT.get(api_url).json()
                temp_result[owner_id] = list(
                    map(lambda x: x["text"], response["response"]["items"])
                )
            print(temp_result)
            return temp_result
        except Exception as e:
            pprint(e)
            return {}
