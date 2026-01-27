# 🚀 GUÍA PARA PUBLICAR EN GITHUB

Felicidades! Tu aplicación está lista para ser publicada en GitHub. Sigue estos pasos:

---

## ✅ Pre-Requisitos Completados

- [x] **CI/CD Workflow Corregido**: `.github/workflows/ci.yml` ahora tiene sintaxis YAML correcta
- [x] **.gitignore Mejorado**: Incluye todos los archivos sensibles y generados
- [x] **Debug Statements Removidos**: Código limpio, sin print() de debug
- [x] **Documentación de Contribución**: `CONTRIBUTING.md` creado
- [x] **Licencia**: `LICENSE` (MIT) añadida
- [x] **Templates de Issues y PRs**: `.github/ISSUE_TEMPLATE/` y `.github/PULL_REQUEST_TEMPLATE.md`
- [x] **README.md**: Ya estaba actualizado y completo
- [x] **SECURITY.md**: Guía de seguridad completa

---

## 📝 Paso a Paso para Publicar

### 1. Verificar Local (5 min)

```bash
# Ir a la carpeta del proyecto
cd "f:\MATRIZ DE REDES\social_media_matrix"

# Activar entorno virtual
.\venv_stable\Scripts\Activate.ps1

# Ejecutar tests
pytest

# Verificar linting
ruff check .
black --check .

# Si todo pasó:
echo "✅ Local verification passed"
```

### 2. Crear Repositorio en GitHub (10 min)

1. Ve a https://github.com/new
2. **Nombre del repositorio**: `Matriz-de-Redes-Maristas` (o `ChampiLeaks`)
3. **Descripción**: 
   ```
   🎯 Plataforma de inteligencia digital para análisis de métricas de redes sociales de instituciones maristas en México
   ```
4. **Visibilidad**: Public (si quieres compartir)
5. **NO INICIALICES** con README.md (ya tienes uno)
6. **NO INICIALICES** con .gitignore (ya tienes uno)
7. Clic en "Create repository"

### 3. Conectar Repositorio Local (10 min)

```powershell
# Ya tienes .git inicializado, pero asegúrate:
cd "f:\MATRIZ DE REDES\social_media_matrix"

# Ver el remoto actual (probablemente no tengas uno)
git remote -v

# Si NO hay remoto, agregar:
# Reemplaza USUARIO con tu usuario de GitHub
git remote add origin https://github.com/USUARIO/Matriz-de-Redes-Maristas.git

# Si ya existe y quieres cambiarlo:
# git remote set-url origin https://github.com/USUARIO/Matriz-de-Redes-Maristas.git

# Verificar
git remote -v
# Debería mostrar: origin  https://github.com/USUARIO/Matriz-de-Redes-Maristas.git
```

### 4. Hacer Commit Limpio (5 min)

```powershell
# Verificar estado
git status

# Agregar todos los cambios
git add .

# Crear commit
git commit -m "Initial commit: CHAMPILEAKS v2.1.0 - Production Ready"
```

### 5. Crear Ramas (2 min)

```powershell
# La rama actual es 'main' (o 'master')
# Crear rama develop para desarrollo
git branch develop

# Ver todas las ramas
git branch -a
```

### 6. Push a GitHub (2 min)

```powershell
# OPCIÓN A: Si tienes SSH configurado
git push -u origin main
git push -u origin develop

# OPCIÓN B: Si usas HTTPS (te pedirá credenciales)
# Git guardará las credenciales en el gestor de contraseñas de Windows
git push -u origin main
git push -u origin develop
```

Espera a que termine... ¡Listo! Tu repositorio está en GitHub.

---

## 🌐 Configurar Streamlit Cloud (15 min)

### 1. Ir a Streamlit Cloud

1. Ve a https://streamlit.io/cloud
2. Haz clic en "Sign up" o "Sign in"
3. Conéctate con tu cuenta de GitHub

### 2. Deploy la Aplicación

1. Click en "New app"
2. **Repository**: `USUARIO/Matriz-de-Redes-Maristas`
3. **Branch**: `main`
4. **Main file path**: `app.py`
5. Click en "Deploy"

### 3. Configurar Secrets

1. Una vez desplegada, ve a Settings (engranaje arriba a la derecha)
2. Click en "Secrets"
3. Copia el contenido de tu `.streamlit/secrets.toml` local
4. Pégalo en el editor de secrets de Streamlit Cloud
5. Guarda

Ejemplo:
```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

[GOOGLE_SHEETS_ID]
sheets_id = "tu-id-aqui"
```

### 4. Verificar Que Funciona

La URL de tu app será:
```
https://usuario-matriz-de-redes.streamlit.app
```

(Reemplaza `usuario` con tu nombre de usuario de GitHub)

---

## 🔒 Seguridad: Verificar que NO subiste Datos Sensibles

```powershell
# Verificar que .env NO está en GitHub
git log --all --full-history -- .env

# Debería mostrar: fatal: your current branch does not have any commits yet
# O no mostrar el archivo

# Verificar que .streamlit/secrets.toml NO está en GitHub
git log --all --full-history -- .streamlit/secrets.toml

# Mismo resultado esperado

# Confirmar archivos en el repositorio
git ls-tree -r HEAD

# Verificar que no hay credenciales en el código
git grep -i "private_key\|password\|secret" HEAD

# No debería encontrar nada o solo en comentarios
```

---

## 📊 Activar GitHub Actions (2 min)

Tu workflow CI/CD ya está configurado. Verificar que funcione:

1. Ve a tu repositorio en GitHub
2. Click en "Actions"
3. Debería haber un workflow ejecutándose automáticamente
4. Si falla, revisa los logs (click en el workflow)

---

## ✨ Extras (Opcional)

### Agregar Badge de Status en README

Añade esto al principio de tu README.md:

```markdown
[![Tests](https://github.com/USUARIO/Matriz-de-Redes-Maristas/actions/workflows/ci.yml/badge.svg)](https://github.com/USUARIO/Matriz-de-Redes-Maristas/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://usuario-matriz-de-redes.streamlit.app)
```

### Agregar a `.github/workflows/ci.yml` (Opcional)

Para enviar reportes de cobertura a Codecov (gratuito):

```yaml
# Agregar después del step "Run tests with coverage"
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
```

Luego:
1. Ve a https://codecov.io
2. Conecta tu repositorio
3. Copia el token
4. En GitHub: Settings → Secrets → New repository secret
5. Nombre: `CODECOV_TOKEN`, Valor: el token

---

## 🎯 Checklist Final

Antes de considerar que completaste:

- [ ] Repositorio creado en GitHub
- [ ] Código pusheado a GitHub (ramas main y develop)
- [ ] Tests pasan localmente: `pytest`
- [ ] GitHub Actions ejecutándose correctamente
- [ ] Streamlit Cloud desplegada
- [ ] Secrets configurados en Streamlit Cloud
- [ ] Aplicación funciona en Streamlit Cloud
- [ ] No hay archivos sensibles en GitHub
- [ ] README.md visible en GitHub
- [ ] CONTRIBUTING.md presente
- [ ] LICENSE presente
- [ ] Templates de Issues funcionando

---

## 📞 Soporte

### Si algo sale mal:

**Problema**: "Permission denied" en git push
```bash
# Solución: Usar SSH en lugar de HTTPS
# O: Usar token de GitHub en lugar de contraseña
```

**Problema**: "fatal: not a git repository"
```bash
# Solución: Ejecutar desde la carpeta correcta
# cd "f:\MATRIZ DE REDES\social_media_matrix"
```

**Problema**: Streamlit Cloud no conecta a Google Sheets
```
Verificar que secrets.toml esté configurado correctamente
Revisar que private_key tenga formato correcto (con saltos de línea)
```

**Problema**: Tests fallan en GitHub Actions pero pasan localmente
```
Verificar que requirements.txt esté actualizado
Asegurar que no hay paths absolutos en el código
```

---

## 🎉 ¡Listo!

Tu aplicación está en GitHub y en Streamlit Cloud. Ahora puedes:

- Compartir el link: `https://usuario-matriz-de-redes.streamlit.app`
- Colaborar con otros en GitHub
- Usar GitHub Issues para tracking
- Automatizar tests y deployment

**¡Felicidades por llegar a producción!** 🚀

---

**Próximos Pasos (Futuro)**:
- Configurar protección de rama main (require reviews)
- Agregar más tests
- Implementar autenticación de usuarios
- Multi-idioma (EN/ES)
- API REST

**Generado**: 12 Enero 2026  
**Versión de App**: 2.1.0
