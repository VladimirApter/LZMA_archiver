import os
from time import time

from lz77 import LZ77
from delta_coding import Delta

input_file = 'input.txt'
decompressed_file = 'decompressed.txt'

input_file_size = os.path.getsize(input_file)


start_lz77_compress = time()
lz77 = LZ77(4096, 32)
lz77.compress(input_file, 'LZ77compressed.bin')
finish_lz77_compress = time()
lz77_compressed_file_size = os.path.getsize('LZ77compressed.bin')
start_lz77_decompress = time()
lz77.decompress('LZ77compressed.bin', decompressed_file)
finish_lz77_decompress = time()

print(f'lz77:\n'
      f'    input file size - {input_file_size}\n'
      f'    compressed file size - {lz77_compressed_file_size}\n'
      f'    compress time - {finish_lz77_compress - start_lz77_compress}\n'
      f'    decompress time - {finish_lz77_decompress - start_lz77_decompress}\n\n')


'''start_delta_lz77_compress = time()
Delta.encode(input_file, 'delta_encoded.bin')
lz77 = LZ77(4096, 32)
lz77.compress('delta_encoded.bin', 'LZ77compressed.bin')
finish_delta_lz77_compress = time()
delta_lz77_compressed_file_size = os.path.getsize('LZ77compressed.bin')
start_delta_lz77_decompress = time()
lz77.decompress('LZ77compressed.bin', 'LZ77decompressed.bin')
Delta.encode('LZ77decompressed.bin', decompressed_file)
finish_delta_lz77_decompress = time()

print(f'delta + lz77:\n'
      f'    input file size - {input_file_size}\n'
      f'    compressed file size - {delta_lz77_compressed_file_size}\n'
      f'    compress time {finish_delta_lz77_compress - start_delta_lz77_compress}\n'
      f'    decompress time {finish_delta_lz77_decompress - start_delta_lz77_decompress}\n\n')'''
