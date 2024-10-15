import os
import pickle
from decimal import *
from time import time, sleep

from binary_decimal import BinaryDecimal
from encoded_data import EncodedData

TEMP_ENCODED_VALUE_ACCURACY = 10
INTERVALS_DICT_ACCURACY = 10


class ArithmeticCoding:
    intervals_dict = None
    intervals_dict_keys = None
    intervals_dict_len = None

    def encode(self, input_file_path, output_file_path):
        self.intervals_dict = self._get_intervals_dict(input_file_path)
        self.intervals_dict_keys = list(self.intervals_dict.keys())
        input_file_size = os.path.getsize(input_file_path)

        low = Decimal(0)
        high = Decimal(1)

        getcontext().prec = max(TEMP_ENCODED_VALUE_ACCURACY, 1)

        with open(input_file_path, 'rb') as input_file:
            while True:
                byte = input_file.read(1)
                if not byte:
                    break
                low, high = self._get_new_low_high(low, high, byte)

        encoded_value = self._find_minimal_decimal(low, high)
        encoded_bytes = BinaryDecimal.serialize_decimal(encoded_value)
        compressed_dict = EncodedData.get_str_dict(self.intervals_dict)

        encoded_data = EncodedData(input_file_size, compressed_dict, encoded_bytes)

        with open(output_file_path, 'ab') as output_file:
            pickle.dump(encoded_data, output_file)

    @staticmethod
    def _get_intervals_dict(input_file_path):
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
        TEMP_ENCODED_VALUE_ACCURACY = min_accuracy * bytes_count

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
        encoded_data_objs = self.deserialize_objects(input_file_path)

        with open(output_file_path, 'w') as _:
            pass  # clean file for encoded data

        for encoded_data in encoded_data_objs:
            encoded_value = BinaryDecimal.deserialize_decimal(encoded_data.value)
            message_length = encoded_data.message_length
            self.intervals_dict = EncodedData.get_decimal_dict(encoded_data.intervals_dict)
            self.intervals_dict_keys = list(self.intervals_dict.keys())
            self.intervals_dict_len = len(self.intervals_dict)

            low = Decimal(0)
            high = Decimal(1)

            with open(output_file_path, 'ab') as output_file:
                for _ in range(message_length):
                    low, high, byte = self.decode_binary_search(encoded_value, low, high)
                    output_file.write(byte)

    @staticmethod
    def deserialize_objects(file_path):
        objects = []
        with open(file_path, 'rb') as file:
            while True:
                try:
                    obj = pickle.load(file)
                    objects.append(obj)
                except EOFError:
                    break
        return objects

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


input_file = 'ac_test.txt'
encoded_file = 'ac_test_encoded.txt'
decoded_file = 'ac_test_decoded.txt'

with open(encoded_file, 'w') as _:
    pass  # clean file for encoded data

start = time()
coder = ArithmeticCoding()
coder.encode(input_file, encoded_file)
coder.decode(encoded_file, decoded_file)
finish = time()
print(finish - start)
print(f"original: {os.path.getsize(input_file)}\ncompresssed: {os.path.getsize(encoded_file)}")

print()

with open(encoded_file, 'w') as _:
    pass  # clean file for encoded data

input_file1 = 'ac_test1.txt'
input_file2 = 'ac_test2.txt'

start = time()
coder = ArithmeticCoding()
coder.encode(input_file1, encoded_file)
coder.encode(input_file2, encoded_file)
coder.decode(encoded_file, decoded_file)
finish = time()
print(finish - start)
print(f"original: {os.path.getsize(input_file1) + os.path.getsize(input_file2)}\ncompresssed: {os.path.getsize(encoded_file)}")
