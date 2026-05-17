import os
import json
import re

def slugify(text: str) -> str:
    # Convert text to slug
    text = text.lower()
    # Remove numbering like "01. "
    text = re.sub(r'^\d+\.\s*', '', text)
    # Replace spaces and non-alphanumeric with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def get_label(name: str) -> str:
    # Remove numbering like "01. " and ".md" extension
    label = re.sub(r'^\d+\.\s*', '', name)
    label = label.replace('.md', '').replace('.mdx', '')
    return label

def crawl_docs(base_path: str, lang: str) -> list:
    lang_path = os.path.join(base_path, lang)
    if not os.path.exists(lang_path):
        return []

    manifest = []
    
    # Sort files to respect numbering
    items = sorted(os.listdir(lang_path))
    
    for item in items:
        item_path = os.path.join(lang_path, item)
        if os.path.isdir(item_path):
            section = {
                "title": get_label(item),
                "items": []
            }
            # Recursively crawl subdirectories
            sub_items = sorted(os.listdir(item_path))
            for sub_item in sub_items:
                if sub_item.endswith(('.md', '.mdx')):
                    label = get_label(sub_item)
                    slug = slugify(label)
                    # Construct href: /docs/{lang}/{section_slug}/{page_slug}
                    # Or follow the current structure in _docs
                    section["items"].append({
                        "label": label,
                        "href": f"/docs/{lang}/{slugify(section['title'])}/{slug}"
                    })
            manifest.append(section)
        elif item.endswith(('.md', '.mdx')) and item != 'introduction.md':
            label = get_label(item)
            manifest.append({
                "label": label,
                "href": f"/docs/{lang}/{slugify(label)}"
            })
            
    return manifest

def generate_manifest():
    docs_path = "_docs"
    languages = [d for d in os.listdir(docs_path) if os.path.isdir(os.path.join(docs_path, d))]
    
    full_manifest = {}
    for lang in languages:
        full_manifest[lang] = crawl_docs(docs_path, lang)
        
    with open('docs/src/manifest.json', 'w', encoding='utf-8') as f:
        json.dump(full_manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Manifest generated for {len(languages)} languages.")

if __name__ == "__main__":
    generate_manifest()
