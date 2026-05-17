import os
import re
import markdown
from nexy.core.config import Config

def find_doc_file(language, path_parts):
    base_path = "_docs"
    current_dir = os.path.join(base_path, language)
    if not os.path.exists(current_dir):
        return None
        
    found_path = None
    for part in path_parts:
        if not part: continue
        
        try:
            items = os.listdir(current_dir)
        except (FileNotFoundError, NotADirectoryError):
            return None
            
        match = None
        for item in items:
            # Clean item name (remove numbering and extension)
            clean_item = re.sub(r"^\d+\.\s*", "", item).lower().replace(" ", "-")
            if clean_item == part or clean_item.split(".")[0] == part:
                match = item
                break
        
        if not match:
            return None
            
        current_dir = os.path.join(current_dir, match)
        if os.path.isfile(current_dir):
            found_path = current_dir
            break
    
    return found_path

def get_doc_content(lang, slug):
    if not slug:
        return {"html": "<h1>Docs</h1>", "title": "Documentation"}
        
    slug_parts = slug.strip("/").split("/")
    
    # Try requested lang, then fallback to English
    file_path = find_doc_file(lang, slug_parts)
    if not file_path and lang != "en":
        file_path = find_doc_file("en", slug_parts)
        
    if file_path and os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Extract title
            title_match = re.search(r"^title\s*:\s*(.+)$", content, re.MULTILINE)
            title = title_match.group(1).strip().strip("'").strip('"') if title_match else "Documentation"
            
            # Clean and render
            clean_content = re.sub(r"^---.*?---", "", content, flags=re.DOTALL)
            conf = Config()
            html = markdown.markdown(clean_content, extensions=conf.MARKDOWN_EXTENSIONS + ["toc"])
            return {"html": html, "title": title}
            
    return {"html": "<h1>404 - Page Not Found</h1>", "title": "Not Found"}
