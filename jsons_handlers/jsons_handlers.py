
import json

def json_reader(file_inp):
    with open(file_inp, 'r', encoding='utf-8') as file:
        contents = file.read()
        js_data = json.loads(contents)
    return js_data


def json_writer(file_out, data):
    # with FileLock(file_out):
    with open(file_out, 'w', encoding='utf-8') as file: json.dump(data, file, ensure_ascii=False, indent=1, sort_keys=True)