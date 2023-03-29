import os

file_name = "test.txt"
size = os.path.getsize(file_name)
chunks = 2

offsets = [i * size // chunks for i in range(chunks + 1)]
offsets[-1] = size
sizes = [offsets[i + 1] - offsets[i] for i in range(chunks)]



with open(file_name, "rb") as f:
    for i in range(chunks):
        f.seek(offsets[i])
        data = f.read(offsets[i + 1] - offsets[i])
        print(data)
