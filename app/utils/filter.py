import os
import re


def create_bpf_filter(ports):
    return " or ".join([f"tcp port {port}" for port in ports])


def rename_traffic_dump(file_path):
    directory, file_name = os.path.split(file_path)
    base_name, extension = os.path.splitext(file_name)

    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return

    files = os.listdir(directory)
    regex = re.compile(rf"{re.escape(base_name)}_(\d+){re.escape(extension)}$")

    max_number = 0
    for file in files:
        match = regex.match(file)
        if match:
            max_number = max(max_number, int(match.group(1)))

    new_file_name = f"{base_name}_{max_number + 1}{extension}"
    new_file_path = os.path.join(directory, new_file_name)
    os.rename(file_path, new_file_path)
    print(f"Файл {file_path} переименован в {new_file_path}.")
