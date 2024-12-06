import numpy as np
from django.core.files import File

from cardreader.models import User, HealthCareCard
from cardreader.services.converter_service import ConverterService
from cardreader.services.data_processor_service import DataProcessorService
from cardreader.services.image_processing_service import ImageProcessingService
from cardreader.services.reader_service import OcrReader, AllowlistOption


class HealthCareCardData:
    name: str
    birth_date: str
    issue_date: str
    card_number: str


class HealthCareCardReaderService:
    image_file: File
    image: np.ndarray
    user: User
    reader: OcrReader
    cardData: HealthCareCard
    processing_service: ImageProcessingService

    def __init__(self, image_file: File, user: User=None):
        self.image_file = image_file
        self.user = user
        self.reader = OcrReader()
        self.cardData = HealthCareCard(
            user=user,
        )
        self.processing_service = ImageProcessingService()
        self.converterService = ConverterService()
        self.dataProcessorService = DataProcessorService()

    def read_data(self):
        self.remove_backgrounds()
        self.read_name()
        self.read_birth_date()
        self.read_issue_date()
        self.read_card_number()
        return self.cardData

    def read_birth_date(self):
        image = self.processing_service.crop_image(self.image, (0.47, 0.62), (0.27, 0.6))
        result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.DATES)
        print(result)
        self.cardData.birthDate = self.dataProcessorService.process_date(result, accuracy_treshold=0.7)

    def read_name(self):
        cropped_image = self.processing_service.crop_image(self.image, (0.25, 0.42), (0.2, 0.8))
        name = ''
        #processed_image = self.processing_service.preprocess_image(cropped_image, ksize=9, treshold=90)
        result = self.reader.read(cropped_image, allowlist_key=AllowlistOption.UPPERCASE_HUNGARIAN)
        name = self.dataProcessorService.process_name(result)

        self.processing_service.imshow(cropped_image)
        print(result)
        self.cardData.name = name

    def read_issue_date(self):
        image = self.processing_service.crop_image(self.image, (0.80, 1), (0.35, 0.85))
        result = self.reader.read(image, show_image=True)
        print(result)
        self.cardData.issueDate = self.dataProcessorService.process_date(result)

    def read_card_number(self):
        image = self.processing_service.crop_image(self.image, (0.62, 0.82), (0.1, 0.65))
        result = self.reader.read(image, show_image=True)
        print(result)
        card_number = self.dataProcessorService.process_numeric_identifier(result, pattern='[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
        self.cardData.cardNumber = card_number if self.__validate_card_number(card_number) else ""

    def remove_backgrounds(self):
        self.image = self.processing_service.remove_background(self.converterService.file_to_numpy(self.image_file))
        self.image_file = self.converterService.numpy_to_file(self.image)
        self.cardData.imageFront = self.image_file

    def __validate_card_number(self, card_number):
        if len(card_number) != 9 or not card_number.isdigit():
            return False  # Hibás bemenet, ha nem 9 jegyű vagy nem csak számokból áll

        # Az első 8 számjegy szorzása és összeadása a megfelelő szabályok szerint
        mult_sum = sum(
            int(card_number[i]) * (3 if i % 2 == 0 else 7) for i in range(8)
        )

        # Az összeget 10-zel elosztva a maradékot kapjuk, ez az ellenőrző számjegy (CDV kód)
        cdv_kod = mult_sum % 10

        # Ellenőrizzük, hogy a CDV kód megegyezik-e a kilencedik számjeggyel
        return cdv_kod == int(card_number[8])