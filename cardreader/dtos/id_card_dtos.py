from array import array


class MrzData:
    name: str
    birthdate: str
    identifier: str
    expiry: str
    sex: str

class IdCardData:
    name: str
    sex: str
    nationality: str
    birthDate: str
    expiryDate: str
    identifier: str
    can: str
    mothers_name: str
    identifier_back: str
    birthplace: str
    mrz: MrzData
    errors: list
    def __init__(self):
        self.errors = []
