import flet as ft


class UserAuthorizedState:
    """
    State for authorized user
    """


class UserIncognitoState:
    """
    State for not-authorized user
    """


class UserState:
    def __init__(self) -> None:
        self.__idx = 0
        self.__states = [UserIncognitoState(), UserAuthorizedState()]

    def __call__(self) -> UserIncognitoState | UserAuthorizedState:
        return self.__states[self.__idx]

    def logged_in(self) -> None:
        """
        Set state to logged in
        """
        self.__idx = 1

    def logged_out(self) -> None:
        """
        Set state to logged in
        """
        self.__idx = 0
