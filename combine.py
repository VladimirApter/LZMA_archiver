from lz77 import LZ77
from arithmetic_coding import ArithmeticCoding
from metadata_work import *


def combine_compress(input_path, quality):
    directory = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path).split('.')[0]
    output_file_path = os.path.join(directory, f'{input_file_name}.lzma')

    temp_file1 = f'{input_file_name}_tmp1.bin'
    temp_file2 = f'{input_file_name}_tmp2.bin'

    save_directory_structure(input_path, temp_file1)

    lz77_coder = LZ77(quality)
    lz77_coder.compress(temp_file1, temp_file2)

    arithmetic_coder = ArithmeticCoding(quality)
    arithmetic_coder.encode(temp_file2, output_file_path)

    os.remove(temp_file1)
    os.remove(temp_file2)


def combine_decompress(input_file_path):
    directory = os.path.dirname(input_file_path)
    input_name = os.path.basename(input_file_path).split('.')[0]

    with open(input_file_path, 'rb') as file:
        quality = pickle.load(file)

    temp_file1 = f'{input_name}_tmp1.bin'
    temp_file2 = f'{input_name}_tmp2.bin'

    arithmetic_coder = ArithmeticCoding(quality)
    arithmetic_coder.decode(input_file_path, temp_file1)

    lz77_coder = LZ77(quality)
    lz77_coder.decompress(temp_file1, temp_file2)

    restore_directory_structure(temp_file2, directory)

    os.remove(temp_file1)
    os.remove(temp_file2)
