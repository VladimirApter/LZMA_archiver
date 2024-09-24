class LZ77:
    def __init__(self, buffer_size, lookahead_size):
        self.buffer_size = buffer_size
        self.lookahead_size = lookahead_size

        self.unit_separator = ''
        self.group_opener = ''
        self.group_closer = ''

    def compress(self, input_file_path, output_file_path):
        with open(input_file_path, 'r', encoding='utf-8') as input_file, \
                open(output_file_path, 'w', encoding='utf-8') as output_file:
            buffer = []
            lookahead = [c for c in input_file.read(self.lookahead_size)]

            while True:
                current_lookahead_len = len(lookahead)
                if current_lookahead_len == 0:
                    break

                if current_lookahead_len < self.lookahead_size:
                    for c in input_file.read(
                            self.lookahead_size - current_lookahead_len):
                        lookahead.append(c)

                match_offset, match_length, next_char = self._find_max_match(
                    buffer, lookahead)
                if match_length <= 1:
                    output_file.write(lookahead[0])
                    match_length = 1
                else:
                    output_file.write(f'{self.group_opener}'
                                      f'{match_offset}'
                                      f'{self.unit_separator}'
                                      f'{match_length}'
                                      f'{self.unit_separator}'
                                      f'{next_char}'
                                      f'{self.group_closer}')

                if match_length > 1:
                    match_length += 1  # +1 to move next_char to the buffer and remove it from lookahead

                buffer += lookahead[:match_length]
                if len(buffer) > self.buffer_size:
                    buffer = buffer[match_length:]

                lookahead = lookahead[match_length:]

    def _find_max_match(self, buffer, lookahead):
        buffer_len = len(buffer)
        lookahead_len = len(lookahead)

        max_length = 0
        offset = 0
        next_char = ''

        for i in range(len(buffer)):
            length = 0
            while i + length < buffer_len and length < lookahead_len and \
                    buffer[i + length] == lookahead[length]:
                length += 1

            if length > max_length:
                max_length = length
                offset = buffer_len - i
                next_char = lookahead[length] if length < lookahead_len else ''

        return offset, max_length, next_char

    def decompress(self, input_file_path, output_file_path):
        with open(input_file_path, 'r', encoding='utf-8') as input_file, \
                open(output_file_path, 'w', encoding='utf-8') as output_file:
            buffer = []

            while True:
                char = input_file.read(1)
                if not char:
                    break

                if char == self.group_opener:
                    match_str = ''
                    while char != self.group_closer:
                        char = input_file.read(1)
                        if not char:
                            raise ValueError(
                                "Invalid format in compressed file")
                        match_str += char

                    match_str = match_str[:-1]  # remove second group_separator
                    match_parts = match_str.split(self.unit_separator)
                    if len(match_parts) != 3:
                        raise ValueError("Invalid format in compressed file")

                    offset = int(match_parts[0])
                    length = int(match_parts[1])
                    next_char = match_parts[2]

                    start = len(buffer) - offset
                    for i in range(length):
                        buffer.append(buffer[start + i])
                    buffer.append(next_char)
                else:
                    buffer.append(char)

                while len(buffer) > self.buffer_size:
                    output_file.write(buffer.pop(0))

            output_file.write(''.join(buffer))


lz77 = LZ77(4096, 18)
lz77.compress('input.txt', 'output.txt')
lz77.decompress('output.txt', 'decompressed.txt')
