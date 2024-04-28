# enums.py
# 04.03.2024

import utils.utils as utils

import os

from pathlib import Path


class Directories:
    # Permament
    Photos = "photos/"
    PhotosEncoded = "photos/encoded/"
    PhotosMultiple = "photos/multiple_people/"
    Downloads = "downloads/"
    DownloadsMatches = "downloads/matches/"
    DownloadsEncodings = "downloads/encodings/"
    Encodings = "encodings/"
    # Search phrases
    SearchPhrases = "search_phrases.txt"
    FacebookProfiles = "facebook_profiles.txt"
    InstagramProfiles = "instagram_profiles.txt"

    def GetDownloadsTemporary():
        if os.name == "nt":
            return "tmp/downloads/"
        else:
            return "/tmp/downloads/"


def CreateDirectories():
    # Permament
    Path(Directories.Photos).mkdir(parents=False, exist_ok=True)
    Path(Directories.PhotosEncoded).mkdir(parents=False, exist_ok=True)
    Path(Directories.PhotosMultiple).mkdir(parents=False, exist_ok=True)
    Path(Directories.Downloads).mkdir(parents=False, exist_ok=True)
    Path(Directories.DownloadsMatches).mkdir(parents=False, exist_ok=True)
    Path(Directories.DownloadsEncodings).mkdir(parents=False, exist_ok=True)
    Path(Directories.Encodings).mkdir(parents=False, exist_ok=True)
    # Temporary(on windows permament)
    Path(Directories.GetDownloadsTemporary()).mkdir(parents=False, exist_ok=True)

    if not os.path.isfile(Directories.SearchPhrases):
        utils.SaveFile(Directories.SearchPhrases, bytes())

    if not os.path.isfile(Directories.FacebookProfiles):
        utils.SaveFile(Directories.FacebookProfiles, bytes())

    if not os.path.isfile(Directories.InstagramProfiles):
        utils.SaveFile(Directories.InstagramProfiles, bytes())
