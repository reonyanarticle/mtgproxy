from typing import TypedDict

STOP_WORDS: list[str] = ["デッキ", "サイドボード", "Deck", "Sideboard"]
STOP_LANDS: list[str] = ["島", "平地", "沼", "山", "森", "Island", "Plains", "Swamp", "Mountain", "Forest"]

TRANSLATE_CONDITION: str = r"《.*?/"
ENGLISH_CONDITION: str = r"[a-zA-Z0-9_ ]{5}"
NUMBER_CONDITION: str = r"[0-9]{,2}"


class CardBody(TypedDict, total=False):
    name: str
    language: str
    number: int
    image_url: str
