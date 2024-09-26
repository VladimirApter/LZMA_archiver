import os
from time import time

from lz77 import LZ77

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
