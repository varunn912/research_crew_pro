from notion_client import Client
from notion_client.errors import APIResponseError
import os
from typing import Optional


def setup_notion() -> Optional[Client]:
    """Setup Notion client with API key."""
    api_key = os.getenv('NOTION_API_KEY')

    if not api_key or api_key.startswith('your_'):
        print("⚠️ NOTION_API_KEY not configured in .env")
        return None

    try:
        client = Client(auth=api_key)
        client.users.me()  # test connection
        return client
    except Exception as e:
        print(f"⚠️ Notion connection failed: {e}")
        return None


def export_to_notion(content: str, title: str) -> Optional[str]:
    """Export content to Notion database."""
    try:
        notion = setup_notion()
        if not notion:
            return None

        database_id = os.getenv('NOTION_DATABASE_ID')
        if not database_id or database_id.startswith('your_'):
            print("⚠️ NOTION_DATABASE_ID not configured in .env")
            return None

        blocks = []
        lines = content.split('\n')

        for line in lines[:100]:  # Notion limit
            if not line.strip():
                continue

            try:
                if line.startswith('# '):
                    blocks.append({
                        "object": "block",
                        "type": "heading_1",
                        "heading_1": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": line[2:].strip()[:2000]}
                            }]
                        }
                    })
                elif line.startswith('## '):
                    blocks.append({
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": line[3:].strip()[:2000]}
                            }]
                        }
                    })
                elif line.startswith('---'):
                    blocks.append({
                        "object": "block",
                        "type": "divider",
                        "divider": {}
                    })
                else:
                    clean_line = line.replace('**', '').replace('*', '').strip()
                    if clean_line:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{
                                    "type": "text",
                                    "text": {"content": clean_line[:2000]}
                                }]
                            }
                        })
            except Exception as e:
                print(f"⚠️ Skipping line: {str(e)[:50]}")
                continue

        page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [{
                        "text": {"content": title[:100]}
                    }]
                }
            },
            children=blocks[:100]
        )

        return page.get('url')

    except APIResponseError as e:
        print(f"❌ Notion API error: {e}")
        return None
    except Exception as e:
        print(f"❌ Notion export error: {e}")
        return None


# ✅ FIX: Add missing class
class NotionTool:
    """Wrapper for CrewAI compatibility"""

    def __init__(self):
        pass

    def run(self, content: str, title: str = "Research Report") -> str:
        """Main execution method used by agents"""
        url = export_to_notion(content, title)

        if not url:
            return "❌ Failed to export to Notion"

        return f"✅ Notion page created: {url}"