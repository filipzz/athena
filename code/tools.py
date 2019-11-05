import json

def read_table(file_to_read):
    with open(file_to_read, 'r') as f:
        data = json.load(f)
    return data

def save_table(table_to_save, file_to_save):
    with open(file_to_save, 'w') as f:
        json.dump(table_to_save, f)


