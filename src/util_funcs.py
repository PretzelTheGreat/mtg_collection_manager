import json
import requests
import os
import csv
import zipfile

show_log = True
DEBUG_LEVEL = "DEBUG"

level_mapping = {"INFO": 0, "DEBUG": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}

def log_message(message_string, level):
    if show_log and level_mapping[level] >= level_mapping[DEBUG_LEVEL]:
        print(f"{level} - {message_string}")

def import_json_file(filename):
    data = {}
    log_message(f"loading {filename}", "INFO")
    with open(filename, 'r', encoding="utf-8") as open_file:
        data = json.load(open_file)

    log_message(f"finished loading {filename}", "INFO")
    return data

def import_csv_file(filename):
    data = []
    log_message(f"loading {filename}", "INFO")
    with open(filename, 'r') as open_file:
        csv_reader = csv.DictReader(open_file)

        for line in csv_reader:
            data.append(line)

    log_message(f"finished loading {filename}", "INFO")
    return data

def import_text_file(filename):
    data = []
    log_message(f"loading {filename}", "INFO")
    with open(filename, encoding='utf-8') as open_file:
        for line in open_file.readlines():
            data.append(line.strip())

    log_message(f"finished loading {filename}", "INFO")
    return data

def export_json_file(filename, data, indent=4):
    log_message(f"exporting {filename}", "INFO")
    with open(filename, 'w', encoding='utf-8') as open_file:

        json.dump(data, open_file, indent=indent)

    log_message(f"done exporting {filename}", "INFO")

def export_csv_file(filename, data, fieldnames):
    log_message(f"exporting {filename}", "INFO")
    with open(filename, 'w', newline="") as open_file:
        csv_writer = csv.DictWriter(open_file, fieldnames=fieldnames)

        csv_writer.writeheader()
        csv_writer.writerows(data)

    log_message(f"done exporting {filename}", "INFO")

def export_text_file(filename, data):
    # this is a simple export function to handle exporting text files
    log_message(f"exporting {filename}", "INFO")
    with open(filename, 'w', encoding='utf-8') as open_file:
        for line in data:
            if line == data[-1]:
                open_file.write(f"{line}")
            else:
                open_file.write(f"{line}\n")

    log_message(f"done exporting {filename}", "INFO")

def create_tmp_dir():
    if 'tmp' not in os.listdir('resources'):
        os.mkdir('resources/tmp')


def download_file_from_url(url, filename):
    # first create a temporary directory to hold the download file
    create_tmp_dir()

    log_message(f"requesting resources from url: '{url}'", "INFO")
    # next, process the request
    r = requests.get(url, allow_redirects=True, timeout=0.500)
    log_message(f"received request data", "INFO")
    
    log_message(f"writing contets of request to '{filename}'", "INFO")
    # write the file with the desired filename (should be roughly what the end filename should be)
    with open(f"resources/tmp/{filename}", 'wb') as open_file:
        open_file.write(r.content)
    log_message(f"done writing request contents", "INFO")


def unzip_file_to_loc(filepath, target_loc):
    # filepath should be passed here, not just the filename
    log_message(f"unzipping '{filepath}' to '{target_loc}'", "INFO")
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(target_loc)
    log_message(f"done unzipping {filepath}", "INFO")