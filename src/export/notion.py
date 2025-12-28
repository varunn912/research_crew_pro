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
        # Test connection
        client.users.me()
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
        
        # Get database ID
        database_id = os.getenv('NOTION_DATABASE_ID')
        if not database_id or database_id.startswith('your_'):
            print("⚠️ NOTION_DATABASE_ID not configured in .env")
            return None
        
        print(f"📊 Using Notion database: {database_id}")
        
        # Parse content into blocks
        blocks = []
        lines = content.split('\n')
        
        for line in lines[:100]:  # Notion limit per request
            if not line.strip():
                continue
            
            try:
                # Headers
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
                    # Regular paragraph
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
        
        # Create page
        page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [{
                        "text": {"content": title[:100]}
                    }]
                }
            },
            children=blocks[:100]  # Notion limit
        )
        
        page_url = page.get('url')
        print(f"✅ Exported to Notion: {page_url}")
        return page_url
        
    except APIResponseError as e:
        print(f"❌ Notion API error: {e}")
        print("   Check database ID and permissions")
        return None
    except Exception as e:
        print(f"❌ Notion export error: {e}")
        import traceback
        traceback.print_exc()
        return None