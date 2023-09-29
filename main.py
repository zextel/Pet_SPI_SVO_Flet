import os
import json
import re
import subprocess
import sys
import webbrowser

from datetime import datetime

import flet as ft

from app.vkParser import VK_Parser
from app.models.UserState import (
    UserState,
    UserAuthorizedState,
)


APP_STATE = "8Hj9F7sG6k3l1P2o5Q4rT0uYwXvZcVbNmLxKjHgMfGdSfD3sA2qW1eR4tY7uI9oP8"
CLIENT_ID = "51756952"

parser_vk = VK_Parser(CLIENT_ID, APP_STATE)
user_state = UserState()


REGEX_PUBLIC = r"https://vk\.com/public\d+"
REGEX_CLUB = r"https://vk\.com/club\d+"

REGEX_PERSON = r"https://vk\.com/id\d+"

FLET_VIEW = {"APP": ft.AppView.FLET_APP, "BROWSER": ft.AppView.WEB_BROWSER}
SELECTED_FLET_VIEW = FLET_VIEW["BROWSER"]

temp_result = None


def setup_page(page):
    page.title = "ПостоМайнер"
    page.vertical_alignment = ft.MainAxisAlignment.START

    page.window_min_width = 1200
    page.window_min_height = 400


async def main(page: ft.Page):
    setup_page(page)

    async def vk_auth(_):
        if parser_vk.auth():
            auth_button.text = "Авторизован - id" + parser_vk.user_id
            side_menu.controls += [logout_button]
            auth_button.bgcolor = ft.colors.GREEN_200
            auth_button.color = ft.colors.WHITE
            auth_button.icon = ft.icons.LOCK_OPEN_ROUNDED
            auth_button.on_click = None
            user_state.logged_in()
        await page.update_async()

    async def vk_logout(_):
        parser_vk.logout()
        auth_button.text = "Войти в VK"
        auth_button.bgcolor = ft.colors.BLUE_200
        auth_button.color = ft.colors.BLUE
        auth_button.icon = ft.icons.LOCK_ROUNDED
        auth_button.on_click = vk_auth
        user_state.logged_out()
        side_menu.controls.pop(-1)
        await page.update_async()

    async def add_public(_):
        if re.match(REGEX_PUBLIC, add_public_text_input.value) or re.match(
            REGEX_CLUB, add_public_text_input.value
        ):
            public_list.controls.append(ft.Text(add_public_text_input.value))
            add_public_text_input.value = ""
        else:
            add_public_text_input.border_color = ft.colors.RED
            page.dialog = incorrect_dialog
            incorrect_dialog.open = True
        await page.update_async()

    async def add_person(_):
        if re.match(REGEX_PERSON, add_person_text_input.value):
            person_list.controls.append(ft.Text(add_person_text_input.value))
            add_person_text_input.value = ""
        else:
            add_person_text_input.border_color = ft.colors.RED
            page.dialog = incorrect_dialog
            incorrect_dialog.open = True
        await page.update_async()

    async def reset_add_public_text_border(_):
        add_public_text_input.border_color = ft.colors.BLUE
        await page.update_async()

    async def reset_add_person_text_border(_):
        add_person_text_input.border_color = ft.colors.BLUE
        await page.update_async()

    async def start_parsing(_):
        global temp_result
        if isinstance(user_state(), UserAuthorizedState):
            publics_data = list(map(lambda x: x.value, public_list.controls))
            persons_data = list(map(lambda x: x.value, person_list.controls))

            if publics_data or persons_data:
                button_start_parse.disabled = True
                progress_bar.value = None

                temp_result = await parser_vk.parse(publics_data, persons_data)

                progress_bar.value = 0
                button_reset_parsed.disabled = False
                button_save_parsed.disabled = False
            else:
                page.dialog = empty_dialog
                empty_dialog.open = True

        else:
            page.dialog = unauthorized_dialog
            unauthorized_dialog.open = True
        await page.update_async()

    async def reset_parsed(_):
        global temp_result
        temp_result = {}
        button_start_parse.disabled = False
        button_reset_parsed.disabled = True
        button_save_parsed.disabled = True
        await page.update_async()

    async def save_parsed(_):
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
            json.dump(temp_result, fp, ensure_ascii=False)
        if SELECTED_FLET_VIEW == FLET_VIEW["APP"]:
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
        elif SELECTED_FLET_VIEW == FLET_VIEW["BROWSER"]:
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

        await page.update_async()

    # Элементы боковой секции
    auth_button = ft.FloatingActionButton(
        icon=ft.icons.LOCK_ROUNDED,
        text="Войти в VK",
        on_click=vk_auth,
        width=230,
    )

    logout_button = ft.FloatingActionButton(
        icon=ft.icons.LOGOUT,
        text="Выход",
        on_click=vk_logout,
        bgcolor=ft.colors.RED_500,
    )

    side_menu = ft.Column(
        [auth_button, logout_button]
        if isinstance(user_state(), UserAuthorizedState)
        else [auth_button],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=250,
    )

    # Диалоги
    incorrect_dialog = ft.AlertDialog(
        title=ft.Text("Проверьте правильность вводимых данных!"),
    )
    unauthorized_dialog = ft.AlertDialog(
        title=ft.Text("Для работы необходимо авторизоваться!"),
    )
    empty_dialog = ft.AlertDialog(
        title=ft.Text("Отсутствуют данные для поиска!"),
    )
    progress_bar = ft.ProgressBar(value=0)

    # Элементы основной части страницы
    main_header = ft.Text("Источники данных", size=40)

    add_public_header = ft.Text("Сообщества", size=28)
    public_list = ft.ListView(
        expand=1, spacing=10, padding=20, auto_scroll=True
    )
    add_public_text_input = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        hint_text="Ссылка на сообщество вида https://vk.com/public12345678",
        on_change=reset_add_public_text_border,
    )
    add_public_button = ft.TextButton(
        text="Добавить сообщество", icon=ft.icons.ADD, on_click=add_public
    )
    add_person_header = ft.Text("Пользователи", size=28)
    person_list = ft.ListView(
        expand=1, spacing=10, padding=20, auto_scroll=True
    )
    add_person_text_input = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        hint_text="Ссылка на пользователя вида https://vk.com/id12345678",
        on_change=reset_add_person_text_border,
    )
    add_person_button = ft.TextButton(
        text="Добавить пользователя", icon=ft.icons.ADD, on_click=add_person
    )
    button_start_parse = ft.TextButton(
        text="Запуск сбора данных",
        icon=ft.icons.CLOUD_UPLOAD_ROUNDED,
        on_click=start_parsing,
    )
    button_reset_parsed = ft.TextButton(
        text="Начать заново",
        icon=ft.icons.RESTART_ALT_ROUNDED,
        disabled=True,
        on_click=reset_parsed,
    )
    button_save_parsed = ft.TextButton(
        text="Сохранить сообщения",
        icon=ft.icons.SAVE_AS_ROUNDED,
        disabled=True,
        on_click=save_parsed,
    )
    button_regvk = ft.TextButton(
        text=r"Помощник в определении ID страницы\пользователя",
        icon=ft.icons.ADS_CLICK_ROUNDED,
        on_click=lambda e: webbrowser.open("https://regvk.com/id/"),
    )

    await page.add_async(
        ft.Row(
            [
                side_menu,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        ft.Row(
                            [main_header, button_regvk],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        add_public_header,
                                        public_list,
                                        add_public_text_input,
                                        add_public_button,
                                    ],
                                    expand=True,
                                ),
                                ft.Column(
                                    [
                                        add_person_header,
                                        person_list,
                                        add_person_text_input,
                                        add_person_button,
                                    ],
                                    expand=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                button_start_parse,
                                button_reset_parsed,
                                button_save_parsed,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        progress_bar,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            height=800,
            expand=True,
        )
    )


ft.app(target=main, view=SELECTED_FLET_VIEW)
