import os
import re
import logging
from typing import Tuple

# Code edited for Unicode issue
# Original: https://github.com/d9pouces/RubyMarshal
from rubymarshal.reader import load


def replace_newlines(byte_string):
    if isinstance(byte_string, bytes):
        return byte_string.replace(b"\r\n", b"\n")
    return byte_string


def decode_utf8(byte_string):
    if isinstance(byte_string, bytes):
        return byte_string.decode("utf-8", errors="replace")
    return byte_string


def sanitize_filename(name: str) -> str:
    name = name.replace(" ", "_")
    name = re.sub(r"[\n\r\t]+", "", name)
    name = re.sub(r'[\/:*?"<>|]', "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def script_info(name: str, code: str) -> str:
    lines = [
        f"# encoding: utf-8",
        f"# Name: {name}",
    ]
    lines.extend(code.splitlines())
    return "\n".join(lines)


def process_script(script: Tuple[int, str, bytes]) -> Tuple[str, str]:
    identifier, name, code = script
    if isinstance(code, str):
        code = code.encode("utf-8")
    code = decode_utf8(replace_newlines(code))
    filename = sanitize_filename(name) + ".rb"

    content = script_info(name, code)
    return filename, content


def create_directory_structure(base_dir, name):
    directories = name.split("/")
    current_path = base_dir
    for dir_name in directories:
        current_path = os.path.join(current_path, dir_name.strip())
        os.makedirs(current_path, exist_ok=True)
    return current_path


def extract_scripts(input_file: str, output_dir: str) -> None:
    list_scripts = []

    logging.info(f"Processing file: {input_file}")

    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "rb") as file:
        scripts = load(file)

    current_dir = output_dir
    id_carpeta = 0
    for n, script in enumerate(scripts):
        identifier, name, code = script
        if name:
            folder_marker = "▼" if "▼" in name else "■" if "■" in name else None
            if folder_marker:
                id_carpeta += 1
                name = f"{id_carpeta}_{name.replace(folder_marker, '').strip()}"
                current_dir = (
                    os.path.join(output_dir, sanitize_filename(name))
                    if folder_marker == "▼"
                    else create_directory_structure(output_dir, name)
                )
                os.makedirs(current_dir, exist_ok=True)
            else:
                try:
                    filename, content = process_script(script)
                    output_path = os.path.join(current_dir, f"{n + 1}_{filename}")
                    list_scripts.append(f"{output_path.replace('\\', '/')}\n")

                    print(f"Saving script to: {output_path}")
                    with open(output_path, "w", encoding="utf-8") as file:
                        file.write(content.strip())

                    logging.info(f"Saved script: {filename}")
                except Exception as e:
                    logging.error(f"Failed to process script {name}: {e}")

    logging.info(f"Total scripts processed: {len(scripts)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    input_file = "Scripts.rvdata2"
    output_dir = "Scripts"

    extract_scripts(input_file, output_dir)
