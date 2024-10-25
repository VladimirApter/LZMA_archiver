from combine import *
from quality import Quality

file = r"C:\Users\admin\Desktop\spaceway code.txt"
file_name = file.split('.')[0]

combine_compress(file, Quality.high)
combine_decompress(f"{file_name}.lzma")
