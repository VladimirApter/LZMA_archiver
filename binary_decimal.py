from decimal import Decimal, getcontext
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
        return binary_decimal._to_decimal()

    @staticmethod
    def _get_precision(decimal_number):
        decimal_str = str(decimal_number)
        if '.' in decimal_str:
            return len(decimal_str.split('.')[1])
        else:
            return 0

    @staticmethod
    def _decimal_to_binary_bytes(decimal_number, precision):
        integer_number = int(decimal_number * (10 ** precision))
        binary_str = bin(integer_number)[2:]  # Убираем префикс '0b'
        while len(binary_str) % 8 != 0:
            binary_str = '0' + binary_str
        binary_bytes = bytes(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
        return binary_bytes

    def _to_decimal(self):
        binary_str = ''.join(format(byte, '08b') for byte in self.binary_bytes)
        integer_number = int(binary_str, 2)
        decimal_number = Decimal(integer_number) / (10 ** self.precision)
        return decimal_number
