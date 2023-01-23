from enum import IntEnum
from typing import NamedTuple


class VkAuthConfig(NamedTuple):
    LOGIN: str
    PASSWORD: str
    TOKEN: str
    TOKEN_APP: str


class VkConfig(NamedTuple):
    HUMORESKI: str
    ANEC_CATEGORY_B: str
    PESY: str


class VkUserSex(IntEnum):
    FEMALE = 1
    MALE = 2


class VkUserInfo(NamedTuple):
    first_name: str
    city: str
    sex: VkUserSex
    birth_year: int


class Mode(IntEnum):
    ECHO = 1
    SWAN = 2
    HUMOR = 3
