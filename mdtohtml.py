import os
import re
import markdown

def compilar_articulo(ruta_md, ruta_plantilla, ruta_salida):
    # Comprobar si el HTML ya existe y si el Markdown NO ha sido modificado desde la última compilación
    if os.path.exists(ruta_salida):
        tiempo_md = os.path.getmtime(ruta_md)
        tiempo_html = os.path.getmtime(ruta_salida)
        
        # Si el HTML es más moderno o igual que el .md, nos saltamos la compilación
        if tiempo_html >= tiempo_md:
            return False # Indica que no se ha recompilado (sin cambios)

    with open(ruta_md, "r", encoding="utf-8") as f:
        contenido_completo = f.read()

    # 1. Separar metadatos (Frontmatter) y contenido por la primera línea en blanco
    lineas = contenido_completo.splitlines()
    metadata = {}
    indice_contenido = 0
    
    for i, linea in enumerate(lineas):
        if ":" in linea and not linea.startswith("#"):
            partes = linea.split(":", 1)
            metadata[partes[0].strip().lower()] = partes[1].strip()
        elif linea.strip() == "":
            indice_contenido = i + 1
            break

    # 2. Convertir el cuerpo Markdown a HTML (activando bloques de código y tablas)
    cuerpo_md = "\n".join(lineas[indice_contenido:])
    html_cuerpo = markdown.markdown(cuerpo_md, extensions=['fenced_code', 'tables'])

    # 3. Leer la plantilla HTML base
    with open(ruta_plantilla, "r", encoding="utf-8") as f:
        plantilla = f.read()

    # 4. Extraer valores del Frontmatter (con valores por defecto si faltan)
    titulo = metadata.get("titulo", "Artículo del Blog")
    descripcion = metadata.get("descripcion", "Artículo técnico del blog de José Villa.")
    imagen = metadata.get("imagen", "https://josevilla.dev/assets/img/default.png")
    fecha = metadata.get("fecha", "2026-10-15")
    slug = metadata.get("slug", os.path.splitext(os.path.basename(ruta_md))[0])
    
    # Tipos válidos permitidos en el Frontmatter
    tipos_validos = ["TechArticle", "BlogPosting", "NewsArticle", "Article", "ScholarlyArticle"]
    
    schema_type = metadata.get("tipo", "BlogPosting")
    if schema_type not in tipos_validos:
        schema_type = "BlogPosting" # Por defecto si escribes mal el tipo o no pones nada
    # Procesar palabras clave
    keywords_raw = metadata.get("keywords", "Python, Desarrollo Web, Blog")
    keywords_list = [kw.strip() for kw in keywords_raw.split(",")]
    keywords_json_str = ", ".join([f'"{kw}"' for kw in keywords_list])

    url_articulo = f"https://josevilla.dev/blog/{slug}.html"

    # 5. Construir dinámicamente el bloque JSON-LD (Schema.org para IAs / GEO)
    schema_json_ld = f"""<script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "{schema_type}",
      "headline": "{titulo}",
      "description": "{descripcion}",
      "datePublished": "{fecha}",
      "author": {{
        "@type": "Person",
        "name": "José Villa"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "José Villa",
        "url": "https://josevilla.dev"
      }},
      "mainEntityOfPage": {{
        "@type": "WebPage",
        "@id": "{url_articulo}"
      }},
      "keywords": [{keywords_json_str}]
    }}
    </script>"""

    # 6. Inyectar dinámicamente en el HTML de la plantilla
    html_final = plantilla
    html_final = re.sub(r"<title>.*?</title>", f"<title>{titulo} | José Villa</title>", html_final)
    html_final = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{descripcion}">', html_final)
    
    html_final = re.sub(r'<meta property="og:title" content=".*?"\s*/?>', f'<meta property="og:title" content="{titulo}">', html_final)
    html_final = re.sub(r'<meta property="og:description" content=".*?"\s*/?>', f'<meta property="og:description" content="{descripcion}">', html_final)
    html_final = re.sub(r'<meta property="og:image" content=".*?"\s*/?>', f'<meta property="og:image" content="{imagen}">', html_final)
    html_final = re.sub(r'<meta property="og:url" content=".*?"\s*/?>', f'<meta property="og:url" content="{url_articulo}">', html_final)

    html_final = html_final.replace("<!-- SCHEMA_JSON_LD -->", schema_json_ld)
    html_final = html_final.replace("<!-- CONTENT -->", html_cuerpo)

    # 7. Guardar el archivo HTML resultante
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html_final)
    
    print(f"⚡ Compilado (nuevo o modificado): {archivo_nombre_limpio(ruta_md)}")
    return True

def archivo_nombre_limpio(ruta):
    return os.path.basename(ruta)

def compilar_todo():
    ruta_plantilla = "templates/plantilla.html"
    carpeta_contenido = "content"
    carpeta_salida = "blog"

    os.makedirs(carpeta_salida, exist_ok=True)

    if not os.path.exists(carpeta_contenido) or not os.path.exists(ruta_plantilla):
        print("❌ Revisa que existan la carpeta 'content/' y 'templates/plantilla.html'.")
        return

    compilados = 0
    saltados = 0

    for archivo in os.listdir(carpeta_contenido):
        if archivo.endswith(".md"):
            nombre_base = os.path.splitext(archivo)[0]
            ruta_md = os.path.join(carpeta_contenido, archivo)
            ruta_salida = os.path.join(carpeta_salida, f"{nombre_base}.html")
            
            hubo_cambios = compilar_articulo(ruta_md, ruta_plantilla, ruta_salida)
            if hubo_cambios:
                compilados += 1
            else:
                saltados += 1

    print(f"\n🎉 Proceso finalizado: {compilados} artículos actualizados, {saltados} sin cambios (omitidos).")

if __name__ == "__main__":
    compilar_todo()