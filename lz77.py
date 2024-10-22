from quality import Quality


class LZ77:
    def __init__(self, quality):
        if quality == Quality.low:
            self.buffer_size = 1024
            self.lookahead_size = 12
        if quality == Quality.medium:
            self.buffer_size = 2048
            self.lookahead_size = 12
        if quality == Quality.high:
            self.buffer_size = 4096
            self.lookahead_size = 16

    def compress(self, input_file_path, output_file_path):
        with open(input_file_path, 'rb') as input_file, \
                open(output_file_path, 'wb') as output_file:
            buffer = bytearray()
            lookahead = bytearray(input_file.read(self.lookahead_size))

            while True:
                match_offset, match_length, next_byte = self._find_max_match(buffer, lookahead)

                data_to_write = self._get_triple_bytes(match_offset, match_length, next_byte)
                output_file.write(data_to_write)

                match_length += 1  # +1 to move next_byte to the buffer and remove it from lookahead

                buffer += lookahead[:match_length]
                if len(buffer) > self.buffer_size:
                    buffer = buffer[match_length:]

                lookahead = lookahead[match_length:]

                if len(lookahead) < self.lookahead_size:
                    for c in input_file.read(self.lookahead_size - len(lookahead)):
                        lookahead.append(c)

                if len(lookahead) == 0:
                    break

    @staticmethod
    def _find_max_match(buffer, lookahead):
        buffer_len = len(buffer)
        lookahead_len = len(lookahead)

        max_length = 0
        offset = 0
        next_byte = None
        is_best_match = False

        for i in range(len(buffer)):
            length = 0
            while i + length < buffer_len and length < lookahead_len and \
                    buffer[i + length] == lookahead[length]:
                length += 1

            if length > max_length:
                if length >= lookahead_len:
                    length = lookahead_len - 1
                    is_best_match = True
                max_length = length
                offset = buffer_len - i
                next_byte = lookahead[length].to_bytes()
                if is_best_match:
                    break

        if max_length == 0:
            next_byte = lookahead[0].to_bytes()
        return offset, max_length, next_byte

    def _get_triple_bytes(self, match_offset, match_length, next_byte):
        result = bytes()
        result += self._int_to_bytes(match_offset)
        result += self._int_to_bytes(match_length)
        result += next_byte
        return result

    def _int_to_bytes(self, number) -> bytes:
        number_bits = self._get_int_bits(number)
        number_bytes = self._get_bytes_from_bits(number_bits)
        return number_bytes

    @staticmethod
    def _get_bytes_from_bits(str_bits) -> bytes:
        if len(str_bits) <= 8:
            return int(str_bits, 2).to_bytes(1, byteorder='big')
        return int(str_bits, 2).to_bytes(2, byteorder='big')

    @staticmethod
    def _get_int_bits(number) -> str:
        if number < 128:
            return f'0{number:07b}'
        return f'1{number:015b}'

    def decompress(self, input_file_path, output_file_path):
        with open(input_file_path, 'rb') as input_file, \
                open(output_file_path, 'wb') as output_file:
            buffer = bytearray()

            while True:
                try:
                    offset, length, next_byte = self._read_triple(input_file)
                except Exception as e:
                    if 'string of length 0 found' in str(e):
                        break
                    else:
                        raise e

                start = len(buffer) - offset
                for i in range(length):
                    buffer.append(buffer[start + i])
                buffer += next_byte

                if len(buffer) > self.buffer_size:
                    buffer_extra_part = buffer[:len(buffer) - self.buffer_size]
                    for byte in buffer_extra_part:
                        self._write_byte(byte, output_file)
                    buffer = buffer[len(buffer) - self.buffer_size:]

            for byte in buffer:
                self._write_byte(byte, output_file)

    def _read_triple(self, file):
        offset = self._read_int(file)
        length = self._read_int(file)
        next_byte = file.read(1)
        return offset, length, next_byte

    @staticmethod
    def _read_int(file):
        first_byte = format(ord(file.read(1)), '08b')
        result = first_byte[1:]
        if first_byte.startswith('1'):
            result += format(ord(file.read(1)), '08b')
        return int(result, 2)

    @staticmethod
    def _write_byte(byte, file):
        byte = byte.to_bytes(1, byteorder='big')
        file.write(byte)
