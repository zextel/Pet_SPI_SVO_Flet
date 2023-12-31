from pprint import pprint
from selenium import webdriver
from typing import List

import pandas as pd
import httpx


from app.models.VkAuthResponce import VkAuthResponce

LIMITS = httpx.Limits(max_connections=5, max_keepalive_connections=5)
CLIENT = httpx.Client(limits=LIMITS)


class VK_Parser:
    def __init__(self, client_id, app_state):
        self.app_state = app_state
        self.client_id = client_id
        self.user_auth_data = None

    def auth(self) -> VkAuthResponce | None:
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
                self.user_auth_data = VkAuthResponce(
                    driver.current_url.split("#")[1]
                    .split("&")[0]
                    .split("=")[1],
                    driver.current_url.split("#")[1]
                    .split("&")[1]
                    .split("=")[1],
                    driver.current_url.split("#")[1]
                    .split("&")[-1]
                    .split("=")[1],
                )
                driver.minimize_window()
                return True
            return False
        except:
            self.user_auth_data = None
            return False

    def logout(self):
        self.user_auth_data = None
        return True

    async def parse(
        self, publics_data, persons_data, tokens: List[str] = []
    ) -> pd.DataFrame:
        publics_data = set(map(str.lower, publics_data))
        tokens = set(map(str.lower, tokens))
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
        temp_result = pd.DataFrame(columns=["owner_id", "text"])
        try:
            for owner_id in ids:
                api_url = f"https://api.vk.com/method/wall.get?owner_id={owner_id}&count=100&access_token={self.user_auth_data.token}&v=5.131"
                _resp = CLIENT.get(api_url).json()
                if tokens:
                    texts = map(
                        lambda x: x["text"],
                        _resp["response"]["items"],
                    )

                    for text in texts:
                        for token in tokens:
                            if token in text.lower():
                                temp_result = pd.concat(
                                    [
                                        temp_result,
                                        pd.DataFrame(
                                            [[owner_id, text]],
                                            columns=temp_result.columns,
                                        ),
                                    ],
                                )
                                break

                else:
                    for text in map(
                        lambda x: x["text"], _resp["response"]["items"]
                    ):
                        temp_result = pd.concat(
                            [
                                temp_result,
                                pd.DataFrame(
                                    [[owner_id, text]],
                                    columns=temp_result.columns,
                                ),
                            ],
                        )

            return temp_result
        except Exception as e:
            pprint(e)
            return {}
