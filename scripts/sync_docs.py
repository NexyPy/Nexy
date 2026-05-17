import os
import re
import unicodedata

def slugify(value: str) -> str:
    """
    Normalizes string, converts to lowercase, removes non-alphanumeric characters,
    and converts spaces to hyphens. Supports non-ASCII characters by falling back to 
    safe characters if slugify fails.
    """
    original = value
    # Normalize and remove non-spacing marks (accents)
    value = unicodedata.normalize('NFKD', value)
    # Remove accents but keep Unicode characters
    value = "".join([c for c in value if not unicodedata.combining(c)])
    
    # Try ASCII-only slug first
    ascii_slug = value.encode('ascii', 'ignore').decode('ascii')
    ascii_slug = re.sub(r'[^\w\s-]', '', ascii_slug).strip().lower()
    slug = re.sub(r'[-\s]+', '-', ascii_slug)
    
    if not slug:
        # For non-ASCII names, we keep them but clean for URLs
        # Replace spaces and special URL chars with hyphens
        slug = original.lower().replace(" ", "-").replace(".", "").replace("/", "-")
        slug = re.sub(r'[\\:*?"<>|]', '', slug)
        slug = slug.strip("-")
    
    return slug

def get_frontmatter(content):
    title = ""
    description = ""
    
    # Try to find title in frontmatter
    title_match = re.search(r'^title\s*:\s*(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip().strip('"').strip("'")
    else:
        # Fallback to first H1
        h1_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()

    description_match = re.search(r'^description\s*:\s*(.+)$', content, re.MULTILINE)
    if description_match:
        description = description_match.group(1).strip().strip('"').strip("'")
    
    return title, description

def clean_markdown(content):
    # Remove frontmatter block if it exists
    content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
    # Remove first H1 if it matches the title
    content = re.sub(r'^#\s*.+$', '', content, count=1, flags=re.MULTILINE)
    return content.strip()

def sync_docs():
    base_docs = "_docs"
    target_docs = "docs/src/routes/docs"
    
    # Clean up target directory to remove stale files
    if os.path.exists(target_docs):
        import shutil
        shutil.rmtree(target_docs)
    os.makedirs(target_docs)

    languages = [d for d in os.listdir(base_docs) if os.path.isdir(os.path.join(base_docs, d))]
    
    for lang in languages:
        lang_src = os.path.join(base_docs, lang)
        lang_dest = os.path.join(target_docs, lang)
        
        if not os.path.exists(lang_dest):
            os.makedirs(lang_dest)
        # Create __init__.py for the language directory
        with open(os.path.join(lang_dest, "__init__.py"), "w") as f: pass

        for root, dirs, files in os.walk(lang_src):
            # Create subdirectories in destination
            for d in dirs:
                # Clean directory name (remove 01. prefix and slugify)
                clean_d = slugify(re.sub(r'^\d+\.\s*', '', d))
                dest_dir = os.path.join(lang_dest, clean_d)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                # Create __init__.py
                with open(os.path.join(dest_dir, "__init__.py"), "w") as f: pass

            for f in files:
                if f.endswith(('.md', '.mdx', '.nexy')):
                    src_file = os.path.join(root, f)
                    
                    # Construct destination path
                    rel_root = os.path.relpath(root, lang_src)
                    if rel_root == '.':
                        clean_rel_root = ''
                    else:
                        # Split path and slugify each part
                        parts = rel_root.split(os.sep)
                        clean_rel_root = os.path.join(*[slugify(re.sub(r'^\d+\.\s*', '', p)) for p in parts])
                    
                    # If it's already a .nexy file, keep it, otherwise use .mdx
                    ext = '.nexy' if f.endswith('.nexy') else '.mdx'
                    clean_f = slugify(re.sub(r'^\d+\.\s*', '', f).replace('.mdx', '').replace('.md', '').replace('.nexy', '')) + ext
                    
                    # Ensure subdirectories for nested files are created
                    dest_file_dir = os.path.join(lang_dest, clean_rel_root)
                    if not os.path.exists(dest_file_dir):
                        os.makedirs(dest_file_dir)
                    
                    dest_file = os.path.join(dest_file_dir, clean_f)
                    
                    with open(src_file, 'r', encoding='utf-8') as sf:
                        content = sf.read()
                        
                        if f.endswith('.nexy'):
                            # For .nexy files, we just copy them as is, but maybe wrap if needed?
                            # Usually .nexy files in _docs would be full components.
                            with open(dest_file, 'w', encoding='utf-8') as df:
                                df.write(content)
                            continue

                        title, desc = get_frontmatter(content)
                        body = clean_markdown(content)
                        
                        # Generate MDX content
                        # We import common components for DX
                        nexy_content = f"""---
from "@/components/docs/DocLayout.nexy" import DocLayout
from "@/components/docs/Callout.nexy" import Callout
from "@/components/docs/Step.nexy" import Step

title: prop[str] = "{title or 'Documentation'}"
description: prop[str] = "{desc or 'Documentation for ' + (title or 'Nexy')}"
lang: prop[str] = "{lang}"
---
<DocLayout title="{{title}}" description="{{description}}" lang="{{lang}}">

{body}

</DocLayout>
"""
                        with open(dest_file, 'w', encoding='utf-8') as df:
                            df.write(nexy_content)
                            
    print("Documentation synchronization complete.")

if __name__ == "__main__":
    sync_docs()
