import os
import json
import re

def strip_markdown(text: str) -> str:
    # Basic markdown removal
    text = re.sub(r'#+\s+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'[*_`]', '', text)
    return text.strip()

def generate_search_index():
    docs_path = "_docs"
    languages = [d for d in os.listdir(docs_path) if os.path.isdir(os.path.join(docs_path, d))]
    
    search_index = []
    
    for lang in languages:
        lang_path = os.path.join(docs_path, lang)
        for root, dirs, files in os.walk(lang_path):
            for file in files:
                if file.endswith(('.md', '.mdx')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Extract title from frontmatter or first H1
                        title_match = re.search(r'^title\s*:\s*(.+)$', content, re.MULTILINE)
                        if not title_match:
                            title_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
                        
                        title = title_match.group(1).strip() if title_match else file.replace('.md', '').replace('.mdx', '')
                        
                        # Clean content
                        clean_content = strip_markdown(content)
                        
                        # Get relative path and clean it
                        rel_path = os.path.relpath(file_path, docs_path)
                        # Remove numbering and extensions from each part
                        parts = rel_path.replace('\\', '/').split('/')
                        clean_parts = [re.sub(r'^\d+\.\s*', '', p).lower().replace(' ', '-').replace('.mdx', '').replace('.md', '') for p in parts]
                        href = "/docs/" + "/".join(clean_parts)
                        
                        search_index.append({
                            "id": len(search_index),
                            "title": title,
                            "content": clean_content[:200], # Store preview
                            "href": href,
                            "lang": lang
                        })
        
    with open('docs/src/search_index.json', 'w', encoding='utf-8') as f:
        json.dump(search_index, f, indent=2, ensure_ascii=False)
    
    print(f"Search index generated with {len(search_index)} documents.")

if __name__ == "__main__":
    generate_search_index()
