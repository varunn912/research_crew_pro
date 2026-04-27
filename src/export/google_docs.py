from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pickle
from typing import Optional

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]


def setup_google_credentials() -> Optional[Credentials]:
    """Setup Google API credentials from credentials.json."""
    creds = None
    token_path = 'config/token.pickle'
    credentials_path = 'config/credentials.json'

    if not os.path.exists(credentials_path):
        print("⚠️ config/credentials.json not found")
        return None

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                creds = None

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"❌ Google auth failed: {e}")
                return None

        os.makedirs('config', exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def export_to_google_docs(content: str, title: str) -> Optional[str]:
    """Export content to Google Docs."""
    try:
        creds = setup_google_credentials()
        if not creds:
            return None

        docs_service = build('docs', 'v1', credentials=creds)

        doc = docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')

        requests = []
        index = 1

        lines = content.split('\n')

        for line in lines:
            if not line.strip():
                requests.append({
                    'insertText': {
                        'location': {'index': index},
                        'text': '\n'
                    }
                })
                index += 1
                continue

            line_text = line + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': line_text
                }
            })

            # Header formatting
            if line.startswith('# '):
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + len(line_text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1'
                        },
                        'fields': 'namedStyleType'
                    }
                })
            elif line.startswith('## '):
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + len(line_text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2'
                        },
                        'fields': 'namedStyleType'
                    }
                })

            index += len(line_text)

        # Batch updates
        batch_size = 100
        for i in range(0, len(requests), batch_size):
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests[i:i + batch_size]}
            ).execute()

        return f"https://docs.google.com/document/d/{doc_id}/edit"

    except Exception as e:
        print(f"❌ Google Docs export error: {e}")
        return None


# ✅ THIS IS THE FIX (missing class)
class GoogleDocsTool:
    """Wrapper class for CrewAI compatibility"""

    def __init__(self):
        pass

    def run(self, content: str, title: str = "Research Report") -> str:
        """Main method used by agents"""
        url = export_to_google_docs(content, title)

        if not url:
            return "❌ Failed to export to Google Docs"

        return f"✅ Document created: {url}"