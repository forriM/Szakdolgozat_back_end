import numpy as np
from django.core.files import File
from easyocr import Reader

from cardreader.dtos.id_card_dtos import IdCardData
from cardreader.models import User, IdCard
from cardreader.services.converter_service import ConverterService
from cardreader.services.data_processor_service import DataProcessorService
from cardreader.services.idcard_validator_service import IdCardValidatorService
from cardreader.services.image_processing_service import ImageProcessingService
from cardreader.services.reader_service import OcrReader, AllowlistOption


class IdCardReaderService:
    image_file_front: File
    image_file_back: File
    image_front: np.ndarray
    image_back: np.ndarray
    user: User
    cardData: IdCardData
    reader: OcrReader
    image_processing_service: ImageProcessingService

    def __init__(self, image_file_front: File, image_file_back: File, user: User=None):
        self.image_file_front = image_file_front
        self.image_file_back = image_file_back
        self.user = user
        self.reader = OcrReader()
        self.cardData = IdCardData()
        self.converterService = ConverterService()
        self.image_processing_service = ImageProcessingService()
        self.dataProcessorService = DataProcessorService()

    def read_data(self):
        self.remove_backgrounds()
        self.read_front()
        self.read_back()
        self.cardData = IdCardValidatorService(self.cardData).validate()
        return self.create_model()


    def remove_backgrounds(self):
        self.image_front = self.image_processing_service.remove_background(self.converterService.file_to_numpy(self.image_file_front))
        self.image_back = self.image_processing_service.remove_background(self.converterService.file_to_numpy(self.image_file_back))
        self.image_file_front = self.converterService.numpy_to_file(self.image_front)
        self.image_file_back = self.converterService.numpy_to_file(self.image_back)

    def read_front(self):
        self.read_name()
        self.read_sex()
        self.read_nationality()
        self.read_birth()
        self.read_expiry()
        self.read_identifier()
        self.read_can()

    def read_back(self):
        self.read_mothers_name()
        self.read_identifier_back()
        self.read_birthplace()
        self.read_mrz()

    def read_name(self):
        image = self.image_processing_service.crop_image(self.image_front, (0.23, 0.3757), (0.3437, 0.7936))
        #image = self.image_processing_service.preprocess_image(image, 7, 80)
        result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.UPPERCASE_HUNGARIAN)
        print(result)
        self.cardData.name = self.dataProcessorService.process_name(result)

    def read_sex(self):
        image = self.image_processing_service.crop_image(self.image_front, (0.4208, 0.5109), (0.4594, 0.6483))
        result = self.reader.read(image)
        self.cardData.sex = self.dataProcessorService.process_sex(result)

    def read_nationality(self):
        image = self.image_processing_service.crop_image(self.image_front, (0.4208, 0.4909), (0.8928, 1.0))
        result = self.reader.read(image)
        self.cardData.nationality = self.dataProcessorService.process_nationality(result)

    def read_birth(self):
        image = self.image_processing_service.crop_image(self.image_front, (0.4709, 0.5511), (0.6944, 1.0))
        result = self.reader.read(image, show_image=True)
        print(result)
        self.cardData.birthDate = self.dataProcessorService.process_date(result, remove_spaces=True)

    def read_expiry(self):
        image = self.image_processing_service.crop_image(self.image_front, (0.5260, 0.6012), (0.6944, 1.0))
        result = self.reader.read(image, show_image=True)
        print(result)
        self.cardData.expiryDate = self.dataProcessorService.process_date(result, remove_spaces=True)

    def read_identifier(self):
        image = self.image_processing_service.crop_image(self.image_front, (0.5661, 0.6663), (0.6944, 1.0))
        result = self.reader.read(image)
        self.cardData.identifier = self.dataProcessorService.process_ID_number(result)

    def read_can(self):
        image = self.image_processing_service.crop_image(self.image_front, (0.6262, 0.7515), (0.4298, 0.6779))
        result = self.reader.read(image)
        self.cardData.can = self.dataProcessorService.process_numeric_identifier(result, '[0-9][0-9][0-9][0-9][0-9][0-9]')

    def create_model(self) -> IdCard:
        print(self.cardData)
        return IdCard(
            name=self.cardData.name,
            sex=self.cardData.sex,
            nationality=self.cardData.nationality,
            birthDate=self.cardData.birthDate,
            expiryDate=self.cardData.expiryDate,
            identifier=self.cardData.identifier,
            can=self.cardData.can,
            mothersName=self.cardData.mothers_name,
            birthPlace = self.cardData.birthplace,
            user=self.user,
            imageFront=self.image_file_front,
            imageBack=self.image_file_back,
        )

    def read_mothers_name(self):
        image = self.image_processing_service.crop_image(self.image_back, (0.39, 0.47), (0.0, 0.394))
        result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.UPPERCASE_HUNGARIAN)
        self.cardData.mothers_name = self.dataProcessorService.process_name(result)

    def read_birthplace(self):
        image = self.image_processing_service.crop_image(self.image_back, (0.09, 0.19), (0.0, 0.394))
        result = self.reader.read(image, show_image=True, allowlist_key=AllowlistOption.BIRTHPLACE)
        self.cardData.birthplace = self.dataProcessorService.process_birthplace(result)

    def read_mrz(self):
        image = self.image_processing_service.crop_image(self.image_back, (0.6154, 1.0), (0.0, 1.0))
        result = self.reader.read(image)
        self.cardData.mrz = self.dataProcessorService.process_mrz(result)

    def read_identifier_back(self):
        image = self.image_processing_service.crop_image(self.image_back, (0.3022, 0.4561), (0.6626, 1.0))
        result = self.reader.read(image)
        self.cardData.identifier_back = self.dataProcessorService.process_ID_number(result)