from datetime import datetime

import numpy as np
from django.core.files import File
from django.db.models.expressions import result
from tifffile import imshow

from cardreader.dtos.student_card_dto import StudentCardData
from cardreader.models import User, StudentCard
from cardreader.services.converter_service import ConverterService
from cardreader.services.data_processor_service import DataProcessorService
from cardreader.services.image_processing_service import ImageProcessingService
from cardreader.services.reader_service import OcrReader, AllowlistOption


class StudentCardReaderService:
    image_file_front: File
    image_file_back: File
    image_front: np.ndarray
    image_back: np.ndarray
    user: User
    cardData: StudentCardData
    reader: OcrReader
    processing_service: ImageProcessingService

    def __init__(self, image_file_front: File, image_file_back: File, user: User= None):
        self.image_file_front = image_file_front
        self.image_file_back = image_file_back
        self.user = user
        self.reader = OcrReader(preprocess=True)
        self.cardData = StudentCardData()
        self.processing_service = ImageProcessingService()
        self.converterService = ConverterService()
        self.dataProcessorService = DataProcessorService()

    def read_data(self):
        self.remove_backgrounds()
        self.read_front()
        self.read_back()
        return self.create_model()

    def remove_backgrounds(self):
        self.image_front = self.processing_service.remove_background(self.converterService.file_to_numpy(self.image_file_front))
        self.image_back = self.processing_service.remove_background(self.converterService.file_to_numpy(self.image_file_back))
        self.image_file_front = self.converterService.numpy_to_file(self.image_front)
        self.image_file_back = self.converterService.numpy_to_file(self.image_back)

    def read_front(self):
        self.read_name()
        self.read_birth_date_and_place()
        self.read_OM()
        self.read_card_number()

    def read_back(self):
        self.read_issue_date()
        self.read_expiry_year()
        self.read_school()
        self.read_address()
        self.read_sticker()

    def create_model(self) -> StudentCard:
        return StudentCard(
            user=self.user,
            imageFront=self.image_file_front,
            imageBack=self.image_file_back,
            name=self.cardData.name,
            birthDate=self.cardData.birth_date,
            issueDate=self.cardData.issue_date,
            expiryDate=self.cardData.expiry_sticker,
            school=self.cardData.school,
            address=self.cardData.address,
            OMNUmber=self.cardData.OM_number,
            cardNumber=self.cardData.card_number,
            placeOfBirth=self.cardData.place_of_birth,
        )

    # def read_name(self):
    #     image = self.processing_service.crop_image(self.image_front, (0.2, 0.4), (0.26, 0.65))
    #     #image = self.processing_service.preprocess_image(image, ksize=9, treshold=70)
    #     result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.UPPERCASE_HUNGARIAN)
    #     self.cardData.name = self.dataProcessorService.process_name(result)
    #     print(result)

    def read_name(self):
        cropped_image = self.processing_service.crop_image(self.image_front, (0.2, 0.4), (0.26, 0.65))
        name = ''
        treshold = 70
        processed_image = []
        result = []
        while (name == '' or name is None) and treshold < 150:
            processed_image = self.processing_service.preprocess_image(cropped_image, ksize=9, treshold=treshold)
            result = self.reader.read(processed_image, allowlist_key=AllowlistOption.UPPERCASE_HUNGARIAN)
            name = self.dataProcessorService.process_name(result)
            treshold = treshold + 20
        self.processing_service.imshow(processed_image)
        self.cardData.name = name
        print(result)

    def read_birth_date_and_place(self):
        cropped_image = self.processing_service.crop_image(self.image_front, (0.40, 0.52), (0.25, 0.67))
        birthdate = ''
        treshold = 55
        processed_image=[]
        result = []
        while (birthdate == '' or birthdate is None) and treshold < 150:
            processed_image = self.processing_service.preprocess_image(cropped_image, ksize=9, treshold=treshold)
            result = self.reader.read(processed_image, allowlist_key=AllowlistOption.DATES)
            birthdate = self.dataProcessorService.process_date(result)
            treshold += 10
        self.processing_service.imshow(processed_image)
        self.cardData.birth_date = birthdate
        print(result)

        image = self.processing_service.crop_image(self.image_front, (0.45, 0.55), (0.27, 0.7))
        image = self.processing_service.preprocess_image(image, ksize=9, treshold=treshold)
        result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.UPPERCASE_HUNGARIAN)
        self.cardData.place_of_birth = self.dataProcessorService.process_birthplace(result)
        print(result)


    def read_OM(self):
        cropped_image = self.processing_service.crop_image(self.image_front, (0.63, 0.8), (0.27, 0.6))
        result = []
        om_number = ''
        processed_image=[]
        treshold = 60
        while om_number == '' or om_number is None and treshold < 150:
            processed_image = self.processing_service.preprocess_image(cropped_image, ksize=9, treshold=treshold)
            result = self.reader.read(processed_image, allowlist_key=AllowlistOption.NUMBERS_ONLY)
            om_number = self.dataProcessorService.process_numeric_identifier(result, '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
            treshold += 10
        self.processing_service.imshow(processed_image)
        self.cardData.OM_number= om_number
        print(result)

    def read_card_number(self):
        image = self.processing_service.crop_image(self.image_front, (0.0, 0.2), (0.63, 1.0))
        image = self.processing_service.preprocess_image(image, ksize=5, treshold=100)
        result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.NUMBERS_ONLY)
        self.cardData.card_number = self.dataProcessorService.process_numeric_identifier(result, '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
        print(result)

    def read_address(self):
        cropped_image = self.processing_service.crop_image(self.image_back, (0.593, 0.72), (0.05, 0.6))
        treshold = 60
        result = []
        address = ''
        processed_image =[]
        while address == '' and treshold < 150:
            processed_image = self.processing_service.preprocess_image(cropped_image, ksize=9, treshold=treshold)
            result = self.reader.read(processed_image, allowlist_key=AllowlistOption.HUNGARIAN_ALPHANUMERIC)
            address = self.dataProcessorService.process_address(result)
            treshold = treshold + 10
        self.processing_service.imshow(processed_image)
        self.cardData.address = address
        print(result)

    def read_issue_date(self):
        cropped_image = self.processing_service.crop_image(self.image_back, (0.15, 0.28), (0.48, 0.71))
        treshold = 55
        result = []
        issue_date = ''
        processed_image =[]
        while issue_date == '' or issue_date is None and treshold<150:
            processed_image = self.processing_service.preprocess_image(cropped_image, ksize=11, treshold=treshold)
            result = self.reader.read(processed_image, allowlist_key=AllowlistOption.DATES)
            issue_date = self.dataProcessorService.process_date(result, accuracy_treshold=0.25)
            treshold = treshold + 10
        self.processing_service.imshow(processed_image)
        self.cardData.issue_date = issue_date
        print(result)

    def read_expiry_year(self):
        image = self.processing_service.crop_image(self.image_back, (0.28, 0.4), (0.48, 0.68))
        image = self.processing_service.preprocess_image(image, ksize=7, treshold=65)
        result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.NUMBERS_ONLY)
        self.cardData.expiry_year = self.dataProcessorService.process_year(result)
        print(result)

    def read_school(self):
        image = self.processing_service.crop_image(self.image_back, (0.43, 0.54), (0.0, 0.8))
        image = self.processing_service.preprocess_image(image, ksize=7, treshold=120, otsu=True)
        result = self.reader.read(image, show_image=True)
        self.cardData.school = self.dataProcessorService.process_school(result)
        print(result)

    def read_sticker(self):
        image = self.processing_service.crop_image(self.image_back, (0.69, 0.95), (0.75, 1))
        #image = self.processing_service.preprocess_image(image, ksize=9, treshold=80)
        result = self.reader.read(image, show_image=True)
        self.cardData.expiry_sticker = self.dataProcessorService.process_sticker(result)
        print(result)