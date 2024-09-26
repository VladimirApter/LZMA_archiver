class Delta:
    @staticmethod
    def encode(input_file_path, output_file_path):
        Delta._process_bytes(input_file_path, output_file_path, mode='encode')

    @staticmethod
    def decode(input_file_path, output_file_path):
        Delta._process_bytes(input_file_path, output_file_path, mode='decode')

    @staticmethod
    def _process_bytes(input_file_path, output_file_path, mode):
        with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
            prev_byte = None
            while True:
                byte = input_file.read(1)
                if not byte:
                    break
                if prev_byte is None:
                    output_file.write(byte)
                else:
                    data_to_write = None
                    if mode == 'encode':
                        data_to_write = (byte[0] - prev_byte) % 256
                    elif mode == 'decode':
                        data_to_write = (prev_byte + byte[0]) % 256

                    output_file.write(data_to_write.to_bytes(1, byteorder='big'))
                prev_byte = byte[0] if prev_byte is None \
                    else(byte[0] if mode == 'encode' else data_to_write)
