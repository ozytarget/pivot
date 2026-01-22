# Railway Deployment Guide - Pivot

## 🚀 Requisitos

- Cuenta en [Railway.app](https://railway.app)
- Repositorio GitHub conectado (este: `ozytarget/pivot`)

## ⚡ Deploy en 3 pasos

### 1️⃣ Ir a Railway.app
https://railway.app

### 2️⃣ Crear nuevo proyecto
- Click en **"New Project"**
- Selecciona **"Deploy from GitHub"**
- Busca y selecciona **`ozytarget/pivot`**

### 3️⃣ Railway automáticamente:
- ✅ Detecta Python
- ✅ Lee `requirements.txt`
- ✅ Usa `Procfile` para comando de inicio
- ✅ Deploy en ~2-3 minutos

## 🔧 Variables de Entorno (Opcional)

En Railway Dashboard → Variables:

```
PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_RUN_ON_SAVE=false
```

## 📊 Verificar Deploy

1. Railway te dará una URL: `https://pivot-xxxx.railway.app`
2. Accede y prueba
3. Ver logs: Railway Dashboard → Logs

## 💰 Pricing Railway

- **Gratis**: $5 crédito/mes (suficiente para apps livianas)
- **Starter**: $20/mes + uso
- **Pro**: $50/mes + uso

Con esta app: **~$2-5/mes** si está activa

## 🆚 Railway vs Alternatives

| Feature | Railway | Heroku | Render | Streamlit Cloud |
|---------|---------|--------|--------|-----------------|
| Precio | $5+/mes | Pago | $7+/mes | Gratis (sleep) |
| Uptime | 24/7 | 24/7 | 24/7 | Depende |
| Deploy | ~2 min | ~2 min | ~2 min | ~2 min |
| Facilidad | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🔗 Enlaces útiles

- [Railway Docs](https://docs.railway.app)
- [Streamlit + Railway](https://docs.railway.app/plugins/streamlit)
- [Dashboard](https://railway.app/dashboard)

---

**Última actualización**: Enero 22, 2026
