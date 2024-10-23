from decimal import Decimal
import pickle

class BinaryDecimal:
    def __init__(self, binary_bytes, precision):
        self.binary_bytes = binary_bytes
        self.precision = precision

    @staticmethod
    def serialize_decimal(decimal_number):
        precision = BinaryDecimal._get_precision(decimal_number)
        binary_bytes = BinaryDecimal._decimal_to_binary_bytes(decimal_number, precision)
        binary_decimal = BinaryDecimal(binary_bytes, precision)
        return pickle.dumps(binary_decimal)

    @staticmethod
    def deserialize_decimal(data):
        binary_decimal = pickle.loads(data)
        return BinaryDecimal._to_decimal(binary_decimal.binary_bytes, binary_decimal.precision)

    @staticmethod
    def _get_precision(decimal_number):
        decimal_str = str(decimal_number)
        if 'E' in decimal_str:
            decimal_str = format(decimal_number, 'f')
        if '.' in decimal_str:
            integer_part, fractional_part = decimal_str.split('.')
            return len(fractional_part)
        else:
            return 0

    @staticmethod
    def _decimal_to_binary_bytes(decimal_number, precision):
        integer_number = int(decimal_number * (10 ** precision))
        binary_bytes = integer_number.to_bytes((integer_number.bit_length() + 7) // 8, byteorder='big')
        return binary_bytes

    @staticmethod
    def _to_decimal(binary_bytes, precision):
        integer_number = int.from_bytes(binary_bytes, byteorder='big')
        decimal_number = Decimal(integer_number) / (10 ** precision)
        return decimal_number
