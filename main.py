# main.py
# 04.03.2024

import utils.facerecognition as frutils
import utils.webutils as webutils
import utils.console as console
import utils.utils as utils

from utils.enums import Directories, CreateDirectories
from services.instagram import Instagram
from services.facebook import Facebook
from services.yandex import Yandex
from services.google import Google

import traceback
import colorama
import shutil
import ntpath
import numpy
import cv2
import os

from insightface.app import FaceAnalysis


def IsArrayEmpty(array, empty_message, not_empty_message):
    if len(array) == 0:
        console.Error(empty_message)
        return True
    else:
        console.Task(not_empty_message)
        return False


def ReverseSearchPhotos(face_analysis, database_sha256, save_encodings, compare_database, download_matches):
    compare_faces = compare_database or download_matches

    photos_path = []
    for photo_name in os.listdir(Directories.Photos):
        if photo_name.endswith((".png", ".jpg", ".jpeg", ".webp")):
            photos_path.append(Directories.Photos + photo_name)

    if IsArrayEmpty(photos_path, "There are no photos", "Encoding faces from {0} photos".format(len(photos_path))):
        return

    # (photo_path, encoding, [[urls]])
    photos_info = []
    for photo_path in photos_path:
        if not compare_faces:
            photos_info.append((photo_path, [], []))
        else:
            faces = face_analysis.get(cv2.imread(photo_path))

            if len(faces) == 1:
                photos_info.append((photo_path, numpy.array(faces[0].normed_embedding, dtype=numpy.float32), []))
            elif len(faces) == 0:
                console.SubError("Couldn't find any faces on photo: {0}".format(photo_path))
            else:
                console.SubError("There is more than one face on photo: {0}, faces count: {1}".format(photo_path, len(faces)))

    if len(photos_info) == 0:
        console.Error("Couldn't encode any face on any image, aborting")
        return
    else:
        console.SubTask("Successfully encoded face on {0} photos".format(len(photos_info)))

    if save_encodings or download_matches:
        driver = webutils.GetWebdriver()
        yandex = Yandex()
        yandex_up_to_date = yandex.Init(driver)

        for photo_info in photos_info:
            console.SubTask("Reverse searching photo: {0}".format(photo_info[0]))

            try:
                if yandex_up_to_date:
                    photo_info[2].append(yandex.ReverseImagesSearch(driver, os.getcwd() + "/" + photo_info[0]))
            except:
                webutils.WebDriverCloseAllExtraTabs(driver)
                console.SubError("Exception while web searching\n")
                traceback.print_exc()

            if webutils.DownloadUrls(photo_info[2], "No urls for photo: {0}".format(photo_info[0])) == False:
                continue

            # (image_path, image_url, [encoding])
            encodings_info = frutils.BatchFaceEncodings(face_analysis)

            if download_matches:
                frutils.MoveMatchedPhotos(photo_info[1], encodings_info)

            if save_encodings:
                frutils.SaveEncodings(encodings_info, database_sha256)
                shutil.move(photo_info[0], Directories.PhotosEncoded + ntpath.basename(photo_info[0]))

            utils.ClearDownloadsTemporary()

        driver.quit()

    if compare_database:
        # [(image_url, [encodings])]
        database = frutils.LoadDataBase()

        for photo_info in photos_info:
            console.SubTask("Reverse searching photo: {0} in database".format(photo_info[0]))
            # (url, similarity)
            matches = []
            for image_info in database:
                best_similarity = 0
                save = False

                for encoding in image_info[1]:
                    similarity = numpy.dot(encoding, photo_info[1])
                    if similarity > 0.6 and similarity > best_similarity:
                        best_similarity = similarity
                        save = True

                if save is True:
                    matches.append((image_info[0], best_similarity))

            matches.sort(key=lambda x: x[1], reverse=False)

            if len(matches) != 0:
                webutils.BatchDownloadMatchedImages(ntpath.basename(photo_info[0]), matches)


def TextSearchPhotos(face_analysis, database_sha256):
    lines = utils.LoadFile(Directories.SearchPhrases).decode().splitlines()

    if IsArrayEmpty(lines, "No phrases to use at text searching", "There are {0} phrases to use at text search".format(len(lines))):
        return

    driver = webutils.GetWebdriver()
    google = Google()
    google_up_to_date = google.Init(driver)

    web_search_crash = []

    for line in lines:
        console.SubTask("Searching for pharse: {0}".format(line))

        # [[urls]]
        array_urls_array = []

        try:
            if google_up_to_date:
                array_urls_array.append(google.TextImagesSearch(driver, line))
        except:
            web_search_crash.append(line)
            webutils.WebDriverCloseAllExtraTabs(driver)
            console.SubError("Exception while web searching\n")
            traceback.print_exc()

        if webutils.DownloadUrls(array_urls_array, "No urls for pharse: {0}".format(line)) == False:
            continue

        # (image_path, image_url, [encoding])
        frutils.SaveEncodings(frutils.BatchFaceEncodings(face_analysis), database_sha256)

        utils.ClearDownloadsTemporary()

    os.remove(Directories.SearchPhrases)
    with open(Directories.SearchPhrases, "w") as file:
        for saved_line in web_search_crash:
            file.write(saved_line + "\n")

    driver.quit()


def FacebookSearchPhotos(face_analysis, database_sha256):
    lines = utils.LoadFile(Directories.FacebookProfiles).decode().splitlines()

    if IsArrayEmpty(lines, "No profiles to use at facebook searching", "There are {0} profiles names to use at facebook profile search".format(len(lines))):
        return

    driver = webutils.GetWebdriver()
    facebook = Facebook()
    facebook_up_to_date = facebook.Init(driver)

    web_search_crash = []

    for line in lines:
        console.SubTask("Searching for pharse: {0}".format(line))

        # [[urls]]
        array_urls_array = []

        try:
            if facebook_up_to_date:
                array_urls_array.append(facebook.ProfileImagesSearch(driver, line))
        except:
            web_search_crash.append(line)
            webutils.WebDriverCloseAllExtraTabs(driver)
            console.SubError("Exception while web searching\n")
            traceback.print_exc()

        if webutils.DownloadUrls(array_urls_array, "No urls for facebook profile: {0}".format(line)) == False:
            continue

        # (image_path, image_url, [encoding])
        frutils.SaveEncodings(frutils.BatchFaceEncodings(face_analysis), database_sha256)

        utils.ClearDownloadsTemporary()

    os.remove(Directories.FacebookProfiles)
    with open(Directories.FacebookProfiles, "w") as file:
        for saved_line in web_search_crash:
            file.write(saved_line + "\n")

    driver.quit()


def InstagramSearchPhotos(face_analysis, database_sha256):
    lines = utils.LoadFile(Directories.InstagramProfiles).decode().splitlines()

    if IsArrayEmpty(lines, "No profiles to use at instagram searching", "There are {0} profiles names to use at instagram profile search".format(len(lines))):
        return

    driver = webutils.GetWebdriver()
    instagram = Instagram()
    instagram_up_to_date = instagram.Init(driver)

    web_search_crash = []

    for line in lines:
        console.SubTask("Searching for pharse: {0}".format(line))

        # [[urls]]
        array_urls_array = []

        try:
            if instagram_up_to_date:
                array_urls_array.append(instagram.ProfileImagesSearch(driver, line))
        except:
            web_search_crash.append(line)
            webutils.WebDriverCloseAllExtraTabs(driver)
            console.SubError("Exception while web searching\n")
            traceback.print_exc()

        if webutils.DownloadUrls(array_urls_array, "No urls for instagram profile: {0}".format(line)) == False:
            continue

        # (image_path, image_url, [encoding])
        frutils.SaveEncodings(frutils.BatchFaceEncodings(face_analysis), database_sha256)

        utils.ClearDownloadsTemporary()

    # os.remove(Directories.InstagramProfiles)
    # with open(Directories.InstagramProfiles, "w") as file:
    #    for saved_line in web_search_crash:
    #        file.write(saved_line + "\n")

    driver.quit()


def main(save_encodings, compare_database, download_matches, search_phrases, search_profiles):
    # Reset console colors everytime we print something
    colorama.init(autoreset=True)
    CreateDirectories()

    # Load it so we won't get spammed by messages, also it will make program run a little faster
    face_analysis = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    face_analysis.prepare(ctx_id=0, det_size=(640, 640))

    database_sha256 = []
    if search_profiles == True or search_phrases == True or save_encodings == True:
        database_sha256 = frutils.LoadDatabaseSHA256()

    if search_profiles:
        FacebookSearchPhotos(face_analysis, database_sha256)
        # InstagramSearchPhotos(face_analysis, database_sha256)

    if search_phrases:
        TextSearchPhotos(face_analysis, database_sha256)

    if save_encodings == True or compare_database == True or download_matches == True:
        ReverseSearchPhotos(face_analysis, database_sha256, save_encodings, compare_database, download_matches)

    console.Task("Program finished working")


if __name__ == "__main__":
    save_encodings = False
    compare_database = True
    download_matches = False
    search_phrases = False
    search_profiles = False

    main(save_encodings, compare_database, download_matches, search_phrases, search_profiles)
