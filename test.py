import os
import re

# Directorio donde se encuentran las imágenes
media_dir = "assets/media/"

# Función para renombrar las imágenes y eliminar el prefijo "Pasted-image-"
def rename_images():
    for filename in os.listdir(media_dir):
        # Comprobamos si la imagen tiene el prefijo "Pasted-image-"
        if filename.startswith("Pasted-image-"):
            new_name = filename[len("Pasted-image-"):]  # Eliminar el prefijo "Pasted-image-"
            old_path = os.path.join(media_dir, filename)
            new_path = os.path.join(media_dir, new_name)
            
            # Renombramos el archivo
            os.rename(old_path, new_path)
            print(f"Renombrado: {filename} -> {new_name}")

# Función para actualizar las rutas en los archivos .md
def update_image_paths(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Reemplazamos las rutas de las imágenes con los nuevos nombres sin el prefijo "Pasted-image-"
    content = re.sub(
        r'!\[([^\]]+)\]\(/assets/media/([^\)]+)\)',
        lambda m: f'![{m.group(1)}](/assets/media/{m.group(2)})',
        content
    )

    # Escribimos el contenido actualizado en el archivo
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Función para procesar todos los archivos .md en _posts
def process_md_files():
    post_dir = "_posts/"
    
    # Recorrer todos los archivos .md
    for filename in os.listdir(post_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(post_dir, filename)
            update_image_paths(file_path)
            print(f"Actualizado: {filename}")

# Paso 1: Renombrar las imágenes en assets/media
rename_images()

# Paso 2: Actualizar las rutas en los archivos markdown
process_md_files()

print("¡Renombrado y actualizado con éxito!")
