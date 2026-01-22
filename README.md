# Pivot - OI Analysis Tool

**Open Interest (OI) Analysis Dashboard** - Análisis de concentración de contratos en opciones financieras.

## 🎯 Características

- 📊 **Análisis de Clusters OI**: Detecta concentraciones de Open Interest en strikes específicos
- 🔴 **Visualización CALL/PUT**: Diferenciación visual de opciones de compra y venta
- 📈 **Múltiples formatos de datos**: Acepta CSV con diferentes estructuras
- 🎨 **Interfaz Streamlit**: Dashboard interactivo en tiempo real
- 🔍 **Exportación de datos**: Descarga análisis en formato PNG

## 🚀 Instalación Local

### Requisitos
- Python 3.8+
- pip

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/ozytarget/pivot.git
cd pivot
```

2. **Crear entorno virtual (opcional pero recomendado)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

La app estará disponible en: **http://localhost:8501**

## 📝 Uso

1. **Ingresa datos de opciones**:
   - Pega CSV con formato: `strike,option_type,open_interest,volume`
   - O usa el generador de datos de ejemplo

2. **Visualiza clusters**:
   - Las áreas roja/verde muestran concentraciones de CALL/PUT
   - Los números indican Open Interest

3. **Exporta resultados**:
   - Descarga gráficos en PNG
   - Copia datos a portapapeles

## 📊 Formatos de Datos Soportados

### Formato 1: Vertical
```
strike,option_type,open_interest,volume
5.0,call,1022,43
5.0,put,0,0
```

### Formato 2: Horizontal (Gamma)
```
Strike,CALL_Gamma,PUT_Gamma,CALL_OI,PUT_OI
100.0,0.0,0.0,0,0
105.0,3.37e-16,0.0,0,100
```

### Formato 3: Compacto
```
Strike,CallOI,PutOI
100,1000,500
105,800,600
```

## 🔧 Configuración

En `app.py`:
- `MAX_CLUSTERS`: Máximo número de clusters a mostrar (default: 2)
- `OPACITY`: Transparencia de zonas (0-100)
- `TAMAÑO_FUENTE`: Pequeño/Normal/Grande

## 📦 Dependencias

- **streamlit**: Framework web interactivo
- **pandas**: Procesamiento de datos
- **numpy**: Cálculos numéricos
- **matplotlib**: Visualización (fallback)
- **plotly**: Gráficos interactivos (opcional)
- **yfinance**: Datos de mercado (opcional)

## 🌐 Deployment en Nube

### Streamlit Cloud (Recomendado)
1. Fork este repositorio a tu cuenta de GitHub
2. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
3. Conecta tu repo
4. Deploy automático

### Heroku
```bash
heroku login
heroku create pivot-app
git push heroku main
```

### AWS / GCP / Azure
- Requiere configuración de máquina virtual
- Ver `INTEGRATION_GUIDE.md` para detalles

## 📚 Documentación

- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) - Guía completa de integración

## 🐛 Troubleshooting

### "Port already in use"
```bash
streamlit run app.py --server.port=8502
```

### Errores de imports
```bash
pip install --upgrade -r requirements.txt
```

### Datos no se muestran
- Verifica el formato CSV
- Asegúrate que hay al menos 2 rows (header + data)
- Los valores deben ser numéricos

## 📄 Licencia

MIT License

## 👥 Autor

**Deploy Bot** - Automated deployment system

## 🔗 Enlaces

- [GitHub](https://github.com/ozytarget/pivot)
- [Documentación](./INTEGRATION_GUIDE.md)

---

**Última actualización**: Enero 22, 2026
