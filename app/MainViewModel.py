import os
import json
import re
import subprocess
import sys
import webbrowser

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from datetime import datetime
from typing import List

from app.settings import CLIENT_ID, APP_STATE, FletView
from app.vkParser import VK_Parser

from app.models.VkAuthResponce import VkAuthResponce
from app.models.UserState import UserState, UserAuthorizedState

REGEX_PUBLIC = r"https://vk\.com/public\d+"
REGEX_CLUB = r"https://vk\.com/club\d+"
REGEX_PERSON = r"https://vk\.com/id\d+"


class MainViewModel:
    def __init__(self):
        self.parser = VK_Parser(CLIENT_ID, APP_STATE)
        self.user_state = UserState()
        self._temp_data = None

    async def auth(self) -> VkAuthResponce | None:
        if self.parser.auth():
            if self.parser.user_auth_data.user_id is not None:
                self.user_state.logged_in()
                return self.parser.user_auth_data

    async def logout(self):
        if self.parser.logout():
            self.user_state.logged_out()
            return True

    def get_user_state(self) -> UserState:
        return self.user_state

    def user_authorized(self) -> bool:
        return isinstance(self.user_state(), UserAuthorizedState)

    async def start_parse(
        self,
        publics: List[str],
        persons: List[str],
        tokens: List[str] = [],
    ):
        self._temp_data = await self.parser.parse(publics, persons, tokens)

    def reset_data(self):
        self._temp_data = None

    def save_data(self, flet_view, _dtype="parquet"):
        __filename = (
            f"/Выгрузка - {datetime.now().strftime('%d-%m-%Y %H-%M-%S')}"
        )
        __path = sys.path[0].replace("\\", "/") + __filename

        match _dtype.lower():
            case "json":
                __path = os.path.normpath(__path) + ".json"
                self._temp_data.to_json(__path)
            case "parquet":
                __path = os.path.normpath(__path) + ".parquet"
                table = pa.Table.from_pandas(self._temp_data)
                pq.write_table(table=table, where=__path)
            case "csv":
                __path = os.path.normpath(__path) + ".csv"
                self._temp_data.to_csv(__path)
            case _:
                return

        if flet_view == FletView.app:
            EXPLORER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")
            subprocess.run([EXPLORER_PATH, "/select,", __path], check=False)

        elif flet_view == FletView.browser:
            __page_path = sys.path[0].replace("\\", "/") + "/link.html"
            with open(__page_path, "w", encoding="utf-8") as f:
                print(
                    '<!doctype html><html lang="ru"><head><meta charset="utf-8" /></head><body>',
                    file=f,
                )
                print(
                    f'<a id="link" href="{__path}">Нажмите правой кнопкой мыши по этой строке и выберите пункт "Сохранить ссылку как..."</a>',
                    file=f,
                )
                print(
                    "</body></html>",
                    file=f,
                )
            webbrowser.open(__page_path)

    def button_regvk_click(self):
        webbrowser.open("https://regvk.com/id/")

    def check_public_link(self, link):
        return re.match(REGEX_PUBLIC, link) or re.match(REGEX_CLUB, link)

    def check_person_link(self, link):
        return re.match(REGEX_PERSON, link)
