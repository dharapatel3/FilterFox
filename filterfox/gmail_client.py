from __future__ import annotations
from typing import List, Dict, Optional, Any
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

class GmailClient:
    def __init__(self, credentials_path: Path, token_path: Path):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._auth()
    def _auth(self):
        creds: Optional[Credentials] = None

        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Missing credentials.json file"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)

            self.token_path.write_text(creds.to_json(), encoding ="utf-8")

        return build("gmail", "v1", credentials=creds)

    def list_message_ids(self, user_id: str = "me", query: str = "", max_results: int = 100) -> List[str]:
        ids: List[str] = []
        page_token = None

        while len(ids) < max_results:
            resp = self.service.users().messages().list(
                userId=user_id,
                q = query,
                maxResults=min(500, max_results - len(ids)),
                pageToken=page_token,
            ).execute()

            for m in resp.get("messages", []) or []:
                ids.append(m["id"])

            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        return ids

    def get_message_metadata(self, message_id: str, user_id: str = "me") -> Dict[str, Any]:
        return self.service.users().messages().get(
            userId=user_id,
            id=message_id,
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "List-Unsubscribe", "Precedence"],
        ).execute()

    def list_labels(self, user_id: str = "me") -> List[Dict[str, str]]:
        resp = self.service.users().labels().list(userId=user_id).execute()
        return resp.get("labels", []) or []

    def create_label(self, name: str, user_id: str = "me") -> str:
        body = {
            "name": name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
        resp = self.service.users().labels().create(userId=user_id, body=body).execute()
        return resp["id"]

    def ensure_label(self, label_name: str, user_id: str = "me") -> str:
        for lab in self.list_labels(user_id=user_id):
            if lab.get("name") == label_name:
                return lab["id"]
        return self.create_label(label_name, user_id=user_id)

    def modify_message(
        self,
        message_id: str,
        add_label_ids: List[str] | None = None,
        remove_label_ids: List[str] | None = None,
        user_id: str = "me",
    ) -> None:
        body = {
            "addLabelIds": add_label_ids or [],
            "removeLabelIds": ["INBOX"],
        }
        self.service.users().messages().modify(userId=user_id, id=message_id, body=body).execute()