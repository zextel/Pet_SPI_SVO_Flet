import flet as ft
from app.MainViewModel import MainViewModel
from app.settings import FletView

view_model = MainViewModel()

SELECTED_FLET_VIEW = FletView.app


def setup_page(page: ft.Page):
    page.title = "ПостоМайнер"
    page.vertical_alignment = ft.MainAxisAlignment.START

    page.window_min_width = 1200
    page.window_min_height = 850

    page.window_width = 1200
    page.window_height = 850


async def main(page: ft.Page):
    setup_page(page)

    async def vk_auth(_):
        credentials = await view_model.auth()
        if credentials is not None:
            auth_button.text = "Авторизован - id" + credentials.user_id
            side_menu.controls += [logout_button]
            auth_button.bgcolor = ft.colors.GREEN_200
            auth_button.color = ft.colors.WHITE
            auth_button.icon = ft.icons.LOCK_OPEN_ROUNDED
            auth_button.on_click = None
        await page.update_async()

    async def vk_logout(_):
        view_model.logout()
        auth_button.text = "Войти в VK"
        auth_button.bgcolor = ft.colors.BLUE_200
        auth_button.color = ft.colors.BLUE
        auth_button.icon = ft.icons.LOCK_ROUNDED
        auth_button.on_click = vk_auth
        side_menu.controls.pop(-1)
        await page.update_async()

    async def add_public(_):
        if view_model.check_public_link(add_public_text_input.value):
            public_list.controls.append(
                ft.Row(
                    [
                        ft.Text(add_public_text_input.value, expand=True),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Удалить запись",
                            on_click=delete_public_clicked,
                        ),
                    ]
                )
            )
            add_public_text_input.value = ""
        else:
            add_public_text_input.border_color = ft.colors.RED
            page.dialog = incorrect_dialog
            incorrect_dialog.open = True
        await page.update_async()

    async def delete_public_clicked(marker):
        for line in public_list.controls:
            if line.controls[1] == marker.control:
                public_list.controls.remove(line)
                break
        await page.update_async()

    async def add_person(_):
        if view_model.check_person_link(add_person_text_input.value):
            person_list.controls.append(
                ft.Row(
                    [
                        ft.Text(add_person_text_input.value, expand=True),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Удалить запись",
                            on_click=delete_person_clicked,
                        ),
                    ]
                )
            )
            add_person_text_input.value = ""
        else:
            add_person_text_input.border_color = ft.colors.RED
            page.dialog = incorrect_dialog
            incorrect_dialog.open = True
        await page.update_async()

    async def delete_person_clicked(marker):
        for line in public_list.controls:
            if line.controls[1] == marker.control:
                person_list.controls.remove(line)
                break
        await page.update_async()

    async def reset_add_public_text_border(_):
        add_public_text_input.border_color = ft.colors.BLUE
        await page.update_async()

    async def reset_add_person_text_border(_):
        add_person_text_input.border_color = ft.colors.BLUE
        await page.update_async()

    async def start_parsing(_):
        if view_model.user_authorized():
            publics_data = list(
                map(lambda x: x.controls[0].value, public_list.controls)
            )
            persons_data = list(
                map(lambda x: x.controls[0].value, person_list.controls)
            )
            tokens_data = list(
                map(lambda x: x.controls[0].value, token_list.controls)
            )

            if publics_data or persons_data:
                button_start_parse.disabled = True
                progress_bar.value = None

                await view_model.start_parse(
                    publics_data, persons_data, tokens_data
                )

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
        view_model.reset_data()
        button_start_parse.disabled = False
        button_reset_parsed.disabled = True
        button_save_parsed.disabled = True
        await page.update_async()

    async def save_parsed(_):
        view_model.save_data(SELECTED_FLET_VIEW)
        await page.update_async()

    async def add_token_click(_):
        token_list.controls.append(
            ft.Row(
                [
                    ft.Text(add_token_text_input.value, expand=True),
                    ft.IconButton(
                        ft.icons.DELETE_OUTLINE,
                        tooltip="Удалить токен",
                        on_click=delete_token_clicked,
                    ),
                ]
            )
        )
        add_token_text_input.value = ""
        await page.update_async()

    async def delete_token_clicked(marker):
        for line in token_list.controls:
            if line.controls[1] == marker.control:
                token_list.controls.remove(line)
                break
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
        if view_model.user_authorized()
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
    public_list = ft.ListView(height=250, auto_scroll=True)
    add_public_text_input = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        hint_text="Ссылка вида https://vk.com/public12345678",
        on_change=reset_add_public_text_border,
    )
    add_public_button = ft.TextButton(
        text="Добавить сообщество", icon=ft.icons.ADD, on_click=add_public
    )
    add_person_header = ft.Text("Пользователи", size=28)
    person_list = ft.ListView(height=250, auto_scroll=True)
    add_person_text_input = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        hint_text="Ссылка вида https://vk.com/id12345678",
        on_change=reset_add_person_text_border,
    )
    add_person_button = ft.TextButton(
        text="Добавить пользователя", icon=ft.icons.ADD, on_click=add_person
    )

    # Токены
    add_token_header = ft.Text("Искомые токены", size=28)
    token_list = ft.ListView(
        height=200,
        spacing=10,
        padding=20,
        auto_scroll=True,
    )
    add_token_text_input = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        hint_text="Токен - искомое слово",
    )
    add_token_button = ft.TextButton(
        text="Добавить токен",
        icon=ft.icons.ADD,
        on_click=add_token_click,
    )

    # Нижняя панель
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
        on_click=lambda e: view_model.button_regvk_click(),
    )

    persons_publics_section = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    add_public_header,
                    ft.Container(
                        public_list,
                        bgcolor=ft.colors.WHITE30,
                        border_radius=10,
                    ),
                    add_public_text_input,
                    add_public_button,
                ],
                expand=1,
            ),
            ft.Column(
                controls=[
                    add_person_header,
                    ft.Container(
                        person_list,
                        bgcolor=ft.colors.WHITE30,
                        border_radius=10,
                    ),
                    add_person_text_input,
                    add_person_button,
                ],
                expand=1,
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    footer_buttons = ft.Row(
        [
            button_start_parse,
            button_reset_parsed,
            button_save_parsed,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True,
    )

    token_section = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Container(
                        token_list,
                        bgcolor=ft.colors.WHITE30,
                        border_radius=10,
                    )
                ],
                expand=3,
            ),
            ft.Column(
                controls=[add_token_text_input, add_token_button],
                expand=2,
                horizontal_alignment=ft.CrossAxisAlignment.END,
            ),
        ]
    )

    main_menu = ft.Column(
        controls=[
            ft.Row(
                [main_header, button_regvk],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            persons_publics_section,
            add_token_header,
            token_section,
            footer_buttons,
            progress_bar,
        ],
        expand=True,
    )

    await page.add_async(
        ft.Row(
            controls=[side_menu, ft.VerticalDivider(width=1), main_menu],
            height=800,
        )
    )


ft.app(target=main, view=SELECTED_FLET_VIEW)
