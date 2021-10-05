import re
from typing import Optional
from mtgsdk import Card
from .commons import ENGLISH_CONDITION, STOP_WORDS, TRANSLATE_CONDITION, CardBody
from tqdm.auto import tqdm
import urllib
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from more_itertools import chunked
from time import sleep
from reportlab.lib.colors import white


def _read_txt(file_name: str) -> list[str]:
    """
    Read the deck list from the file.

    Parameters
    ----------
    file_name : str
        The name of the file containing the deck list.

    Returns
    -------
    list[str]
        The list of card information on the deck list.
    Raises
    ------
    ValueError
        If the input file is empty.
    """
    with open(file_name, "r") as f:
        texts: list[str] = [
            s.strip() for s in f.readlines() if ((len(s.strip()) > 0) and (s.strip() not in STOP_WORDS))
        ]
    if len(texts) == 0:
        raise ValueError("There is nothing written in the file. Please check the file name again.")

    return texts


def _find_card_url_by_name(name: str, language: str) -> Optional[str]:
    """
    Search for URL link for the card image.

    Parameters
    ----------
    name : str
        the card name. English or Japanese is fine. (Other languages are not supported.)
    language : str
        The language of the card name you want to search.

    Returns
    -------
    Optional[str]
        The URL link of card image. If it does not exist, None is returned.
    """
    sleep(1.0)
    if language == "english":
        cards: list = Card.where(name=name).all()
    else:
        cards = Card.where(name=name).where(language=language).all()
    if len(cards) == 0:
        print(f"Could not find image for {name}.")
        return None
    else:
        for card in cards:
            if card.image_url != None:
                return card.image_url
        return None


def _texts_data_to_jsons(texts: list[str]) -> list[CardBody]:
    """
    Store various information about the card in json.

    Parameters
    ----------
    texts : list[str]
        The list of card information on the deck list.

    Returns
    -------
    list[CardBody]
        the list of json where Card name, number of cards, search language and URL link are stored.
    """
    print("==== Get card information from text data. ====")
    jsons: list[CardBody] = []
    for text in tqdm(texts):
        card_info: CardBody = {}
        # 2桁入っている土地とかはそもそも無視している。
        card_info["number"] = int(text[0])

        # Wisdom Guildのデータかどうかの確認。
        if re.search(TRANSLATE_CONDITION, text) is not None:
            card_info["name"] = re.search(TRANSLATE_CONDITION, text).group()
            card_info["language"] = "japanese"
        else:
            # MTG Arenaからインポートしたデッキで英語かどうかの確認。
            if re.match(ENGLISH_CONDITION, text):
                card_info["name"] = text[2:]
                card_info["language"] = "english"
            else:
                words: list[str] = text.split(" ")
                card_info["name"] = words[1]
                card_info["language"] = "japanese"

        image_url = _find_card_url_by_name(name=card_info["name"], language=card_info["language"])
        if image_url is None:
            card_info["image_url"] = ""
        else:
            card_info["image_url"] = image_url

        jsons.append(card_info)
    print("===== The card information has been downloaded. =====")
    return jsons


def __normalize_image(image: Image.Image) -> Image.Image:
    """
    Adjust the size of the image.

    Parameters
    ----------
    image : Image.Image
        Card image.

    Returns
    -------
    Image.Image
        Card image arranged to a specific size.
    """
    width: int = 185
    height: int = 257
    image_width, image_height = image.size
    width_reduction_rate: float = width / image_width
    height_reduction_rate: float = height / image_height
    image = image.convert("RGB")
    image = image.resize((int(image_width * width_reduction_rate), int(image_height * height_reduction_rate)))
    return image


def __url_to_jpeg(image_url: str) -> Image.Image:
    """
    Convert URL to image.

    Parameters
    ----------
    image_url : str
        The URL link of The card.

    Returns
    -------
    Image.Image
        The Card image.
    """
    bytes_data: bytes = urllib.request.urlopen(image_url).read()
    img: Image.Image = Image.open(io.BytesIO(bytes_data))
    img = __normalize_image(image=img)
    return img


def __arrange_imgs(pdf: canvas.Canvas, imgs: list[Image.Image]) -> None:
    """
    Arrange images neatly on pdf.

    Parameters
    ----------
    pdf : canvas.Canvas
        The pdf that you want to print.
    imgs : list[Image.Image]
        List of images for proxy.
    """
    margin: int = 5
    img_width: int = 185
    img_height: int = 257
    index: int = 0
    for collum in range(3):
        for row in range(3):
            if index == len(imgs):
                break
            else:
                pdf.drawInlineImage(
                    imgs[index], img_width * row + margin * (row + 1), img_height * collum + margin * (collum + 1)
                )
                pdf.setFontSize(20)
                pdf.setFillColor(white)
                pdf.drawString(img_width * row + 30, img_height * collum + 150, "Proxy")
                index += 1
        else:
            continue
        break
    return None


def _create_print_pdf(jsons: list[CardBody], save_name: str) -> None:
    """
    Download the image from the URL and create the proxy pdf.

    Parameters
    ----------
    jsons : list[CardBody]
        the list of json where Card name, number of cards, search language and URL link are stored.
    save_name : str
        The file name at the time of save.
    """
    print("===== Creates a proxy from card information. =====")
    imgs: list[Image.Image] = []
    for json in tqdm(jsons):
        image_url: str = json["image_url"]
        if image_url == "":
            print(f"{json['name']}は画像をダウンロードすることができませんでした。")
        else:
            imgs += [__url_to_jpeg(image_url=image_url) for _ in range(json["number"])]

    if save_name[-3:] != "pdf":
        save_name = save_name + ".pdf"

    chunked_imgs: list[list[Image.Image]] = list(chunked(imgs, 9))
    pdf: canvas.Canvas = canvas.Canvas(save_name, pagesize=A4)
    for i in range(len(chunked_imgs)):
        if i != 0:
            pdf.showPage()

        __arrange_imgs(pdf=pdf, imgs=chunked_imgs[i])
    pdf.save()
    print("===== Proxy data creation succeeded. =====")
    return None


def create_proxy(file_name: str, save_name: str) -> None:
    """
    Main function that creates a proxy from the deck list.

    Parameters
    ----------
    file_name : str
        The name of the file containing the deck list.
    save_name : str
        The file name at the time of save.
    """
    texts: list[str] = _read_txt(file_name=file_name)
    jsons: list[CardBody] = _texts_data_to_jsons(texts=texts)
    _create_print_pdf(jsons=jsons, save_name=save_name)
    return None
