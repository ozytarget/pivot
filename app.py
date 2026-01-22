import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import io

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False
    go = None

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except:
    YFINANCE_AVAILABLE = False
    yf = None

# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def detect_clusters(strikes, oi_values, max_clusters=2):
    """
    Detecta hasta max_clusters picos reales de OI y construye rangos contiguos.
    """
    if len(strikes) == 0:
        return []
    
    sorted_idx = np.argsort(strikes)
    strikes_sorted = np.array(strikes)[sorted_idx]
    oi_sorted = np.array(oi_values)[sorted_idx]
    
    if len(strikes_sorted) == 0:
        return []
    
    n_peaks = min(max_clusters, len(oi_sorted))
    top_indices = np.argsort(oi_sorted)[-n_peaks:]
    
    clusters = []
    for idx in top_indices:
        peak_strike = strikes_sorted[idx]
        peak_oi = oi_sorted[idx]
        
        low_idx = idx
        high_idx = idx
        
        while low_idx > 0 and oi_sorted[low_idx-1] > peak_oi * 0.3:
            low_idx -= 1
        
        while high_idx < len(strikes_sorted)-1 and oi_sorted[high_idx+1] > peak_oi * 0.3:
            high_idx += 1
        
        strike_low = strikes_sorted[low_idx]
        strike_high = strikes_sorted[high_idx]
        total_oi = np.sum(oi_sorted[low_idx:high_idx+1])
        
        clusters.append((strike_low, strike_high, total_oi))
    
    clusters.sort(key=lambda x: x[2], reverse=True)
    
    return clusters[:max_clusters]


def calculate_pivot(df_exp, all_strikes):
    """
    Calcula el pivot para un vencimiento específico.
    """
    min_diff = float('inf')
    pivot_strike = None
    
    for s in all_strikes:
        put_below = df_exp[
            (df_exp['option_type'] == 'PUT') & (df_exp['strike'] <= s)
        ]['open_interest'].sum()
        
        call_above = df_exp[
            (df_exp['option_type'] == 'CALL') & (df_exp['strike'] >= s)
        ]['open_interest'].sum()
        
        diff = abs(put_below - call_above)
        
        if diff < min_diff:
            min_diff = diff
            pivot_strike = s
    
    return pivot_strike


def calculate_global_pivot(df_all):
    """
    Calcula el pivot global sumando todos los vencimientos.
    """
    all_strikes = sorted(df_all['strike'].unique())
    min_diff = float('inf')
    pivot_strike = None
    
    for s in all_strikes:
        put_below = df_all[
            (df_all['option_type'] == 'PUT') & (df_all['strike'] <= s)
        ]['open_interest'].sum()
        
        call_above = df_all[
            (df_all['option_type'] == 'CALL') & (df_all['strike'] >= s)
        ]['open_interest'].sum()
        
        diff = abs(put_below - call_above)
        
        if diff < min_diff:
            min_diff = diff
            pivot_strike = s
    
    return pivot_strike


def get_current_price(ticker):
    """
    Obtiene el precio actual del ticker desde Yahoo Finance.
    """
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        data = yf.Ticker(ticker)
        price = data.info.get('currentPrice') or data.history(period='1d')['Close'].iloc[-1]
        return float(price)
    except:
        return None


def find_max_pain(df_max_pain):
    """
    Encuentra el strike con menor pérdida (Max Pain) del archivo max_pain.
    """
    if df_max_pain is None or len(df_max_pain) == 0:
        return None
    
    try:
        # Normalizar nombres de columnas
        df_max_pain.columns = df_max_pain.columns.str.strip().str.lower()
        
        # Buscar columna de loss
        loss_col = None
        for col in df_max_pain.columns:
            if 'loss' in col and 'total' in col:
                loss_col = col
                break
        
        if loss_col is None:
            return None
        
        # Buscar columna de strike
        strike_col = None
        for col in df_max_pain.columns:
            if 'strike' in col:
                strike_col = col
                break
        
        if strike_col is None:
            return None
        
        # Encontrar el strike con menor pérdida
        min_loss_idx = df_max_pain[loss_col].idxmin()
        max_pain_strike = float(df_max_pain.loc[min_loss_idx, strike_col])
        
        return max_pain_strike
    except Exception as e:
        st.warning(f"⚠️ Error calculando Max Pain: {str(e)}")
        return None


def find_gamma_exposure(df_gamma):
    """
    Encuentra el strike con mayor gamma agregada (CALL + PUT) del archivo gamma_exposure.
    """
    if df_gamma is None or len(df_gamma) == 0:
        return None
    
    try:
        # Normalizar nombres de columnas
        df_gamma.columns = df_gamma.columns.str.strip()
        
        # Buscar columnas de gamma
        call_gamma_col = None
        put_gamma_col = None
        
        for col in df_gamma.columns:
            col_lower = col.lower()
            if 'call' in col_lower and 'gamma' in col_lower:
                call_gamma_col = col
            if 'put' in col_lower and 'gamma' in col_lower:
                put_gamma_col = col
        
        if call_gamma_col is None or put_gamma_col is None:
            return None
        
        # Buscar columna de strike
        strike_col = None
        for col in df_gamma.columns:
            if col.lower() == 'strike' or col.lower() == 'strikes':
                strike_col = col
                break
        
        if strike_col is None:
            return None
        
        # Calcular gamma total (valor absoluto para sumar correctamente)
        df_gamma['total_gamma_abs'] = df_gamma[call_gamma_col].abs() + df_gamma[put_gamma_col].abs()
        
        # Encontrar el strike con mayor gamma
        max_gamma_idx = df_gamma['total_gamma_abs'].idxmax()
        gamma_strike = float(df_gamma.loc[max_gamma_idx, strike_col])
        
        return gamma_strike
    except Exception as e:
        st.warning(f"⚠️ Error calculando Gamma Exposure: {str(e)}")
        return None


def clean_strikes(df):
    """
    Limpia los datos eliminando strikes outliers que están muy fuera del rango normal.
    """
    if len(df) == 0:
        return df
    
    Q1 = df['strike'].quantile(0.25)
    Q3 = df['strike'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    
    if lower_bound < 0:
        lower_bound = df['strike'].quantile(0.01)
    if upper_bound < lower_bound:
        upper_bound = df['strike'].max()
    
    df_clean = df[(df['strike'] >= lower_bound) & (df['strike'] <= upper_bound)].copy()
    
    if len(df_clean) == 0:
        return df
    
    return df_clean


# ============================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN DE GRÁFICO
# ============================================================================

def generate_chart(dfs_dict, ticker, spot=None, max_pain=None, gamma_exposure=None):
    """
    Genera el gráfico PNG con todas las especificaciones.
    """
    
    fig_width = 17.92
    fig_height = 10.24
    fig = plt.figure(figsize=(fig_width, fig_height), facecolor='black')
    
    ax_main = fig.add_axes((0.08, 0.12, 0.70, 0.78))
    ax_panel = fig.add_axes((0.80, 0.12, 0.18, 0.78))
    
    ax_main.set_facecolor('black')
    ax_panel.set_facecolor('black')
    ax_panel.axis('off')
    
    df_all = pd.concat(dfs_dict.values(), ignore_index=True)
    
    global_pivot = calculate_global_pivot(df_all)
    
    all_strikes = sorted(df_all['strike'].unique())
    y_min = all_strikes[0]
    y_max = all_strikes[-1]
    y_range = y_max - y_min
    
    ax_main.set_ylim(y_min, y_max)
    ax_main.set_xlim(0, len(dfs_dict) + 1)
    
    ax_main.set_ylabel('Strike Price ($)', color='white', fontsize=12, fontweight='bold')
    ax_main.set_yticks(all_strikes[::max(1, len(all_strikes)//10)])
    ax_main.tick_params(axis='y', colors='white', labelsize=9)
    
    expirations = sorted(dfs_dict.keys())
    date_labels = [exp.strftime('%Y-%m-%d') for exp in expirations]
    ax_main.set_xticks(range(1, len(expirations) + 1))
    ax_main.set_xticklabels(date_labels, rotation=45, ha='right', color='gray', fontsize=10)
    
    ax_main.spines['top'].set_visible(False)
    ax_main.spines['right'].set_visible(False)
    ax_main.spines['left'].set_color('white')
    ax_main.spines['bottom'].set_color('white')
    ax_main.grid(True, axis='y', alpha=0.1, color='white', linestyle=':')
    
    CALL_TEXT = '#ff3b3b'
    CALL_BORDER = '#8a1f1f'
    CALL_FILL = '#3a0a0a'
    
    PUT_TEXT = '#00ff66'
    PUT_BORDER = '#146b3a'
    PUT_FILL = '#062015'
    
    VERTICAL_LINE = '#00bfff'
    PIVOT_LOCAL = '#808080'
    PIVOT_GLOBAL = '#ffffff'
    SPOT_LINE = '#ffaa00'
    MAX_PAIN_LINE = '#ff00ff'
    GAMMA_LINE = '#00ffff'
    
    dx_near = 0.06
    dx_step = 0.04
    min_box_height = max(8, 0.025 * y_range)
    
    for i, exp_date in enumerate(expirations, start=1):
        df_exp = dfs_dict[exp_date]
        
        ax_main.axvline(x=i, color=VERTICAL_LINE, linestyle='--', linewidth=0.8, alpha=0.4)
        
        df_call = df_exp[df_exp['option_type'] == 'CALL']
        df_put = df_exp[df_exp['option_type'] == 'PUT']
        
        call_clusters = detect_clusters(
            df_call['strike'].values, 
            df_call['open_interest'].values, 
            max_clusters=2
        )
        
        put_clusters = detect_clusters(
            df_put['strike'].values, 
            df_put['open_interest'].values, 
            max_clusters=2
        )
        
        pivot_local = calculate_pivot(df_exp, df_exp['strike'].unique())
        
        if pivot_local:
            ax_main.plot([i-0.3, i+0.3], [pivot_local, pivot_local], 
                        color=PIVOT_LOCAL, linestyle='--', linewidth=1.0, alpha=0.6)
        
        W = 1.0
        
        call_labels = []
        for j, (low, high, total_oi) in enumerate(call_clusters):
            box_height = max(high - low, min_box_height)
            box_center = (low + high) / 2
            box_low = box_center - box_height / 2
            box_high = box_center + box_height / 2
            
            rect = mpatches.Rectangle(
                (i - 0.35, box_low), 0.35, box_height,
                linewidth=1.4, edgecolor=CALL_BORDER, facecolor=CALL_FILL, alpha=0.25
            )
            ax_main.add_patch(rect)
            
            if low == high:
                strike_label = f"{int(low)}"
            else:
                strike_label = f"{int(low)}-{int(high)}"
            
            volume_label = f"{int(total_oi):,}"
            y_label = box_center
            call_labels.append((j, y_label, strike_label, volume_label))
        
        call_labels.sort(key=lambda x: x[1])
        for idx, (j, y_label, strike_label, volume_label) in enumerate(call_labels):
            k = 0
            if idx > 0:
                prev_y = call_labels[idx-1][1]
                if abs(y_label - prev_y) < 0.03 * y_range:
                    k = 1
            
            x_call = i - dx_near * W - k * dx_step * W
            
            if k > 0:
                ax_main.plot([i, x_call], [y_label, y_label], 
                           color=CALL_BORDER, linewidth=0.8, alpha=0.5)
            
            # Strike en gris
            ax_main.text(x_call, y_label + 5, strike_label,
                        ha='right', va='center', color='gray', fontsize=8, fontweight='bold')
            # Volumen en rojo
            ax_main.text(x_call, y_label - 5, volume_label,
                        ha='right', va='center', color=CALL_TEXT, fontsize=8, fontweight='bold')
        
        put_labels = []
        for j, (low, high, total_oi) in enumerate(put_clusters):
            box_height = max(high - low, min_box_height)
            box_center = (low + high) / 2
            box_low = box_center - box_height / 2
            box_high = box_center + box_height / 2
            
            rect = mpatches.Rectangle(
                (i, box_low), 0.35, box_height,
                linewidth=1.4, edgecolor=PUT_BORDER, facecolor=PUT_FILL, alpha=0.25
            )
            ax_main.add_patch(rect)
            
            if low == high:
                strike_label = f"{int(low)}"
            else:
                strike_label = f"{int(low)}-{int(high)}"
            
            volume_label = f"{int(total_oi):,}"
            y_label = box_center
            put_labels.append((j, y_label, strike_label, volume_label))
        
        put_labels.sort(key=lambda x: x[1])
        for idx, (j, y_label, strike_label, volume_label) in enumerate(put_labels):
            k = 0
            if idx > 0:
                prev_y = put_labels[idx-1][1]
                if abs(y_label - prev_y) < 0.03 * y_range:
                    k = 1
            
            x_put = i + dx_near * W + k * dx_step * W
            
            if k > 0:
                ax_main.plot([i, x_put], [y_label, y_label], 
                           color=PUT_BORDER, linewidth=0.8, alpha=0.5)
            
            # Strike en gris
            ax_main.text(x_put, y_label + 5, strike_label,
                        ha='left', va='center', color='gray', fontsize=8, fontweight='bold')
            # Volumen en verde
            ax_main.text(x_put, y_label - 5, volume_label,
                        ha='left', va='center', color=PUT_TEXT, fontsize=8, fontweight='bold')
    
    if global_pivot:
        ax_main.axhline(y=global_pivot, color=PIVOT_GLOBAL, linestyle='--', 
                       linewidth=1, alpha=0.8)
        ax_main.text(len(dfs_dict) + 0.3, global_pivot, f"PIVOT {int(global_pivot)}",
                    ha='left', va='center', color=PIVOT_GLOBAL, fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='black', edgecolor=PIVOT_GLOBAL, linewidth=1))
    
    if spot:
        ax_main.axhline(y=spot, color=SPOT_LINE, linestyle='-', linewidth=1, alpha=0.9)
        ax_main.text(0.2, spot, f"PRICE {spot:.2f}",
                    ha='left', va='center', color=SPOT_LINE, fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='black', edgecolor=SPOT_LINE, linewidth=1))
    
    if max_pain:
        ax_main.axhline(y=max_pain, color=MAX_PAIN_LINE, linestyle=':', linewidth=1, alpha=0.9)
        ax_main.text(len(dfs_dict) + 0.3, max_pain, f"MAX PAIN {max_pain:.2f}",
                    ha='left', va='center', color=MAX_PAIN_LINE, fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='black', edgecolor=MAX_PAIN_LINE, linewidth=1))
    
    if gamma_exposure:
        ax_main.axhline(y=gamma_exposure, color=GAMMA_LINE, linestyle='-.', linewidth=1, alpha=0.9)
        ax_main.text(len(dfs_dict) + 0.3, gamma_exposure, f"MAX GAMMA {gamma_exposure:.2f}",
                    ha='left', va='center', color=GAMMA_LINE, fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='black', edgecolor=GAMMA_LINE, linewidth=1))
    
    panel_y = 0.95
    ax_panel.text(0.1, panel_y, f"TICKER: {ticker}", 
                 color='white', fontsize=14, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.08
    if spot:
        ax_panel.text(0.1, panel_y, f"SPOT: ${spot:.2f}", 
                     color=SPOT_LINE, fontsize=12, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.08
    if global_pivot:
        ax_panel.text(0.1, panel_y, f"PIVOT: ${global_pivot:.2f}", 
                     color=PIVOT_GLOBAL, fontsize=12, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.08
    if max_pain:
        ax_panel.text(0.1, panel_y, f"MAX PAIN: ${max_pain:.2f}", 
                     color=MAX_PAIN_LINE, fontsize=12, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.08
    if gamma_exposure:
        ax_panel.text(0.1, panel_y, f"MAX GAMMA: ${gamma_exposure:.2f}", 
                     color=GAMMA_LINE, fontsize=12, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.12
    ax_panel.text(0.1, panel_y, "LEYENDA:", 
                 color='white', fontsize=11, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.08
    ax_panel.text(0.1, panel_y, "█ CALLS", 
                 color=CALL_TEXT, fontsize=10, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.06
    ax_panel.text(0.1, panel_y, "█ PUTS", 
                 color=PUT_TEXT, fontsize=10, fontweight='bold', transform=ax_panel.transAxes)
    
    panel_y -= 0.08
    ax_panel.text(0.1, panel_y, "--- Pivot Local", 
                 color=PIVOT_LOCAL, fontsize=9, transform=ax_panel.transAxes)
    
    panel_y -= 0.06
    ax_panel.text(0.1, panel_y, "--- Pivot Global", 
                 color=PIVOT_GLOBAL, fontsize=9, transform=ax_panel.transAxes)
    
    panel_y -= 0.06
    ax_panel.text(0.1, panel_y, "─ Spot Price", 
                 color=SPOT_LINE, fontsize=9, transform=ax_panel.transAxes)
    
    if max_pain:
        panel_y -= 0.06
        ax_panel.text(0.1, panel_y, ": Max Pain", 
                     color=MAX_PAIN_LINE, fontsize=9, transform=ax_panel.transAxes)
    
    if gamma_exposure:
        panel_y -= 0.06
        ax_panel.text(0.1, panel_y, "─· Max Gamma", 
                     color=GAMMA_LINE, fontsize=9, transform=ax_panel.transAxes)
    
    fig.text(0.5, 0.96, f"{ticker} - Institutional Options OI Zones", 
            ha='center', color='white', fontsize=18, fontweight='bold')
    
    return fig


# ============================================================================
# INTERFAZ STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="OI Zones Chart Builder",
    page_icon="📊",
    layout="wide"
)

def main():
    # Título minimalista
    st.markdown("<h1 style='text-align: center;'>OI ZONES</h1>", unsafe_allow_html=True)
    
    # Upload area compacta
    uploaded_files = st.file_uploader(
        "Upload CSV files",
        type=['csv'],
        accept_multiple_files=True,
        key="main_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        ticker = None
        for file in uploaded_files:
            try:
                ticker = file.name.split('_')[0].upper()
                break
            except:
                pass
        
        if ticker:
            try:
                dfs_dict = {}
                df_max_pain = None
                df_gamma = None
                
                with st.spinner("Procesando archivos CSV..."):
                    for file in uploaded_files:
                        try:
                            df = pd.read_csv(file)
                            df.columns = df.columns.str.strip()
                            cols_lower = [str(col).lower() for col in df.columns]
                            
                            # Detectar gamma_exposure - debe tener "gamma" en el nombre de columnas
                            has_gamma = any('gamma' in col for col in cols_lower)
                            has_call = any('call' in col for col in cols_lower)
                            has_put = any('put' in col for col in cols_lower)
                            
                            if has_gamma and has_call and has_put:
                                df_gamma = df
                                # También procesar gamma como skew_analysis para mostrar en gráfico
                                # Convertir gamma a formato skew
                                cols_lower_dict = {col.lower(): col for col in df.columns}
                                
                                # Encontrar columnas de OI (obtener el nombre original, no la clave lowercase)
                                call_oi_col = next((cols_lower_dict[col] for col in cols_lower_dict if 'call' in col and 'oi' in col), None)
                                put_oi_col = next((cols_lower_dict[col] for col in cols_lower_dict if 'put' in col and 'oi' in col), None)
                                strike_col = next((cols_lower_dict[col] for col in cols_lower_dict if 'strike' in col), None)
                                
                                if strike_col and call_oi_col and put_oi_col:
                                    # Crear registros skew a partir de gamma
                                    df_skew = pd.DataFrame()
                                    df_skew['strike'] = df[strike_col]
                                    df_skew['option_type'] = 'CALL'
                                    df_skew['open_interest'] = df[call_oi_col]
                                    
                                    df_skew_put = pd.DataFrame()
                                    df_skew_put['strike'] = df[strike_col]
                                    df_skew_put['option_type'] = 'PUT'
                                    df_skew_put['open_interest'] = df[put_oi_col]
                                    
                                    df_combined = pd.concat([df_skew, df_skew_put], ignore_index=True)
                                    df_combined = clean_strikes(df_combined)
                                    
                                    try:
                                        date_str = file.name.split('_')[-1].replace('.csv', '')
                                        exp_date = datetime.strptime(date_str, '%Y-%m-%d')
                                    except:
                                        exp_date = datetime.now()
                                    
                                    dfs_dict[exp_date] = df_combined
                                continue
                            
                            # Detectar max_pain
                            has_total_loss = any('total_loss' in col or 'total loss' in col for col in cols_lower)
                            
                            if has_total_loss:
                                df_max_pain = df
                                continue
                            
                            # Procesar como archivo de OI Zones
                            required_cols = ['strike', 'option_type', 'open_interest']
                            # Buscar columnas case-insensitive
                            cols_lower_dict = {col.lower(): col for col in df.columns}
                            missing_cols = [col for col in required_cols if col not in cols_lower_dict]
                            
                            if missing_cols:
                                st.error(f"❌ {file.name} - Faltan columnas: {missing_cols}")
                                continue
                            
                            # Renombrar columnas a lowercase para procesamiento
                            rename_dict = {cols_lower_dict[col]: col for col in required_cols if col in cols_lower_dict}
                            df = df.rename(columns=rename_dict)
                            
                            df['option_type'] = df['option_type'].str.upper()
                            df = clean_strikes(df)
                            
                            try:
                                date_str = file.name.split('_')[-1].replace('.csv', '')
                                exp_date = datetime.strptime(date_str, '%Y-%m-%d')
                            except:
                                exp_date = datetime.now()
                            
                            dfs_dict[exp_date] = df
                        except Exception as e:
                            st.error(f"❌ Error procesando {file.name}: {str(e)}")
                
                if not dfs_dict:
                    st.error("❌ No se encontraron archivos skew_analysis válidos")
                else:
                    df_all = pd.concat(dfs_dict.values(), ignore_index=True)
                    
                    spot_auto = calculate_global_pivot(df_all)
                    price_live = get_current_price(ticker)
                    spot = price_live if price_live else spot_auto
                    
                    max_pain = find_max_pain(df_max_pain)
                    gamma_exposure = find_gamma_exposure(df_gamma)
                    
                    # Métricas principales - solo las más importantes
                    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
                    with col1:
                        st.metric("Ticker", ticker)
                    with col2:
                        st.metric("SPOT", f"${spot:.2f}" if spot else "N/A")
                    with col3:
                        st.metric("PIVOT", f"${calculate_global_pivot(df_all):.2f}")
                    with col4:
                        st.metric("Vencimientos", len(dfs_dict))
                    with col5:
                        total_oi = df_all['open_interest'].sum()
                        st.metric("Total OI", f"{int(total_oi):,}")
                    with col6:
                        call_oi = df_all[df_all['option_type'] == 'CALL']['open_interest'].sum()
                        st.metric("OI CALLS", f"{int(call_oi):,}")
                    with col7:
                        put_oi = df_all[df_all['option_type'] == 'PUT']['open_interest'].sum()
                        st.metric("OI PUTS", f"{int(put_oi):,}")
                    with col8:
                        total_strikes = len(df_all['strike'].unique())
                        call_put_ratio = call_oi / put_oi if put_oi > 0 else 0
                        st.metric("C/P Ratio", f"{call_put_ratio:.2f}")
                    
                    with st.spinner("Generating chart..."):
                        fig = generate_chart(dfs_dict, ticker, spot, max_pain, gamma_exposure)
                        
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=150, facecolor='black')
                        buf.seek(0)
                        
                        st.pyplot(fig, use_container_width=True)
                        
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label="⬇️ Download PNG",
                                data=buf,
                                file_name=f"{ticker}_OI_Zones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        
                        plt.close(fig)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ No se pudo extraer el ticker del nombre del archivo")


if __name__ == "__main__":
    main()
