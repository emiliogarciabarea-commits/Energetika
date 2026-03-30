import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import qrcode  # Librería para el QR

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Energetika Pro", layout="centered")

class EnergetikaPDF(FPDF):
    def header(self):
        if os.path.exists("Logo_Energetika.jpg"):
            self.image("Logo_Energetika.jpg", 155, 10, 40)
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(20, 50, 100)
        self.cell(0, 10, 'ESTUDIO DE AHORRO ENERGETICO', ln=True)
        self.set_font('Arial', '', 10)
        self.set_text_color(100)
        self.cell(0, 5, f'Energetika - Consultoria Profesional | {datetime.now().strftime("%d/%m/%Y")}', ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Informe generado por Energetika - Auditoria Profesional.', 0, 0, 'C')

def limpiar_texto(texto):
    """Limpia emojis y caracteres no compatibles con latin-1"""
    if not isinstance(texto, str): return str(texto)
    return texto.replace('📍 ', '').encode('latin-1', 'replace').decode('latin-1')

def generar_pdf(df_detalle, df_ranking, df_consumos, df_precios_ganadora, nombre_cliente, direccion_cliente, compania_actual_manual):
    try:
        pdf = EnergetikaPDF()
        
        # --- PROCESAMIENTO PREVIO DE DATOS ---
        # Filtramos el ranking quitando la fila de la factura actual
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("FACTURA|ACTUAL", na=False, case=False)]
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        
        ganadora_row = ranking_ordenado.iloc[0]
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_periodo = ganadora_row.iloc[1]
        
        # Identificar coste actual buscando la fila con "FACTURA" o "ACTUAL"
        coste_actual_total = df_detalle[df_detalle['Compañía/Tarifa'].str.contains("FACTURA|ACTUAL", na=False, case=False)]['Coste (€)'].sum()
        
        porcentaje_ahorro_ganadora = (ahorro_total_periodo / coste_actual_total) * 100 if coste_actual_total > 0 else 0
        lista_fechas = df_consumos['Fecha'].unique()
        
        # --- LÓGICA DE CÁLCULO POR DÍAS REALES ---
        total_dias_analizados = df_consumos['Días'].sum()
        ahorro_anual_sin_iva = (ahorro_total_periodo / total_dias_analizados) * 365 if total_dias_analizados > 0 else 0
        ahorro_anual_con_iva = ahorro_anual_sin_iva * 1.21

        primer_nombre = nombre_cliente.split()[0] if nombre_cliente else "cliente"

        # PÁGINA 1: PORTADA
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 22); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, limpiar_texto(f"Hola, {primer_nombre}!"), ln=True, align='C')
        
        pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 10, limpiar_texto("Hemos analizado tus facturas recientes y tenemos excelentes noticias.\nPuedes reducir tu gasto energetico significativamente."), align='C')
        
        pdf.ln(20); pdf.set_fill_color(240, 248, 255); pdf.rect(20, 100, 170, 60, 'F')
        pdf.set_y(110); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "TU AHORRO ANUAL ESTIMADO ES DE:", ln=True, align='C')
        pdf.set_font('Arial', 'B', 40); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 25, f"{round(ahorro_anual_con_iva, 2)} EUR", ln=True, align='C')
        
        pdf.set_font('Arial', 'I', 11); pdf.set_text_color(100)
        pdf.cell(0, 10, f"(Lo que supone un ahorro del {round(porcentaje_ahorro_ganadora, 1)}% en tu factura)", ln=True, align='C')
        
        pdf.ln(30); pdf.set_font('Arial', '', 11); pdf.set_text_color(80); pdf.set_x(30)
        pdf.multi_cell(150, 7, limpiar_texto("Este estudio ha sido realizado de forma independiente por Energetika, analizando y comparando entre mas de 35 tarifas del mercado actual para encontrar la que mejor se adapta a tu perfil de consumo real."), align='C')

        # PÁGINA 2: ANÁLISIS DETALLADO
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(45, 8, "Cliente:", 0); pdf.set_font('Arial', '', 11); pdf.cell(0, 8, limpiar_texto(nombre_cliente), ln=True)
        pdf.cell(45, 8, "Direccion:", 0); pdf.cell(0, 8, limpiar_texto(direccion_cliente), ln=True)
        pdf.set_font('Arial', 'B', 11); pdf.cell(45, 8, "Suministro Actual:", 0); pdf.set_font('Arial', '', 11); pdf.set_text_color(200, 0, 0); pdf.cell(0, 8, limpiar_texto(compania_actual_manual), ln=True)
        
        pdf.ln(5); pdf.set_font('Arial', 'I', 9); pdf.set_text_color(100)
        pdf.cell(0, 5, "* Los importes de las siguientes tablas se muestran sin IVA ni impuestos especiales.", ln=True); pdf.ln(2)

        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        pdf.set_x(30); pdf.set_fill_color(210, 225, 240); pdf.set_font('Arial', 'B', 8)
        pdf.cell(45, 7, " Mes de Factura", 1, 0, 'C', True); pdf.cell(50, 7, " Consumo Total (kWh)", 1, 0, 'C', True); pdf.cell(55, 7, " Potencia Contratada", 1, 1, 'C', True)
        
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for _, row in df_consumos.iterrows():
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.set_x(30); pdf.cell(45, 7, f" {row['Fecha']}", 1); pdf.cell(50, 7, f" {round(total_kwh, 2)} kWh", 1, 0, 'C'); pdf.cell(55, 7, f" {row['Potencia (kW)']} kW", 1, 1, 'C')

        # COMPARATIVA MENSUAL
        pdf.ln(8); pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "2. COMPARATIVA DE COSTES Y AHORRO MENSUAL", ln=True)
        pdf.set_x(25); pdf.set_fill_color(210, 225, 240); pdf.cell(40, 7, " Periodo", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True); pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 8); meses_grafica, ahorros_grafica = [], []
        for fecha in lista_fechas:
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("FACTURA|ACTUAL", na=False, case=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_mes = c_act - c_pro
                meses_grafica.append(str(fecha)); ahorros_grafica.append(ahorro_mes)
                pdf.set_x(25); pdf.set_text_color(0); pdf.cell(40, 7, f" {fecha}", 1); pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R'); pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                if ahorro_mes > 0: pdf.set_text_color(34, 139, 34); txt_ahorro = f" +{round(ahorro_mes, 2)} EUR"
                else: pdf.set_text_color(200, 0, 0); txt_ahorro = f" {round(ahorro_mes, 2)} EUR"
                pdf.cell(40, 7, txt_ahorro, 1, 1, 'R'); pdf.set_text_color(0)
            except: continue

        # Gráfica de barras
        if meses_grafica:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(meses_grafica, ahorros_grafica, color=['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica], edgecolor='black')
            ax.axhline(0, color='black', linewidth=0.8); plt.xticks(rotation=45); plt.tight_layout()
            fig.savefig("temp_plot.png", dpi=300); plt.close(fig); pdf.image("temp_plot.png", x=45, w=120)

        # PÁGINA 3: RANKING Y CONCLUSIÓN
        pdf.add_page()
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "3. COMPARATIVA CON OTRAS OPCIONES DE MERCADO", ln=True)
        pdf.set_x(35); pdf.set_fill_color(20, 50, 100); pdf.set_text_color(255); pdf.cell(80, 7, " Compania / Tarifa", 1, 0, 'L', True); pdf.cell(60, 7, " Ahorro Total Detectado", 1, 1, 'C', True)
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for _, row in ranking_ordenado.head(5).iterrows():
            pdf.set_x(35); pdf.cell(80, 7, f" {limpiar_texto(row.iloc[0])}", 1); pdf.set_text_color(34, 139, 34); pdf.cell(60, 7, f" +{round(row.iloc[1], 2)} EUR", 1, 1, 'C'); pdf.set_text_color(0)

        # Recuadro de recomendación final
        pdf.ln(10); pdf.set_fill_color(230, 240, 255); pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 12, " CONCLUSION Y RECOMENDACION FINAL", ln=True, fill=True, align='C')
        pdf.ln(5); pdf.set_font('Arial', 'B', 11); pdf.set_text_color(20, 50, 100)
        pdf.multi_cell(0, 8, limpiar_texto(f"La opcion mas eficiente para su suministro es {nombre_ganadora}."), align='C')
        
        ahorro_5_anos = ahorro_anual_con_iva * 5
        pdf.set_font('Arial', 'I', 11); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 10, f"Dejaras de pagar {round(ahorro_5_anos, 2)} EUR extra en los proximos 5 anos.", ln=True, align='C')

        # QR
        pdf.ln(5)
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data("https://wa.me/4915154663318?text=Hola, quiero contratar la tarifa ganadora")
        qr.make(fit=True); qr_img = qr.make_image(fill_color=(20, 50, 100), back_color="white")
        qr_img.save("temp_qr.png")
        pdf.image("temp_qr.png", x=92, w=25)
        pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "Escanea para contratacion directa", ln=True, align='C')

        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"Error tecnico: {e}"); return None

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador Pro | Energetika")
c1, c2 = st.columns(2)
with c1:
    nombre_cliente = st.text_input("Nombre completo cliente:", "Sheila Maria Gonzalez Ordoñez")
    direccion_cliente = st.text_input("Dirección:", "Calle Ejemplo 123")
with c2:
    compania_actual_manual = st.text_input("Compañía actual:", "Energía XXI")

archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if archivo:
    try:
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        df_pre = pd.read_excel(archivo, sheet_name="Precios Tarifa Ganadora")

        st.success("✅ Datos del Excel cargados correctamente.")
        if st.button("🚀 Generar PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran, df_con, df_pre, nombre_cliente, direccion_cliente, compania_actual_manual)
            if pdf_bytes:
                st.download_button(label="📥 Descargar Informe", data=pdf_bytes, file_name=f"Auditoria_{nombre_cliente.replace(' ', '_')}.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
