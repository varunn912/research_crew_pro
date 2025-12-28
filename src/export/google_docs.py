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
    
    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print("⚠️ config/credentials.json not found")
        print("   Download from Google Cloud Console")
        return None
    
    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or get new token
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
        
        # Save token
        os.makedirs('config', exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def export_to_google_docs(content: str, title: str) -> Optional[str]:
    """Export content to Google Docs with proper formatting."""
    try:
        creds = setup_google_credentials()
        if not creds:
            return None
        
        # Build services
        docs_service = build('docs', 'v1', credentials=creds)
        
        # Create document
        doc = docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')
        
        print(f"📄 Created Google Doc: {doc_id}")
        
        # Prepare content requests
        requests = []
        index = 1
        
        # Split content into manageable chunks
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
            
            # Add line
            line_text = line + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': index},
                    'text': line_text
                }
            })
            
            # Format headers
            if line.startswith('# '):
                text_len = len(line_text)
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + text_len
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1'
                        },
                        'fields': 'namedStyleType'
                    }
                })
            elif line.startswith('## '):
                text_len = len(line_text)
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': index,
                            'endIndex': index + text_len
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2'
                        },
                        'fields': 'namedStyleType'
                    }
                })
            
            index += len(line_text)
        
        # Apply formatting in batches (Google Docs API limit)
        batch_size = 100
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i+batch_size]
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': batch}
                ).execute()
            except HttpError as e:
                print(f"⚠️ Batch update warning: {e}")
        
        # Get shareable link
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        
        print(f"✅ Exported to Google Docs: {doc_url}")
        return doc_url
        
    except Exception as e:
        print(f"❌ Google Docs export error: {e}")
        import traceback
        traceback.print_exc()
        return None