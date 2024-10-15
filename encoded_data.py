from decimal import Decimal


class EncodedData:
    def __init__(self, message_length, intervals_dict, value):
        self.message_length = message_length
        self.intervals_dict = intervals_dict
        self.value = value

    @staticmethod
    def get_str_dict(decimal_dict):
        str_dict = {}
        for key in decimal_dict.keys():
            interval = decimal_dict[key]
            str_dict[key] = interval.to_eng_string()
        return str_dict

    @staticmethod
    def get_decimal_dict(str_dict):
        decimal_dict = {}
        for key in str_dict.keys():
            decimal_dict[key] = Decimal(str_dict[key])
        return decimal_dict



