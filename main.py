import os
from combine import *
from quality import Quality

def main():
    while True:
        action = input("Выберите действие: сжать (c) или восстановить (r) файлы? (или 'q' для выхода): ").strip().lower()

        if action == 'q':
            print("Выход из программы.")
            break

        if action == 'c':
            quality_input = input("Выберите качество сжатия: низкое (l), среднее (m) или высокое (h): ").strip().lower()
            if quality_input == 'l':
                quality = Quality.low
            elif quality_input == 'm':
                quality = Quality.medium
            elif quality_input == 'h':
                quality = Quality.high
            else:
                print("Неверный выбор качества. Пожалуйста, попробуйте снова.")
                continue

            file_path = input("Укажите полный путь до файла/директории, который необходимо сжать: ").strip()
            if os.path.exists(file_path):
                try:
                    combine_compress(file_path, quality)
                    compressed_file_name = os.path.basename(file_path) + '.lzma'
                    print(f"Сжатый файл сохранен в папку с исходным файлом/директорией: {compressed_file_name}")
                except Exception as e:
                    print(f"Ошибка при сжатии файла: {e}")
            else:
                print("Указанный путь не существует. Пожалуйста, попробуйте снова.")

        elif action == 'r':
            file_path = input("Укажите полный путь до файла, который нужно восстановить: ").strip()
            if not os.path.exists(file_path):
                print("Указанный путь не существует. Пожалуйста, попробуйте снова.")
            if file_path.endswith('.lzma'):
                try:
                    decompressed_file_name = combine_decompress(file_path)
                    print(f"Файл успешно восстановлен в: {decompressed_file_name}")
                except:
                    print("Сжатый файл поврежден и не может быть восстановлен.")
            else:
                print("Файл должен иметь расширение .lzma. Пожалуйста, попробуйте снова.")

        else:
            print("Неверный выбор действия. Пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()
