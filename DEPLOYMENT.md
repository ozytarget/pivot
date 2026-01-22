# Pivot - Opciones de Deployment

Este documento describe las diferentes formas de hacer deploy de Pivot en producción.

## 📋 Tabla de Contenidos

1. [Local Development](#local-development)
2. [Streamlit Cloud](#streamlit-cloud)
3. [Docker](#docker)
4. [Heroku](#heroku)
5. [AWS](#aws)
6. [Variables de Entorno](#variables-de-entorno)

---

## Local Development

### Requisitos
- Python 3.8+
- git

### Setup

```bash
# Clonar
git clone https://github.com/ozytarget/pivot.git
cd pivot

# Entorno virtual
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows

# Dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

Acceso: http://localhost:8501

---

## Streamlit Cloud (⭐ Recomendado para inicio rápido)

### Pasos

1. **Fork el repositorio** a tu cuenta de GitHub
2. **Crea cuenta** en [streamlit.io/cloud](https://streamlit.io/cloud)
3. **Click "New app"**
4. **Selecciona**:
   - Repository: `tu-usuario/pivot`
   - Branch: `main`
   - File: `app.py`
5. **Deploy** (automático en ~2 minutos)

### Ventajas
✅ Gratis para uso personal  
✅ Deploy automático con cada push  
✅ HTTPS incluido  
✅ No requiere servidor  

### URL resultante
```
https://[proyecto-id]-pivot.streamlit.app
```

### Limitaciones
⚠️ Inactividad después de 7 días (sleep)  
⚠️ Reinicia después de push  
⚠️ Limitado a 1GB memoria  

---

## Docker

### Crear imagen

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build & Run

```bash
# Build
docker build -t pivot:latest .

# Run local
docker run -p 8501:8501 pivot:latest

# Run con variables
docker run -p 8501:8501 \
  -e DEBUG=true \
  pivot:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  pivot:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - ./data:/app/data
```

Ejecutar: `docker-compose up`

---

## Heroku

### Requisitos
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Cuenta Heroku

### Deploy

```bash
# Login
heroku login

# Crear app
heroku create pivot-app-demo

# Variables
heroku config:set DEBUG=true

# Deploy
git push heroku main

# Logs
heroku logs --tail

# Acceso
heroku open
```

### Procfile

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Costo
- Gratis: Dyno gratuito (duerme después de 30 min)
- Pago: $50/mes básico (24/7)

---

## AWS (Elastic Beanstalk)

### Requisitos
- AWS Account
- [AWS CLI](https://aws.amazon.com/cli/)
- [EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)

### Deploy

```bash
# Inicializar
eb init -p python-3.10 pivot-app

# Crear ambiente
eb create pivot-prod

# Deploy
eb deploy

# Abrir
eb open

# Ver logs
eb logs
```

### `.ebextensions/streamlit.config`

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.py
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.micro
```

### Costo (estimado)
- EC2: ~$10/mes
- RDS (si usa BD): ~$15/mes

---

## GCP (App Engine)

### Requisitos
- [Google Cloud SDK](https://cloud.google.com/sdk)
- GCP Project

### Deploy

```bash
# Configurar proyecto
gcloud config set project PROJECT_ID

# Deploy
gcloud app deploy

# URL
gcloud app browse
```

### `app.yaml`

```yaml
runtime: python310

env: standard

entrypoint: streamlit run app.py --server.port=8080 --server.address=0.0.0.0

env_variables:
  STREAMLIT_SERVER_HEADLESS: "true"
```

### Costo
- Gratis: $0-28/mes (siempre activo)
- Pago: según uso

---

## Azure (App Service)

### Deploy

```bash
# Login
az login

# Crear grupo
az group create -n pivot-group -l eastus

# Crear app service
az appservice plan create \
  -n pivot-plan \
  -g pivot-group \
  --sku B1

# Deploy
az webapp create \
  -n pivot-app \
  -g pivot-group \
  -p pivot-plan \
  --runtime "PYTHON|3.10"

# Push
git remote add azure [URL]
git push azure main
```

### Costo
- Plan B1: ~$55/mes

---

## Variables de Entorno

Crear `.streamlit/secrets.toml`:

```toml
# API Keys
YFINANCE_KEY = "xxx"

# Database
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASS = "secret"

# General
DEBUG = false
MAX_CLUSTERS = 2
OPACITY = 70
```

Acceder en código:

```python
import streamlit as st

debug = st.secrets.get("DEBUG", False)
max_clusters = st.secrets.get("MAX_CLUSTERS", 2)
```

---

## Comparativa de Opciones

| Opción | Costo | Complejidad | Velocidad | Soporte | 
|--------|-------|-------------|-----------|---------|
| Streamlit Cloud | Gratis | Muy baja | ⚡⚡⚡ | Oficial |
| Docker + VPS | $5-20 | Media | ⚡⚡⚡ | Comunidad |
| Heroku | Gratis/Pago | Baja | ⚡⚡ | Oficial |
| AWS EB | $10-100 | Alta | ⚡⚡⚡ | Oficial |
| GCP App Engine | $0-100 | Media | ⚡⚡⚡ | Oficial |
| Azure | $55+ | Media | ⚡⚡⚡ | Oficial |

---

## 🚀 Recomendación

Para **inicio rápido**: **Streamlit Cloud**  
Para **producción**: **Docker + AWS/GCP**  
Para **máxima flexibilidad**: **Docker + VPS**

---

## 📚 Referencias

- [Streamlit Docs](https://docs.streamlit.io)
- [Docker Hub](https://hub.docker.com)
- [Heroku Docs](https://devcenter.heroku.com)
- [AWS EB](https://aws.amazon.com/elasticbeanstalk/)

---

**Última actualización**: Enero 22, 2026
