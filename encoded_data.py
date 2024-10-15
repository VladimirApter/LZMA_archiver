from decimal import Decimal


class EncodedData:
    def __init__(self, message_length, value):
        self.message_length = message_length
        self.value = value
