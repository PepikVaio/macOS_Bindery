#!/bin/bash

rm -rf Bindery.ico.pngs
rm -f Bindery.ico

mkdir Bindery.ico.pngs

sips -z 16 16 Bindery.png --out Bindery.ico.pngs/16.png
sips -z 32 32 Bindery.png --out Bindery.ico.pngs/32.png
sips -z 128 128 Bindery.png --out Bindery.ico.pngs/128.png
sips -z 256 256 Bindery.png --out Bindery.ico.pngs/256.png

python3 <<'PY'
import os
import struct

folder = "Bindery.ico.pngs"
sizes = [16, 32, 128, 256]

images = []

for size in sizes:
    path = os.path.join(folder, f"{size}.png")

    with open(path, "rb") as file:
        data = file.read()

    images.append((size, data))

with open("Bindery.ico", "wb") as file:
    file.write(struct.pack("<HHH", 0, 1, len(images)))

    offset = 6 + len(images) * 16

    for size, data in images:
        width = 0 if size == 256 else size
        height = 0 if size == 256 else size

        file.write(struct.pack(
            "<BBBBHHII",
            width,
            height,
            0,
            0,
            1,
            32,
            len(data),
            offset
        ))

        offset += len(data)

    for _, data in images:
        file.write(data)
PY