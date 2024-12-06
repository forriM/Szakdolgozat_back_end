import re
from datetime import datetime
from cardreader.dtos.id_card_dtos import MrzData


class DataProcessorService:
    def process_name(self, result):
        if len(result) == 0:
            return ''
        values = []
        for (bbox, text, prob) in result:
            if prob > 0.5:
                text = text.replace('0', 'O').lower()
                if re.match(r'^[a-záéíóöőúüű\s]+$', text):
                    values.append(text)

        if len(values) > 3:
            return ''
        if len(values) == 1:
            values = values[0].split(' ')

        name = ' '.join(values)
        names = [name.capitalize() for name in name.split(' ')]
        return ' '.join(names) if len(names) > 1 else ''

    def process_sex(self, result):
        values = []
        for (bbox, text, prob) in result:
            values += re.findall('[A-Z]', text)
        if not values:
            return ''

        if 'N' in values:
            return 'female'
        if 'F' in values:
            return 'male'

        sex = values[0]
        return 'male' if sex == 'F' else 'female' if sex == 'N' else ''

    def process_nationality(self, result):
        if len(result) == 0:
            return ''

        for (bbox, text, prob) in result:
            text = text.upper()
            matches = re.findall('[A-Z][A-Z][A-Z]', text)
            if matches:
                return ''.join(matches)
        return ''

    def process_date(self, result, accuracy_threshold=0.5, remove_spaces=False):
        values = []
        month_names_hu = [
            'január', 'február', 'március', 'április', 'május', 'június',
            'július', 'augusztus', 'szeptember', 'október', 'november', 'december'
        ]

        for (bbox, text, prob) in result:
            if prob > accuracy_threshold:
                text = text.replace('O', '0').lower()
                if remove_spaces:
                    text = text.replace(' ', '')
                if text:
                    values.append(text)

        combined_text = ' '.join(values)
        try:
            if '.' in combined_text and len(combined_text.split('.')) >= 3:
                return datetime.strptime(combined_text, '%Y.%m.%d').strftime('%Y-%m-%d')
        except ValueError:
            pass

        for i, month in enumerate(month_names_hu, start=1):
            if month in combined_text:
                combined_text = combined_text.replace(month, f"{i}.").replace(' ', '')
                try:
                    return datetime.strptime(combined_text, '%Y.%m.%d').strftime('%Y-%m-%d')
                except ValueError:
                    pass

        if len(values) == 3 and all(v.isnumeric() for v in values):
            year, month, day = (values if len(values[0]) == 4 else values[::-1])
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return None

    def process_ID_number(self, result):
        for (bbox, text, prob) in result:
            text = text.replace('O', '0')
            match = re.findall('[0-9]{6}[A-Z]{2}', text)
            if match:
                return ''.join(match)
        return ''

    def process_numeric_identifier(self, result, pattern):
        idstring = ''.join(text.replace(' ', '').replace('O', '0')
                           for (bbox, text, prob) in result if prob > 0.6 and text.isnumeric())
        matches = re.findall(pattern, idstring)
        return ''.join(matches) if matches else ''

    def process_birthplace(self, result):
        values = [text for (bbox, text, prob) in result if prob > 0.55]
        return ' '.join(values) if values else ''

    def process_sticker(self, result):
        year_pattern = re.compile(r'^\d{2}/\d{2}$')
        date_pattern = re.compile(r'^\d{5}$')
        yearstr, semester, expiry_date = '', 0, None

        for (bbox, text, prob) in result:
            if prob > 0.3:
                if year_pattern.match(text):
                    yearstr = text
                elif date_pattern.match(text) and text[2] == '1':
                    yearstr = f"{text[:2]}/{text[3:]}"
                elif not text.isnumeric() and text[0].isnumeric():
                    semester = int(text[0])

        if yearstr:
            expiry_year = '20' + yearstr.split('/')[1]
            expiry_date = f"{expiry_year}.{'10.31' if semester in {0, 2} else '03.31'}"
            return datetime.strptime(expiry_date, '%Y.%m.%d').strftime('%Y-%m-%d')
        return None

    def process_mrz(self, result):
        values = [text.replace(' ', '') for (bbox, text, prob) in result if prob > 0.25]
        if not values:
            return MrzData()

        mrz_split = re.sub('<{2,}', '<', '<'.join(values)).split('<')
        mrz = MrzData()
        mrz.identifier = mrz_split[1][3:] if len(mrz_split) > 1 else ''
        mrz.birthdate = self.__convert_date_str(mrz_split[3][:6], False) if len(mrz_split) > 3 else ''
        mrz.sex = 'Nő' if len(mrz_split) > 3 and mrz_split[3][7].upper() == 'F' else 'Férfi' if len(mrz_split) > 3 and mrz_split[3][7].upper() == 'M' else ''
        mrz.expiry = self.__convert_date_str(mrz_split[3][8:-4], True) if len(mrz_split) > 3 else ''
        return mrz

    def process_school(self, result):
        return ' '.join(text for (bbox, text, prob) in result if prob > 0.3)

    def process_year(self, result):
        values = [text for (bbox, text, prob) in result if prob > 0.4 and len(text) == 4]
        return ''.join(values)

    def process_address(self, result):
        values = [text for (bbox, text, prob) in result if prob > 0.4]
        address = ' '.join(values)
        return address if address[:4].isnumeric() else ''

    @staticmethod
    def __convert_date_str(date, is_expiry):
        if len(date) != 6 or not all(date[i:i+2].isnumeric() for i in range(0, 6, 2)):
            return ''
        year = int(date[:2]) + (2000 if int(date[:2]) <= int(str(datetime.today().year)[2:]) or is_expiry else 1900)
        return f"{date[4:]}-{date[2:4]}-{year}"
