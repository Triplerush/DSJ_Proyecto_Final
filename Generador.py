import os

# ==========================================
# CONFIGURACIÓN
# ==========================================

# El directorio raíz es donde está este mismo archivo
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))

# Nombre del archivo final
NOMBRE_SALIDA = 'codigo_proyecto_compilado.txt'
RUTA_SALIDA = os.path.join(DIRECTORIO_RAIZ, NOMBRE_SALIDA)

# Extensiones permitidas
EXTENSIONES = ('.py', '.spec', '.kv')

# Carpetas a ignorar (para no leer librerías ni basura)
IGNORAR_CARPETAS = {
    '__pycache__', 'venv', 'env', '.git', '.idea', 
    '.vscode', 'build', 'dist', 'egg-info','bin','.buildozer'
}

# Nombre de este script para no incluirlo en el escaneo
NOMBRE_SCRIPT = os.path.basename(__file__)

def leer_contenido(ruta):
    """Lee el archivo intentando utf-8."""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Error leyendo archivo]: {e}"

def formatear_salida(nombre, ruta, contenido):
    separador = "=" * 60
    return f"{separador}\nARCHIVO: {nombre}\nRUTA: {ruta}\n{contenido}\n\n"

def procesar_proyecto():
    print(f"--- Escaneando desde: {DIRECTORIO_RAIZ} ---")
    partes = []
    archivos_encontrados = 0

    for root, dirs, files in os.walk(DIRECTORIO_RAIZ):
        # 1. Limpiar carpetas que no queremos recorrer (modifica la lista in-place)
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]

        for nombre in files:
            # 2. Filtrar por extensión
            if nombre.endswith(EXTENSIONES):
                
                # 3. EXCLUIR este mismo script y el archivo de salida
                if nombre == NOMBRE_SCRIPT or nombre == NOMBRE_SALIDA:
                    continue

                ruta_completa = os.path.join(root, nombre)
                print(f"Procesando: {nombre}")
                
                contenido = leer_contenido(ruta_completa)
                partes.append(formatear_salida(nombre, ruta_completa, contenido))
                archivos_encontrados += 1

    # Guardar todo
    if partes:
        with open(RUTA_SALIDA, 'w', encoding='utf-8') as f:
            f.write("".join(partes))
        print(f"\n✔ ÉXITO. {archivos_encontrados} archivos guardados en: {NOMBRE_SALIDA}")
    else:
        print("\n⚠ No se encontraron archivos .py, .spec o .kv aquí.")

if __name__ == '__main__':
    procesar_proyecto()