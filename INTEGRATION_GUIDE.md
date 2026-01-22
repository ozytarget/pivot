# 🔗 INTEGRACIÓN STREAMLIT + PINE SCRIPT

## ¿Cómo funciona?

### Paso 1: Procesa datos en Streamlit (app.py)
1. Carga tus archivos CSV (skew_analysis, max_pain, gamma_exposure)
2. La app calcula y visualiza las zonas OI
3. **Al final, verás una sección "Export to Pine Script"**

### Paso 2: Genera datos para Pine Script
1. Click en botón **"🔄 Generate Pine Script Data"**
2. Aparecerá un text area con los datos en formato:
   ```
   Strike,CallOI,PutOI
   145,1000,2000
   150,1500,1800
   155,2000,1200
   ```

### Paso 3: Copia y pega en Pine Script
1. **Copia todo el texto** del text area
2. Abre el archivo `OI_Zones_DataImport.pine` en TradingView
3. En la sección **"📊 Pega aquí los datos"**, pega el texto

### Paso 4: Disfruta la visualización
- Pine Script automáticamente:
  - Detecta clusters de OI (como app.py)
  - Dibuja zonas CALL (rojo) y PUT (verde)
  - Muestra líneas de referencia (PIVOT, MAX PAIN, MAX GAMMA)

---

## 📁 Archivos necesarios

### Streamlit (Python)
- **Ubicación:** `c:\Users\urbin\cALCULO\app.py`
- **Función:** Procesa CSV y exporta datos

### Pine Script
- **Ubicación:** `c:\Users\urbin\Downloads\OI_Zones_DataImport.pine`
- **Función:** Importa datos y visualiza en TradingView

---

## 🔄 Flujo completo

```
CSV Files
    ↓
[app.py procesa]
    ↓
OI Zones Calculator
    ↓
[Genera datos]
    ↓
Formato Strike,CallOI,PutOI
    ↓
[Copias datos]
    ↓
Pine Script Input
    ↓
TradingView Chart
```

---

## ⚙️ Configuración en Pine Script

Una vez pegados los datos, personaliza:
- **Ticker:** Nombre del subyacente
- **Global Pivot:** Strike de equilibrio
- **Max Pain:** Strike de máximo dolor
- **Max Gamma:** Strike de máxima gamma
- **Spot Price:** Precio actual

---

## 📊 Ejemplo de datos exportados

```
Strike,CallOI,PutOI
140,500,5000
145,1200,4500
150,3000,2000
155,2500,1500
160,1000,800
165,400,300
```

Estos números representan:
- **Strike:** Precio del contrato
- **CallOI:** Open Interest total de CALLS en ese strike
- **PutOI:** Open Interest total de PUTS en ese strike

---

## 🎯 Ventajas

✅ **Automático:** app.py calcula todo
✅ **Flexible:** Actualiza datos cuando quieras
✅ **Visualización en TradingView:** Overlay en gráficos reales
✅ **Sin límites:** Trabaja con cualquier cantidad de datos

---

## 🔧 Troubleshooting

**Problema:** Pine Script no muestra datos
- ✓ Asegúrate de pegar el texto COMPLETO (incluido header)
- ✓ Formato debe ser exacto: `Strike,CallOI,PutOI`
- ✓ Sin espacios extras

**Problema:** Streamlit no genera botón de exportación
- ✓ Carga archivos CSV primero
- ✓ Aguarda a que se procesen

**Problema:** Zonas no aparecen en TradingView
- ✓ Verifica que los strikes estén dentro del rango del gráfico
- ✓ Revisa inputs de Pivot, Max Pain, Max Gamma

