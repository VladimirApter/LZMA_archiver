import unittest
import os
import tempfile
from combine import combine_compress, combine_decompress
from quality import Quality


class TestCompressionFunctions(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.test_dir.name, 'test_file.txt')
        self.test_file_content = 'This is a test file.'

        with open(self.test_file_path, 'w') as f:
            f.write(self.test_file_content)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_compress_and_decompress(self):
        compressed_file_path = self.test_file_path + '.lzma'

        combine_compress(self.test_file_path, Quality.high)
        self.assertTrue(os.path.exists(compressed_file_path))

        decompressed_file_name = combine_decompress(compressed_file_path)
        decompressed_file_path = os.path.join(os.path.dirname(self.test_file_path), decompressed_file_name)
        self.assertTrue(os.path.exists(decompressed_file_path))

        with open(decompressed_file_path, 'r') as f:
            decompressed_content = f.read()
        self.assertEqual(decompressed_content, self.test_file_content)

    def test_compress_nonexistent_file(self):
        nonexistent_file_path = os.path.join(self.test_dir.name, 'nonexistent_file.txt')
        with self.assertRaises(ValueError):
            combine_compress(nonexistent_file_path, Quality.high)

    def test_decompress_corrupted_file(self):
        corrupted_file_path = os.path.join(self.test_dir.name, 'corrupted_file.lzma')
        with open(corrupted_file_path, 'w') as f:
            f.write('This is a corrupted file.')

        with self.assertRaises(ValueError):
            combine_decompress(corrupted_file_path)

    def test_compress_and_decompress_binary_files(self):
        sizes = [255, 256, 257]

        for size in sizes:
            binary_file_path = os.path.join(self.test_dir.name, f'binary_file_{size}.bin')
            binary_data = b"0" * size

            with open(binary_file_path, 'wb') as f:
                f.write(binary_data)

            compressed_file_path = binary_file_path + '.lzma'

            combine_compress(binary_file_path, Quality.high)
            self.assertTrue(os.path.exists(compressed_file_path))

            decompressed_file_name = combine_decompress(compressed_file_path)
            decompressed_file_path = os.path.join(os.path.dirname(binary_file_path), decompressed_file_name)
            self.assertTrue(os.path.exists(decompressed_file_path))

            with open(decompressed_file_path, 'rb') as f:
                decompressed_content = f.read()
            self.assertEqual(decompressed_content, binary_data)


if __name__ == '__main__':
    unittest.main()
