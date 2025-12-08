# DSJ_Proyecto_Final
# Guía Definitiva: Compilación de APK con Kivy & Buildozer en Zorin OS 17

Esta guía describe paso a paso cómo configurar un entorno limpio en **Zorin OS 17 (o Ubuntu 24.04)** dentro de **VirtualBox** para compilar una aplicación Kivy a Android (APK) sin errores.

> **NOTA:** Esta guía asume que NO se utilizarán entornos virtuales (`venv`) y se instalará todo a nivel global.

---

## 🛠️ 1. Requisitos Previos (VirtualBox)

Antes de encender la máquina virtual, asegúrate de configurar lo siguiente:

1.  **Memoria de Video:** Auméntala al máximo posible (128 MB).
2.  **Aceleración 3D:** Márcala como **Habilitada**.
3.  **Carpetas Compartidas:** Configura una carpeta para pasar archivos entre Windows y Linux, pero **NUNCA** intentes compilar dentro de ella.

---

## 🚀 2. Preparación del Sistema

Abre la terminal en Zorin OS y ejecuta estos comandos en orden.

### 2.1. Actualizar el sistema e instalar herramientas básicas
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-dev build-essential
```

### 2.2. Instalar dependencias de compilación (Ingredientes vitales)
Estas librerías son necesarias para que Buildozer pueda construir Python para Android (soporte para SSL, ZIP, Imágenes, etc.).
```bash
sudo apt install -y libffi-dev libssl-dev libjpeg-dev zlib1g-dev \
    autoconf automake libtool pkg-config cmake unzip zip \
    libncurses-dev libportmidi-dev libswscale-dev libavformat-dev \
    libavcodec-dev libsqlite3-dev libbz2-dev liblzma-dev \
    libgdbm-dev libgdbm-compat-dev libreadline-dev uuid-dev
```

## 🐍 3. Instalación de Buildozer y Python
Al no usar entorno virtual en Linux moderno, debemos usar la bandera --break-system-packages.
```bash
# 1. Actualizar pip
pip3 install --upgrade pip --break-system-packages

# 2. Instalar Buildozer, Cython y Pillow
# IMPORTANTE: Kivy 2.3.0 requiere Cython 3.0 o superior
pip3 install buildozer "Cython>=3.0.0" pillow --break-system-packages

# 3. Instalar dependencias internas de Buildozer manualmente
# (Esto evita el error "externally-managed-environment" durante la compilación)
pip3 install appdirs "colorama>=0.3.3" jinja2 "sh>=1.10,<2.0" \
    build toml packaging setuptools --break-system-packages
```

## 📂 4. Preparación del Proyecto (CRÍTICO)
**ADVERTENCIA:** Windows no permite crear "enlaces simbólicos". Si intentas compilar en el Escritorio (si es compartido) o en /media/sf_Compartida, fallará.

### 4.1. Crear un espacio de trabajo nativo en Linux
```bash
cd ~
mkdir Proyectos_Android
cd Proyectos_Android
```

### 4.2. Traer tu proyecto
Copia tu proyecto desde tu carpeta compartida o clónalo aquí.
```bash
# Ejemplo copiando desde una carpeta compartida llamada "Windows":
cp -r ~/Escritorio/Windows/DSJ_Proyecto_Final .
```

## ⚙️ 5. Configuración de Archivos
Antes de compilar, verifica estos archivos en tu proyecto para evitar errores de versión o congelamientos.

### A) Archivo buildozer.spec
Edita la línea de requerimientos para evitar conflictos entre versiones viejas y nuevas:
```ini
requirements = python3,kivy==2.3.0,Cython>=3.0.0,pillow
```

### B) Archivo game/collision.py (Si aplica)
Asegúrate de que tus bucles while tengan un límite de seguridad para que el juego no se congele en el celular:
```python
# Ejemplo de seguridad
loop_count = 0
while loop_count < 10 and colision_detectada:
    # mover objeto...
    loop_count += 1
```

## 🛡️ 6. El "Paso Mágico" (Evitar contaminación)
En Zorin 17/Ubuntu 24.04, si tienes instaladas las librerías de desarrollo gráfico (sdl2) en el sistema, Buildozer se confunde y usa las de la PC en lugar de las de Android, causando errores como __GNUC_PREREQ.

Ejecuta esto para eliminarlas antes de compilar:
```bash
sudo apt remove -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

## 🏗️ 7. Compilación
Asegúrate de estar dentro de la carpeta del proyecto:
```bash
cd ~/Proyectos_Android/DSJ_Proyecto_Final
```

### 7.1. Limpieza total (Recomendado la primera vez)
Esto borra cualquier configuración corrupta anterior.
```bash
rm -rf .buildozer
```

### 7.2. Generar la APK
Este proceso tomará entre 15 y 30 minutos la primera vez (descargará el SDK/NDK de Android).
```bash
buildozer android debug
```

## 📦 8. Finalización
Si ves el mensaje:
```
Bin is ready
```

Tu APK ha sido creada exitosamente en la carpeta bin/. Ahora puedes copiarla a tu carpeta compartida para instalarla en tu móvil.
```bash
# Ejemplo de cómo sacarla a la carpeta compartida de Windows
cp bin/*.apk ~/Escritorio/Windows/
```