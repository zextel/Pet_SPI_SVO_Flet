import flet as ft
from dataclasses import dataclass


APP_STATE = "8Hj9F7sG6k3l1P2o5Q4rT0uYwXvZcVbNmLxKjHgMfGdSfD3sA2qW1eR4tY7uI9oP8"
CLIENT_ID = "51756952"


@dataclass
class FletView:
    app: ft.AppView = ft.AppView.FLET_APP
    browser: ft.AppView = ft.AppView.WEB_BROWSER
