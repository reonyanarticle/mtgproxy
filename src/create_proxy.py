import re
from mtgsdk import Card
from commons import ENGLISH_CONDITION, STOP_WORDS, TRANSLATE_CONDITION, CardBody
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
    with open(file_name, "r") as f:
        texts: list[str] = [
            s.strip() for s in f.readlines() if ((len(s.strip()) > 0) and (s.strip() not in STOP_WORDS))
        ]
    return texts


def _find_card_url_by_name(name: str, language: str):
    sleep(2.0)
    if language == "english":
        cards: list = Card.where(name=name).all()
    else:
        cards = Card.where(name=name).where(language=language).all()
    if len(cards) == 0:
        print(f"{name}の画像を検索できませんでした。")
        return None
    else:
        for card in cards:
            if card.image_url != None:
                return card.image_url
        return None


def _texts_data_to_jsons(texts: list[str]) -> list[CardBody]:
    print("==== Get card information from text data. ====")
    jsons: list[CardBody] = []
    for text in tqdm(texts):
        card_info: CardBody = {}
        card_info["number"] = int(text[0])

        if re.search(TRANSLATE_CONDITION, text) is not None:
            card_info["name"] = re.search(TRANSLATE_CONDITION, text).group()
            card_info["language"] = "japanese"
        else:
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
    width: int = 185
    height: int = 257
    image_width, image_height = image.size
    width_reduction_rate: float = width / image_width
    height_reduction_rate: float = height / image_height
    image = image.convert("RGB")
    image = image.resize(
        (int(image_width * width_reduction_rate), int(image_height * height_reduction_rate)))
    return image


def __url_to_jpeg(image_url: str) -> Image.Image:
    bytes_data: bytes = urllib.request.urlopen(image_url).read()
    img: Image.Image = Image.open(io.BytesIO(bytes_data))
    img = __normalize_image(image=img)
    return img


def __arrange_imgs(pdf: canvas.Canvas, imgs: list[Image.Image]) -> None:
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
                pdf.drawString(img_width*row + 30, img_height*collum + 150, 'Proxy')
                index += 1
        else:
            continue
        break
    return None


def _create_print_pdf(jsons: list[CardBody], save_name: str) -> None:
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
    texts: list[str] = _read_txt(file_name=file_name)
    jsons: list[CardBody] = _texts_data_to_jsons(texts=texts)
    _create_print_pdf(jsons=jsons, save_name=save_name)
    return None
