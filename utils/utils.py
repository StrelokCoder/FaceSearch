# utils.py
# 04.03.2024

from utils.enums import Directories

import string, random
import hashlib
import os

from PIL.PngImagePlugin import PngInfo
from PIL import Image, UnidentifiedImageError


def RandomString(length=32):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def HashStringSHA256(string):
    hash = hashlib.new("sha256")
    hash.update(string.encode())
    return hash.hexdigest()


def SaveFile(file_path, file_bytes):
    with open(file_path, "wb") as file:
        file.write(file_bytes)


def LoadFile(file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()
    return file_bytes


# Use this to save image, cause it will remove invalid images in the process
def SaveImage(image_path, image_bytes, metadatas):
    SaveFile(image_path, image_bytes)

    try:
        image = Image.open(image_path)
        # No more console spamming with warning "libpng warning: iCCP: known incorrect sRGB profile"
        image.info.pop("icc_profile", None)
    except UnidentifiedImageError:
        os.remove(image_path)
        return

    if len(metadatas) == 0:
        return

    os.remove(image_path)
    image_metadata = PngInfo()
    for metadata in metadatas:
        image_metadata.add_text(metadata[0], metadata[1])

    image.save(image_path, pnginfo=image_metadata)
    image.close()


def GetImageMetadata(image_path, metadata_key):
    with Image.open(image_path) as image:
        ret = image.info[metadata_key]
    return ret


def ClearDownloadsTemporary():
    for image_name in os.listdir(Directories.GetDownloadsTemporary()):
        os.remove(Directories.GetDownloadsTemporary() + image_name)
