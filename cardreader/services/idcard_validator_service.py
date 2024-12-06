from cardreader.dtos.id_card_dtos import IdCardData


class IdCardValidatorService:
    cardData: IdCardData
    def __init__(self, cardData: IdCardData):
        self.cardData = cardData

    def validate(self):
        self.__validate_identifier()
        self.__validate_birth()
        self.__validate_expiriy()
        self.__validate_sex()
        return self.cardData

    def __validate_identifier(self):
        if self.cardData.identifier == '':
            self.cardData.errors.append("Igazolványszám leolvasása nem sikerült")
        elif not self.cardData.identifier == self.cardData.identifier_back == self.cardData.mrz.identifier:
            self.cardData.errors.append("A hátlapról és az előlapról leolvasott igazolványszám nem egyezik")

    def __validate_birth(self):
        if self.cardData.birthDate == '':
            self.cardData.errors.append("Születési dátum leolvasása nem sikerült")
        elif not self.cardData.identifier == self.cardData.identifier_back == self.cardData.mrz.identifier:
            self.cardData.errors.append("A hátlapról és az előlapról leolvasott születési dátum nem egyezik")


    def __validate_expiriy(self):
        if self.cardData.birthDate == '':
            self.cardData.errors.append("Lejárati dátum leolvasása nem sikerült")
        elif not self.cardData.identifier == self.cardData.identifier_back == self.cardData.mrz.identifier:
            self.cardData.errors.append("A hátlapról és az előlapról leolvasott lejárati dátum nem egyezik")

    def __validate_sex(self):
        if self.cardData.birthDate == '':
            self.cardData.errors.append("Nem leolvasása nem sikerült")
        elif not self.cardData.identifier == self.cardData.identifier_back == self.cardData.mrz.identifier:
            self.cardData.errors.append("A hátlapról és az előlapról leolvasott nem nem egyezik")


