# facerecognition.py
# 04.03.2024

import utils.console as console
import utils.utils as utils

from utils.enums import Directories

import shutil
import numpy
import cv2
import os

from tqdm import tqdm as ProgressionBar


# Modifies image by drawing detected faces on it
def DrawFacesInfo(faces, image_path, save_path):
    img = cv2.imread(image_path)

    for face in faces:
        # Box showing where face is
        face_box = face.bbox.astype(int)
        cv2.rectangle(img, (face_box[0], face_box[1]), (face_box[2], face_box[3]), (0, 0, 255), 2)

        # Main face landmarks
        for landmark in face.kps:
            cv2.circle(img, (int(landmark[0]), int(landmark[1])), 3, (255, 0, 0), -1)

        # All face landmakrs
        for landmark in face.landmark_2d_106:
            cv2.circle(img, (int(landmark[0]), int(landmark[1])), 1, (0, 255, 0), -1)

        # Basic info about person
        if face.gender is not None and face.age is not None:
            cv2.putText(img, "{0},{1}".format(face.sex, face.age), (face_box[0] - 2, face_box[1] - 5), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 1)

    cv2.imwrite(save_path, img)


# Moves matched photo to matched photos folder
def MoveMatchedPhotos(original_encoding, encodings_info):
    for encoding_info in encodings_info:
        best_similarity = 0
        save = False

        for encoding in encoding_info[2]:
            similarity = numpy.dot(encoding, original_encoding)
            if similarity > 0.6 and similarity > best_similarity:
                best_similarity = similarity
                save = True

        if save is True:
            shutil.move(encoding_info[0], os.getcwd() + "/" + Directories.DownloadsMatches + "{:.10f}.png".format(best_similarity))


def BatchFaceEncodings(face_analysis):
    encodings_info = []

    for image_name in ProgressionBar(os.listdir(Directories.DownloadsTemporary)):
        image_path = Directories.DownloadsTemporary + image_name
        faces = face_analysis.get(cv2.imread(image_path))

        encodings = []
        for face in faces:
            encodings.append(numpy.array(face.normed_embedding, dtype=numpy.float32))

        if len(encodings) != 0:
            encodings_info.append((image_path, utils.GetImageMetadata(image_path, "url"), encodings))

    console.SubTask("Faces found and encoded on {0} images, from total of {1} images".format(len(encodings_info), len(os.listdir(Directories.DownloadsTemporary))))

    return encodings_info


def SaveEncodedImage(save_directory, image_url, encodings):
    if len(encodings) != 0:
        file_bytes = bytes()
        file_bytes += int(len(image_url)).to_bytes(4, "big")
        file_bytes += str(image_url).encode()
        file_bytes += int(len(encodings)).to_bytes(4, "big")
        for i in range(0, len(encodings), 1):
            file_bytes += bytes(encodings[i])
        utils.SaveFile(save_directory + utils.HashStringSHA256(image_url), file_bytes)


def LoadEncodedImage(encoding_path):
    with open(encoding_path, "rb") as file:
        image_url_length = int.from_bytes(file.read(4), "big")
        image_url = file.read(image_url_length).decode()
        encodings_count = int.from_bytes(file.read(4), "big")
        encodings = []
        for i in range(0, encodings_count, 1):
            encodings.append(numpy.fromstring(file.read(2048), dtype=numpy.float32))

    return (image_url, encodings)


def LoadDataBase():
    database = []

    encodings_directories = os.listdir(Directories.Encodings)
    for encodings_directory in encodings_directories:
        encodings_directory = Directories.Encodings + encodings_directory + "/"
        encodings_path = os.listdir(encodings_directory)
        for i in range(0, len(encodings_path), 1):
            database.append(LoadEncodedImage(encodings_directory + encodings_path[i]))

    return database


def LoadDatabaseSHA256():
    database_sha256 = []

    for directory in os.listdir(Directories.Encodings):
        for encoding_name in os.listdir(Directories.Encodings + directory + "/"):
            database_sha256.append(encoding_name)

    return database_sha256


# Returns (path_to_directory, items_count)
def FindEmptyEncodingDirectory():
    directories = os.listdir(Directories.Encodings)
    for directory in directories:
        directory = Directories.Encodings + directory + "/"
        items_count = len(os.listdir(directory))
        if items_count < 1024:
            return [directory, items_count]

    new_directory_path = Directories.Encodings + str(len(directories) + 1) + "/"
    os.mkdir(new_directory_path)
    return [new_directory_path, 0]


def SaveEncodings(encodings_info, database_sha256):
    save_directory = FindEmptyEncodingDirectory()

    for i in range(0, len(encodings_info), 1):
        encoding_info = encodings_info[i]
        sha256_is_equal = False

        encoding_sha256 = utils.HashStringSHA256(encoding_info[1])
        for sha256 in database_sha256:
            if sha256 == encoding_sha256:
                sha256_is_equal = True
                break

        if sha256_is_equal == True:
            continue

        if save_directory[1] >= 1024:
            save_directory = FindEmptyEncodingDirectory()

        save_directory[1] += 1
        database_sha256.append(encoding_sha256)
        SaveEncodedImage(save_directory[0], encoding_info[1], encoding_info[2])
