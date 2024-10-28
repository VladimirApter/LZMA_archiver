from combine import *
from quality import Quality

file = ""
file_name = file.split('.')[0]

combine_compress(file, Quality.high)
combine_decompress(f"{file_name}.lzma")
