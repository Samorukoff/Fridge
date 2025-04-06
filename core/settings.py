from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    gs_link: str


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str = "config.env"):
    env= Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TOKEN"),
            admin_id=env.int("ADMIN_ID"),
            gs_link=env.str("GS_LINK")
        )
    )


settings= get_settings('config.env')