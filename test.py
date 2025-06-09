from pathlib import Path
import re

POSTS_DIR = Path("_posts")

# Regex para capturar la parte del nombre de la imagen en la sintaxis markdown
pattern = re.compile(r"!\[Pasted image (\d+\.png)\]\(/assets/media/Pasted image \d+\.png\)")

def renombrar_imagenes_en_posts():
    files_changed = 0
    for post_path in POSTS_DIR.glob("*.md"):
        text = post_path.read_text(encoding="utf-8")
        new_text, count = pattern.subn(r"![\1](/assets/media/\1)", text)
        if count > 0:
            post_path.write_text(new_text, encoding="utf-8")
            print(f"Modificado {post_path.name}, {count} cambios")
            files_changed += 1
    print(f"Total archivos modificados: {files_changed}")

if __name__ == "__main__":
    renombrar_imagenes_en_posts()
