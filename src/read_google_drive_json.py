import io
import json
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class GoogleDriveJsonReader:
    _SCOPES = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    def __init__(self, credentials_json_path, token_json_path, json_path):
        self._creds = self._set_credential(credentials_json_path, token_json_path)
        self._json = self._read_json(json_path)

    def _set_credential(self, credentials_json_path: str, token_json_path: str):
        creds = None

        if os.path.exists(token_json_path):
            # creds = Credentials.from_authorized_user_file(token_json_path)
            creds = Credentials.from_authorized_user_info(
                os.environ.get("GOOGLE_DRIVE_TOKEN")
            )
        return creds

    def _read_json(self, json_path):
        # Drive APIクライアントを初期化
        service = build("drive", "v3", credentials=self._creds)

        # ファイル名で検索
        query = f"name = '{json_path}'"
        response = service.files().list(q=query).execute()
        files = response.get("files", [])

        # ファイルが存在するか
        if not files:
            raise FileNotFoundError(f"パスにファイルが見つかりません. {json_path}")

        file_id = files[0]["id"]

        # ファイルをダウンロード
        request = service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        file_io.seek(0)

        json_content = json.load(file_io)

        return json_content

    @property
    def json(self):
        return self._json

    @property
    def creds(self):
        return self._creds
