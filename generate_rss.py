import os
import re
from datetime import datetime

# Configuración del blog
SITE_TITLE = "José Villa | Blog Técnico"
SITE_URL = "https://josevilla.dev"
BLOG_DIR = "blog"
OUTPUT_FILE = "feed.xml"

def extract_meta(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraer título del tag <title> o del <h1> principal
    title_match = re.search(r"<title>(.*?)</title>", content)
    title = title_match.group(1).split("|")[0].strip() if title_match else "Artículo sin título"

    # Extraer meta description
    desc_match = re.search(r'<meta name="description" content="(.*?)">', content)
    description = desc_match.group(1) if desc_match else ""

    # Extraer fecha de publicación del tag <time> (ej. datetime="2026-10-14")
    time_match = re.search(r'<time datetime="(.*?)">', content)
    if time_match:
        date_str = time_match.group(1)
        # Convertir a formato RFC-822 requerido por RSS
        dt = datetime.fromisoformat(date_str)
    else:
        # Fallback a fecha de modificación del archivo
        dt = datetime.fromtimestamp(os.path.getmtime(file_path))

    pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0200")
    
    # Nombre del archivo HTML para construir el enlace
    filename = os.path.basename(file_path)
    link = f"{SITE_URL}/blog/{filename}"

    return {
        "title": title,
        "link": link,
        "description": description,
        "pubDate": pub_date,
        "timestamp": dt.timestamp()
    }

def generate_rss():
    items = []
    
    # Recorrer la carpeta blog/ buscando archivos .html
    for root, _, files in os.walk(BLOG_DIR):
        for file in files:
            if file.endswith(".html") and file != "index.html":
                file_path = os.path.join(root, file)
                meta = extract_meta(file_path)
                items.append(meta)

    # Ordenar los artículos del más reciente al más antiguo
    items.sort(key=lambda x: x["timestamp"], reverse=True)

    # Construir el contenido XML del RSS
    now_str = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0200")
    
    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>{SITE_TITLE}</title>
        <link>{SITE_URL}/blog/index.html</link>
        <description>Artículos sobre desarrollo, ciberseguridad, productividad, ciencia de datos y ecología práctica.</description>
        <language>es</language>
        <lastBuildDate>{now_str}</lastBuildDate>
        <atom:link href="{SITE_URL}/{OUTPUT_FILE}" rel="self" type="application/rss+xml"/>
"""

    for item in items:
        rss_content += f"""
        <item>
            <title>{item["title"]}</title>
            <link>{item["link"]}</link>
            <guid>{item["link"]}</guid>
            <pubDate>{item["pubDate"]}</pubDate>
            <description>{item["description"]}</description>
        </item>"""

    rss_content += """
    </channel>
</rss>
"""

    # Guardar el archivo feed.xml en la raíz
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_content)
    
    print(f"¡Feed RSS generado con éxito! Se han indexado {len(items)} artículos.")

if __name__ == "__main__":
    generate_rss()
