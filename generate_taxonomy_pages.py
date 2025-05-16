import os
import re
from collections import defaultdict

POSTS_DIR = "_posts"
CATEGORIES_DIR = "categories"
TAGS_DIR = "tags"

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.strip().lower())

def extract_frontmatter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    frontmatter = re.search(r'^---(.*?)---', content, re.DOTALL)
    if frontmatter:
        yaml = frontmatter.group(1)
        categories = re.findall(r'categories:\s*\[(.*?)\]', yaml)
        tags = re.findall(r'tags:\s*\[(.*?)\]', yaml)
        cat_list = [c.strip() for cat in categories for c in cat.split(',')]
        tag_list = [t.strip() for tag in tags for t in tag.split(',')]
        return cat_list, tag_list
    return [], []

def collect_terms():
    all_categories = set()
    all_tags = set()

    for filename in os.listdir(POSTS_DIR):
        if filename.endswith(".md"):
            cats, tags = extract_frontmatter(os.path.join(POSTS_DIR, filename))
            all_categories.update(cats)
            all_tags.update(tags)
    return all_categories, all_tags

def write_md_file(name, slug, layout, folder):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{slug}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"""---
layout: {layout}
title: {name}
permalink: /{folder}/{slug}/
---
""")
    print(f"✅ Created: {filepath}")

def main():
    categories, tags = collect_terms()

    print("\n📁 Generating category pages...")
    for cat in categories:
        slug = slugify(cat)
        write_md_file(cat, slug, "category", CATEGORIES_DIR)

    print("\n🏷️ Generating tag pages...")
    for tag in tags:
        slug = slugify(tag)
        write_md_file(tag, slug, "tag", TAGS_DIR)

if __name__ == "__main__":
    main()
