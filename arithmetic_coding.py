import pickle
from decimal import *

from bd import BDec
from ed import ED
from quality import Quality

TEMP_ENCODED_VALUE_ACCURACY = 10
INTERVALS_DICT_ACCURACY = 10


class ArithmeticCoding:
    intervals_dict = None
    intervals_dict_keys = None
    intervals_dict_len = None

    def __init__(self, quality):
        self.quality = quality

    def encode(self, input_file_path, output_file_path):
        with open(output_file_path, 'w') as _:
            pass  # clean file for encoded data

        with open(output_file_path, 'ab') as output_file:
            pickle.dump(self.quality, output_file)

        read_part_size = 0
        if self.quality == Quality.low:
            read_part_size = 1000
        if self.quality == Quality.medium:
            read_part_size = 2500
        if self.quality == Quality.high:
            read_part_size = 10000

        self.intervals_dict = self._get_intervals_dict(input_file_path, read_part_size)
        self.intervals_dict_keys = list(self.intervals_dict.keys())

        with open(output_file_path, 'ab') as output_file:
            compressed_dict = self._get_str_dict(self.intervals_dict)
            pickle.dump(compressed_dict, output_file)
            pickle.dump(max(TEMP_ENCODED_VALUE_ACCURACY, 1), output_file)

        getcontext().prec = max(TEMP_ENCODED_VALUE_ACCURACY, 1)

        offset = 0
        while True:
            low = Decimal(0)
            high = Decimal(1)

            with open(input_file_path, 'rb') as input_file:
                input_file.seek(offset)

                bytes_str = input_file.read(read_part_size)
                if not bytes_str:
                    break
                for byte_str in bytes_str:
                    byte = byte_str.to_bytes(1, byteorder='big')
                    low, high = self._get_new_low_high(low, high, byte)

            v = self._find_minimal_decimal(low, high)
            b = BDec.serialize_decimal(v)

            d = ED(len(bytes_str), b)

            with open(output_file_path, 'ab') as output_file:
                pickle.dump(d, output_file)

            offset += read_part_size

    @staticmethod
    def _get_intervals_dict(input_file_path, read_part_size):
        def get_min_value(probability_dict):
            min_value = next(iter(probability_dict.values()))

            for value in probability_dict.values():
                if value < min_value:
                    min_value = value

            return min_value

        def get_min_accuracy(decimal):
            decimal_str = str(decimal)
            dot_index = decimal_str.find('.')
            if dot_index == -1:
                return 0

            for i in range(dot_index + 1, len(decimal_str)):
                if decimal_str[i] != '0':
                    return i - dot_index + 1

            return len(decimal_str) - dot_index

        bytes_count = 0
        frequency = {}
        with open(input_file_path, 'rb') as input_file:
            while True:
                byte = input_file.read(1)
                if not byte:
                    break

                if byte not in frequency:
                    frequency[byte] = 1
                else:
                    frequency[byte] += 1

                bytes_count += 1

        getcontext().prec = 15
        probability = {}
        for byte in frequency.keys():
            probability[byte] = Decimal(frequency[byte]) / bytes_count

        min_probability = get_min_value(probability)
        min_accuracy = get_min_accuracy(min_probability)

        global TEMP_ENCODED_VALUE_ACCURACY
        TEMP_ENCODED_VALUE_ACCURACY = min_accuracy * read_part_size + 150

        global INTERVALS_DICT_ACCURACY
        INTERVALS_DICT_ACCURACY = min_accuracy

        getcontext().prec = INTERVALS_DICT_ACCURACY

        intervals_dict = {}
        last_high = Decimal(0)
        for byte in probability.keys():
            last_high += Decimal(probability[byte])
            intervals_dict[byte] = last_high

        intervals_dict[list(intervals_dict.keys())[-1]] = Decimal(1)  # this is elimination of float numbers error
        return intervals_dict

    @staticmethod
    def _get_str_dict(decimal_dict):
        str_dict = {}
        for key in decimal_dict.keys():
            interval = decimal_dict[key]
            str_interval = interval.to_eng_string()
            if '.' in str_interval:
                str_interval = str_interval.split('.')[1]
            str_dict[key] = str_interval
        return str_dict

    @staticmethod
    def _get_decimal_dict(str_dict):
        decimal_dict = {}
        for key in str_dict.keys():
            str_interval = str_dict[key]
            if str_interval != '1':
                str_interval = f'0.{str_interval}'
            decimal_dict[key] = Decimal(str_interval)
        return decimal_dict

    def _get_new_low_high(self, low, high, byte):
        byte_low, byte_high = self._get_byte_low_high(byte)

        current_range = (high - low)
        new_low = low + current_range * byte_low
        new_high = low + current_range * byte_high
        return new_low, new_high

    def _get_byte_low_high(self, byte):
        byte_low = 0
        byte_index = self.intervals_dict_keys.index(byte)
        if byte_index != 0:
            byte_low = self.intervals_dict[self.intervals_dict_keys[byte_index - 1]]
        byte_high = self.intervals_dict[byte]

        return byte_low, byte_high

    @staticmethod
    def _find_minimal_decimal(low, high):
        low_decimal_places = abs(low.as_tuple().exponent)
        high_decimal_places = abs(high.as_tuple().exponent)

        max_decimal_places = max(low_decimal_places, high_decimal_places)

        for decimal_places in range(1, max_decimal_places + 1):
            rounded_low = round(low, decimal_places)
            rounded_high = round(high, decimal_places)

            if low < rounded_low < high:
                return rounded_low
            if low < rounded_high < high:
                return rounded_high

        return (low + high) / Decimal(2)

    def decode(self, input_file_path, output_file_path):
        self.intervals_dict, encoded_data_objs = self.deserialize_file(input_file_path)
        self.intervals_dict_keys = list(self.intervals_dict.keys())
        self.intervals_dict_len = len(self.intervals_dict)

        with open(output_file_path, 'w') as _:
            pass  # clean file for encoded data

        for encoded_data in encoded_data_objs:
            encoded_value = BDec.deserialize_decimal(encoded_data.v)
            message_length = encoded_data.ml

            low = Decimal(0)
            high = Decimal(1)

            with open(output_file_path, 'ab') as output_file:
                for _ in range(message_length):
                    low, high, byte = self.decode_binary_search(encoded_value, low, high)
                    output_file.write(byte)

    @staticmethod
    def deserialize_file(file_path):
        objects = []
        with open(file_path, 'rb') as file:
            quality = pickle.load(file)
            str_dict = pickle.load(file)
            intervals_dict = ArithmeticCoding._get_decimal_dict(str_dict)
            getcontext().prec = int(pickle.load(file))
            while True:
                try:
                    obj = pickle.load(file)
                    objects.append(obj)
                except EOFError:
                    break
        return intervals_dict, objects

    def decode_binary_search(self, encoded_value, low, high):
        left, right = 0, self.intervals_dict_len
        while True:
            mid = (right + left) // 2
            byte = self.intervals_dict_keys[mid]
            current_low, current_high = self._get_new_low_high(low, high, byte)

            if current_low <= encoded_value <= current_high:
                return current_low, current_high, byte
            elif current_low > encoded_value:
                right = mid - 1
            elif current_high < encoded_value:
                left = mid + 1
