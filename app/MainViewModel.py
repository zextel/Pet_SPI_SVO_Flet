import os
import json
import re
import subprocess
import sys
import webbrowser

from datetime import datetime
from typing import List

from app.settings import CLIENT_ID, APP_STATE, FLET_VIEW
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
        credentials = self.parser.user_auth_data
        if credentials:
            self.user_state.logged_in()
            return credentials

    async def logout(self):
        if self.parser.logout():
            self.user_state.logged_out()
            return True

    def get_user_state(self) -> UserState:
        return self.user_state

    def user_authorized(self) -> bool:
        return isinstance(self.user_state, UserAuthorizedState)

    async def start_parse(
        self, publics: List[str], persons: List[str], tokens: List[str] = []
    ):
        self._temp_data = await self.parser.parse(publics, persons, tokens)

    def reset_data(self):
        self._temp_data = None

    def save_data(self, flet_view):
        __path = (
            sys.path[0].replace("\\", "/")
            + f"/Выгрузка - {datetime.now().strftime('%d-%m-%Y %H-%M-%S')}.json"
        )
        print(__path)
        with open(
            __path,
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(self._temp_data, fp, ensure_ascii=False)
        if flet_view == FLET_VIEW["APP"]:
            __path = os.path.normpath(__path)
            FILEBROWSER_PATH = os.path.join(
                os.getenv("WINDIR"), "explorer.exe"
            )
            if os.path.isdir(__path):
                subprocess.run([FILEBROWSER_PATH, __path], check=False)
            elif os.path.isfile(__path):
                subprocess.run(
                    [FILEBROWSER_PATH, "/select,", __path], check=False
                )
        elif flet_view == FLET_VIEW["BROWSER"]:
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
