import os
import pickle

def save_directory_structure(path, output_file):
    def get_file_info(file_path):
        stat_info = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'is_file': os.path.isfile(file_path),
            'is_dir': os.path.isdir(file_path),
            'size': stat_info.st_size,
            'created': stat_info.st_ctime,
            'modified': stat_info.st_mtime,
            'accessed': stat_info.st_atime,
            'content': open(file_path, 'rb').read() if os.path.isfile(file_path) else None
        }

    def traverse_directory(directory):
        structure = {}
        for root, dirs, files in os.walk(directory):
            relative_path = os.path.relpath(root, directory)
            if relative_path == '.':
                relative_path = ''
            structure[relative_path] = {
                'dirs': [get_file_info(os.path.join(root, d)) for d in dirs],
                'files': [get_file_info(os.path.join(root, f)) for f in files]
            }
        return structure

    if os.path.isdir(path):
        structure = traverse_directory(path)
    elif os.path.isfile(path):
        structure = {
            '': {
                'dirs': [],
                'files': [get_file_info(path)]
            }
        }
    else:
        raise ValueError("Path must be a directory or a file")

    with open(output_file, 'wb') as f:
        pickle.dump((os.path.basename(path), structure), f)

def restore_directory_structure(input_file, output_path):
    with open(input_file, 'rb') as f:
        top_level_name, structure = pickle.load(f)

    def create_file(file_info, base_path):
        file_path = os.path.join(base_path, file_info['name'])
        with open(file_path, 'wb') as f:
            f.write(file_info['content'])
        os.utime(file_path, (file_info['accessed'], file_info['modified']))

    def create_directory(dir_info, base_path):
        dir_path = os.path.join(base_path, dir_info['name'])
        os.makedirs(dir_path, exist_ok=True)

    def restore_structure(structure, base_path):
        for relative_path, content in structure.items():
            current_path = os.path.join(base_path, relative_path)
            os.makedirs(current_path, exist_ok=True)
            for dir_info in content['dirs']:
                create_directory(dir_info, current_path)
            for file_info in content['files']:
                create_file(file_info, current_path)

    def get_unique_name(name, base_path):
        unique_name = name
        if os.path.exists(os.path.join(base_path, unique_name)):
            unique_name = f"{os.path.splitext(unique_name)[0]}_lzma_decompressed{os.path.splitext(unique_name)[1]}"
        return unique_name

    # Проверяем, является ли верхний уровень директорией или файлом
    if structure['']['dirs'] or len(structure['']['files']) > 1:
        # Если это директория или содержит несколько файлов
        top_level_name = get_unique_name(top_level_name, output_path)
        top_level_path = os.path.join(output_path, top_level_name)
        os.makedirs(top_level_path, exist_ok=True)
        restore_structure(structure, top_level_path)
    else:
        # Если это отдельный файл
        file_info = structure['']['files'][0]
        file_name = get_unique_name(file_info['name'], output_path)

        file_path = os.path.join(output_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(file_info['content'])
        #os.utime(file_path, (file_info['accessed'], file_info['modified']))
