# 📸 Guía para Agregar Imágenes

## 📁 Estructura de Carpetas

La aplicación ya tiene creada automáticamente la carpeta `images/` donde debes colocar tus archivos.

```
social_media_matrix/
├── app.py
├── data/
│   ├── cuentas.csv
│   └── metricas.csv
└── images/          ← COLOCA TUS IMÁGENES AQUÍ
    ├── logo_maristas.png          (Logo principal)
    ├── banner_landing.jpg         (Fondo de página inicio)
    └── icon_maristas.png          (Ícono opcional)
```

---

## 🎨 Imágenes Necesarias

### 1. **Logo Principal** (`logo_maristas.png`)
- **Ubicación**: Aparece en el menú lateral izquierdo
- **Formato recomendado**: PNG con fondo transparente
- **Tamaño ideal**: 400x400px (se redimensiona automático)
- **Peso máximo**: 500KB

### 2. **Banner de Landing Page** (`banner_landing.jpg`)
- **Ubicación**: Fondo de la página de inicio (hero banner)
- **Formato recomendado**: JPG o PNG
- **Tamaño ideal**: 1920x600px (formato panorámico)
- **Peso máximo**: 2MB
- **Sugerencia**: Usa una imagen de campus, estudiantes, o institucional

### 3. **Ícono** (`icon_maristas.png`) - Opcional
- **Formato**: PNG
- **Tamaño**: 128x128px
- **Uso futuro**: Para favicons o badges

---

## 📥 Cómo Agregar tus Imágenes

### Opción 1: Arrastrar y Soltar
1. Abre la carpeta del proyecto: `f:\MATRIZ DE REDES\social_media_matrix\`
2. Entra a la carpeta `images/`
3. Arrastra tus imágenes con los nombres exactos:
   - `logo_maristas.png`
   - `banner_landing.jpg`

### Opción 2: Copiar y Pegar
1. Copia tus imágenes
2. Pégalas en `f:\MATRIZ DE REDES\social_media_matrix\images\`
3. Renómbralas exactamente como se indica arriba

### Opción 3: Desde PowerShell
```powershell
# Navegar a la carpeta images
cd "f:\MATRIZ DE REDES\social_media_matrix\images"

# Copiar imágenes desde otra ubicación
Copy-Item "C:\ruta\origen\tu_logo.png" -Destination "logo_maristas.png"
Copy-Item "C:\ruta\origen\tu_banner.jpg" -Destination "banner_landing.jpg"
```

---

## ✅ Verificación

Después de agregar las imágenes:

1. **Reinicia Streamlit** (presiona `R` en la terminal o refresca el navegador)
2. Verifica que aparezcan:
   - Logo en el **menú lateral izquierdo** (esquina superior)
   - Banner de fondo en la **página de Inicio**

---

## 🎨 Recomendaciones de Diseño

### Para el Logo:
- Fondo transparente
- Colores institucionales (azul #003696)
- Legible en tamaño pequeño
- Evita degradados complejos

### Para el Banner:
- Colores corporativos o imágenes institucionales
- Evita texto en la imagen (se superpone con overlay azul)
- Resolución alta para pantallas grandes
- Contraste medio (el overlay oscurece automáticamente)

---

## 🔧 ¿Qué pasa si no agregas imágenes?

**No hay problema.** La aplicación usa imágenes de respaldo (fallback):
- Logo: Imagen pública de Wikipedia de Maristas
- Banner: Imagen profesional de Unsplash (estudiantes universitarios)

Tu app funcionará perfectamente, solo que con imágenes genéricas.

---

## 🖼️ Recursos Gratuitos de Imágenes

Si necesitas imágenes temporales:

- **Unsplash**: https://unsplash.com/s/photos/education
- **Pexels**: https://www.pexels.com/search/university/
- **Freepik**: https://www.freepik.com/ (requiere atribución)

**Banners educativos sugeridos**:
- Estudiantes colaborando
- Campus universitario
- Libros y tecnología
- Aulas modernas

---

## 📞 Soporte

Si las imágenes no aparecen:

1. Verifica que los nombres sean **exactos** (mayúsculas/minúsculas)
2. Confirma que estén en la carpeta `images/`
3. Revisa la consola de PowerShell por errores
4. Refresca el navegador con `Ctrl + F5`

---

¡Listo! Una vez agregadas las imágenes, tu dashboard tendrá la identidad visual completa de los Maristas. 🎓✨
