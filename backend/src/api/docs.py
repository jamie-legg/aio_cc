from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
import os
import json
from pathlib import Path

router = APIRouter()

# Get the project root directory (assuming this file is in backend/src/api/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

@router.get("/api/docs")
async def get_docs_index():
    """Get the documentation index with all categories and files"""
    try:
        index_file = DOCS_DIR / "index.json"
        if not index_file.exists():
            raise HTTPException(status_code=404, detail="Documentation index not found")
        
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading docs index: {str(e)}")

@router.get("/api/docs/{category}/{filename}")
async def get_doc_content(category: str, filename: str):
    """Get the content of a specific documentation file"""
    try:
        # Validate category and filename to prevent path traversal
        if ".." in category or ".." in filename:
            raise HTTPException(status_code=400, detail="Invalid path")
        
        doc_path = DOCS_DIR / category / filename
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="Documentation file not found")
        
        # Read the markdown file
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"content": content, "filename": filename, "category": category}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading documentation: {str(e)}")

@router.get("/api/docs/search")
async def search_docs(query: str):
    """Search through all documentation files"""
    try:
        results = []
        
        # Load the index to get all files
        index_file = DOCS_DIR / "index.json"
        if not index_file.exists():
            return {"results": []}
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Search through each category
        for category_key, category_data in index_data["categories"].items():
            for doc in category_data["docs"]:
                doc_path = DOCS_DIR / category_key / doc["filename"]
                if doc_path.exists():
                    try:
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Simple text search (case-insensitive)
                        if query.lower() in content.lower() or query.lower() in doc["title"].lower():
                            results.append({
                                "category": category_key,
                                "category_name": category_data["name"],
                                "filename": doc["filename"],
                                "title": doc["title"],
                                "description": doc["description"],
                                "snippet": _extract_snippet(content, query)
                            })
                    except Exception:
                        continue
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documentation: {str(e)}")

def _extract_snippet(content: str, query: str, max_length: int = 200) -> str:
    """Extract a snippet around the query match"""
    query_lower = query.lower()
    content_lower = content.lower()
    
    # Find the first occurrence
    index = content_lower.find(query_lower)
    if index == -1:
        return content[:max_length] + "..." if len(content) > max_length else content
    
    # Extract snippet around the match
    start = max(0, index - max_length // 2)
    end = min(len(content), start + max_length)
    
    snippet = content[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    
    return snippet

