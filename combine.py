import hashlib
import os

from lz77 import LZ77
from arithmetic_coding import ArithmeticCoding
from metadata_work import *


def append_checksum(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()

    checksum = hashlib.md5(data).digest()

    with open(file_path, 'ab') as file:
        file.write(checksum)


def verify_checksum(file_path, output_file_path):
    with open(file_path, 'rb') as file:
        data = file.read()

    checksum_length = hashlib.md5().digest_size
    file_data = data[:-checksum_length]
    stored_checksum = data[-checksum_length:]
    calculated_checksum = hashlib.md5(file_data).digest()
    is_valid = stored_checksum == calculated_checksum

    if is_valid:
        with open(output_file_path, 'wb') as file:
            file.write(file_data)

    return is_valid


def calculate_compression_percentage(original_path, compressed_path):
    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)

    compression_percentage = (1 - (compressed_size / original_size)) * 100
    return compression_percentage


def combine_compress(input_path, quality):
    directory = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)
    output_file_path = os.path.join(directory, f'{input_file_name}.lzma')

    temp_file1 = f'{input_file_name}_tmp1.bin'
    temp_file2 = f'{input_file_name}_tmp2.bin'

    save_directory_structure(input_path, temp_file1)

    lz77_coder = LZ77(quality)
    lz77_coder.compress(temp_file1, temp_file2)

    arithmetic_coder = ArithmeticCoding(quality)
    arithmetic_coder.encode(temp_file2, output_file_path)

    append_checksum(output_file_path)

    print(f'Исходныые данные сжаты на {calculate_compression_percentage(temp_file1, output_file_path):.2f}%')

    os.remove(temp_file1)
    os.remove(temp_file2)


def combine_decompress(input_file_path):
    directory = os.path.dirname(input_file_path)
    input_name = os.path.basename(input_file_path).split('.')[0]

    temp_file3 = f'{input_name}_tmp3.bin'
    if not verify_checksum(input_file_path, temp_file3):
        raise ValueError

    input_file_path = temp_file3
    with open(input_file_path, 'rb') as file:
        quality = pickle.load(file)

    temp_file1 = f'{input_name}_tmp1.bin'
    temp_file2 = f'{input_name}_tmp2.bin'

    arithmetic_coder = ArithmeticCoding(quality)
    arithmetic_coder.decode(input_file_path, temp_file1)

    lz77_coder = LZ77(quality)
    lz77_coder.decompress(temp_file1, temp_file2)

    result_name = restore_directory_structure(temp_file2, directory)

    os.remove(temp_file1)
    os.remove(temp_file2)
    os.remove(temp_file3)

    return result_name