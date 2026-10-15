# traer cambios a mi directorio local
# 1. Traer e integrar los cambios de GitHub a tu carpeta local
git pull origin main --rebase

# 2. Volver a subir tus cambios locales
git push origin main


# Subir cambios a git
## 1. Añadir todos los cambios o nuevos artículos convertidos
git add .

## 2. Guardar los cambios localmente con un mensaje descriptivo
git commit -m "feat: descripción de lo que has añadido o modificado"

## 3. Subir los cambios a GitHub (desplegando automáticamente la web y el feed RSS)
´´´
git push origin main


## generar html desde .md contenido
ejecutar el python: build_blog.py del directorio raíz.