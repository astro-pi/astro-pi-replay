import io
import json
import logging
import os
import re
import typing
from pathlib import Path
from typing import Optional

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
TIMEOUT_SECONDS = 10


# Endpoint (must be a member of RPF):


class AssetPreparer:
    READ_SCOPE = "https://www.googleapis.com/auth/drive.metadata.readonly"
    # WRITE_SCOPE = "https://www.googleapis.com/auth/drive"
    WRITE_SCOPE = "https://www.googleapis.com/auth/drive.file"
    SCOPES = [WRITE_SCOPE]

    APP_SCRIPT_ENDPOINT: str = (
        "https://script.google.com/a/macros/"
        + "raspberrypi.org/s/AKfycbwnW3cNq25NsyaTjPG0qPP2mHXveYSPd_"
        + "mW3cmhoSSQlmjDgz0T1gmSsfzhCu1_HSbH/exec"
    )

    def __init__(self) -> None:
        creds = None
        if Path("token.json").exists():
            creds = Credentials.from_authorized_user_file(
                "token.json", AssetPreparer.SCOPES
            )
            self.creds = creds
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            logger.info("Creds invalid")
            if creds and creds.expired and creds.refresh_token:
                logger.info("Creds expired - trying to refresh")
                creds.refresh(Request())
            else:
                logger.info("Signing OAuth using credentials.json")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", AssetPreparer.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

            self.creds = creds

            # Start the services
            # self.scripts_service = build("script", "v2", credentials=creds)
            self.drive_service = build("drive", "v3", credentials=creds)

    def convention_checker(self, directory: str | Path) -> bool:
        """Ensures that the given directory adheres to the conventions
        outlined in `docs/explanation.md`. Otherwise, raises an exception.
        """

        dir_to_check: Path
        if type(directory) == Path:
            dir_to_check = typing.cast(Path, directory)
        else:
            dir_to_check = Path(directory)

        children = os.listdir(dir_to_check)
        assert ["data", "metadata.json", "photos", "videos"] in children
        assert (dir_to_check / "data" / "data.csv").exists()
        # Check it has photos/img_*.jpg|jpeg|png files
        assert all(filter(lambda x: x, os.listdir(dir_to_check / "photos")))
        # Check the metadata.json file has the correct keys
        with (dir_to_check / "metadata.json").open() as f:
            metadata = json.loads(f.read())
        assert [
            "lens",
            "camera",
            "ground_sampling_distance_cm",
            "resolution_x",
            "resolution_y",
            "start",
            "end",
            "team_credits",
        ] in metadata

        # Check it has a videos/video.mp4 file
        assert (dir_to_check / "videos" / "video.mp4").exists()

        replay_dir: Path = Path(__file__).parent.parent.parent
        replay_dir = replay_dir / "astro_pi_executor" / "replay"
        assert dir_to_check.is_relative_to(replay_dir)
        assert (
            dir_to_check.parent
            == f"({metadata['resolution_x']}_{metadata['resolution_y']})"
        )
        assert dir_to_check.parent.parent in ["VIS", "IR"]
        # TODO check it's unique by fetching S3

        return True

    def download_from_gdrive(self, url: str):
        self.drive_service.files()

        # # Call the Drive v3 API
        # results = service.files().list(
        #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
        # items = results.get('files', [])

        # if not items:
        #     print('No files found.')
        #     return
        # print('Files:')
        # for item in items:
        #     print(u'{0} ({1})'.format(item['name'], item['id']))
        # except HttpError as error:
        # # TODO(developer) - Handle errors from drive API.
        # print(f'An error occurred: {error}')

    # def derivation():
    #     working_dir: Path = Path(tempfile.gettempdir() / uuid.uuid4())

    def dl(self, url: str) -> typing.Optional[io.BytesIO]:
        split: list[str] = re.findall(
            r"(https?://)?drive.google.com/drive/folders/([A-z0-9_]+)\?.+$", url
        )
        print(split)
        if len(split) != 1 or len(split[0]) != 2:
            raise Exception(f"Couldn't identify fileId from url {url}.")
        fileId: str = split[0][1]
        # supportsAllDrives needed for Shared Drive support
        request = self.drive_service.files().get_media(
            fileId=fileId, supportsAllDrives=True
        )
        file: Optional[io.BytesIO] = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        try:
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"Download {int(status.progress() * 100)}.")
        except HttpError as e:
            logger.error(f"An error occurred: {e}")
            file = None

        return file

    def test_dl(self, fileId):
        return requests.get(
            AssetPreparer.APP_SCRIPT_ENDPOINT,
            # params={"folderId": fileId})
            headers={"Authorization": f"Bearer {self.creds.token}"},
            timeout=TIMEOUT_SECONDS,
        )


# 1dVk0aYwgJ9mzuZp6cwke_vY1jnk1yCNM
url: str = (
    "https://drive.google.com/drive/folders/"
    + "1dVk0aYwgJ9mzuZp6cwke_vY1jnk1yCNM?usp=drive_link"
)
# Path: Astro Pi Internal MSL Results 2023 / VIS / AstroX

testFileId: str = "1gWaT9C3AjIAGansYEg6QhwaR6YfYr8F9"

"""
Note: You cannot upload or download folders, shortcuts,
third-party shortcuts, and Google Workspace documents to or from Drive.
However, if they use compatible formats you can upload
or export Google Workspace documents. For example, you can create
a Google Doc when you import a PDF. Similarly, you
can export a Google Slides presentation as a Microsoft PowerPoint file.

"""
