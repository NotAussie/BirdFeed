import json
from .logger import Logger
from colorama import Fore

logger = Logger()


def load_posts() -> list:
    try:
        with open("/data/db.json", "r") as f:
            d = json.load(f)
        logger.output("INFO", Fore.LIGHTCYAN_EX, "DATABASE:SAVE", "Loaded database")

    except FileNotFoundError:
        d = {"posts": []}
        logger.output(
            "ERROR",
            Fore.LIGHTRED_EX,
            "DATABASE:LOAD",
            "Failed to load database (Using empty database)",
        )

    return d["posts"]


def save_posts(posts):
    try:
        with open("/data/db.json", "r") as f:
            d = json.load(f)

    except FileNotFoundError:
        d = {"posts": []}

    d["posts"] = posts

    try:
        with open("/data/db.json", "w+") as f:
            json.dump(d, f, indent=4)

    except PermissionError:
        logger.output(
            "INFO",
            Fore.LIGHTCYAN_EX,
            "DATABASE:SAVE",
            "Failed to save to db file, database will be in-memory only",
        )

    else:
        logger.output(
            "WARN", Fore.LIGHTYELLOW_EX, "DATABASE:SAVE", "Updated the database"
        )
