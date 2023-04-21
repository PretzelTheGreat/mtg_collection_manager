import json

show_log = True

def log_message(message_string, level):
    if show_log:
        print(f"{level} - {message_string}")

def import_json_file(filename):
    data = {}
    log_message(f"loading {filename}", "DEBUG")
    with open(filename, 'r', encoding="utf-8") as open_file:
        data = json.load(open_file)

    log_message(f"finished loading {filename}", "DEBUG")
    return data