import chardet

def detect_file_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    return chardet.detect(raw_data)['encoding']

file_path = '/Users/zuhayrshaikh/Documents/GitHub/EV-placement/model/401_Data.csv'
encoding = detect_file_encoding(file_path)
print(f"The detected encoding is: {encoding}")
