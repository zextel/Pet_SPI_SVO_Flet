from dataclasses import dataclass


@dataclass
class VkAuthResponce:
    """
    Dataclass for responce after authorization with VK OAuth
    """

    token: str
    expire: str
    user_id: str

    def __init__(self, token: str, expire: str, user_id: str):
        self.token = token
        self.expire = expire
        self.user_id = user_id
