from enum import Enum

import cv2
from easyocr import Reader
from sympy import false
from matplotlib import pyplot as plt

class AllowlistOption(Enum):
    DATES = '0123456789 .'
    HUNGARIAN_ALPHANUMERIC = '0123456789abcdefghijklmnopqrstuvwxyzáéíóöőúüűABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÖŐÚÜŰ '
    UPPERCASE_ENGLISH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    UPPERCASE_ENGLISH_NUMBERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    NUMBERS_ONLY = '0123456789'
    UPPERCASE_HUNGARIAN = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÖŐÚÜŰ '
    BIRTHPLACE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÖŐÚÜŰ() '

class OcrReader:
    reader:Reader

    def __init__(self, preprocess= false):
        self.reader = Reader(['hu'], gpu=True)
        self.preprocess = preprocess

    def read(self, image, detail=1, show_image=False, allowlist_key: AllowlistOption = None):
        if show_image:
            self.__imshow(image)

        allowlist = allowlist_key.value if allowlist_key else None

        return self.reader.readtext(image, detail=detail, allowlist=allowlist)

    def __imshow(self,  image, size= 10):
        h, w = image.shape[0], image.shape[1]
        aspect_ratio = w / h
        plt.figure(figsize=(size * aspect_ratio, size))
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()