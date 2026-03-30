
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
        # Logo opcional
        if os.path.exists("Logo_Energetika.jpg"):
            self.image("Logo_Energetika.jpg", 155, 10, 40)
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(20, 50, 100)
        self.cell(0, 10, 'ESTUDIO DE AHORRO ENERGÉTICO', ln=True)
        self.set_font('Arial', '', 10)
        self.set_text_color(100)
        self.cell(0, 5, f'Energetika - Consultoría Profesional | {datetime.now().strftime("%d/%m/%Y")}', ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Informe generado por Energetika - Auditoría Profesional.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking, df_consumos, df_precios_ganadora, nombre_cliente, direccion_cliente, compania_actual_manual):
    try:
        pdf = EnergetikaPDF()
        
        # --- PROCESAMIENTO PREVIO DE DATOS ---
        # Filtramos la fila de la factura actual en el ranking para encontrar la mejor
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        
        ganadora_row = ranking_ordenado.iloc[0]
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_periodo = ganadora_row.iloc[1]
        
        # Coste actual (buscando la etiqueta "ACTUAL" en el detalle)
        df_actual = df_detalle[df_detalle['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]
        coste_actual_total = df_actual['Coste (€)'].sum()
        
        porcentaje_ahorro_ganadora = (ahorro_total_periodo / coste_actual_total) * 100 if coste_actual_total > 0 else 0
        lista_fechas = df_consumos['Fecha'].unique()
        
        # --- LÓGICA DE CÁLCULO POR DÍAS REALES ---
        total_dias_analizados = df_consumos['Días'].sum()
        if total_dias_analizados > 0:
            ahorro_por_dia = ahorro_total_periodo / total_dias_analizados
            ahorro_anual_sin_iva = ahorro_por_dia * 365
        else:
            ahorro_anual_sin_iva = 0
            
        ahorro_anual_con_iva = ahorro_anual_sin_iva * 1.21
        primer_nombre = nombre_cliente.split()[0] if nombre_cliente else "cliente"

        # PÁGINA 1: PORTADA
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 22); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, f"¡Hola, {primer_nombre}!".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        
        pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 10, "Hemos analizado tus facturas recientes y tenemos excelentes noticias.\nPuedes reducir tu gasto energético significativamente.".encode('latin-1', 'replace').decode('latin-1'), align='C')
        
        pdf.ln(20); pdf.set_fill_color(240, 248, 255); pdf.rect(20, 100, 170, 60, 'F')
        pdf.set_y(110); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "TU AHORRO ANUAL ESTIMADO ES DE:", ln=True, align='C')
        pdf.set_font('Arial', 'B', 40); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 25, f"{round(ahorro_anual_con_iva, 2)} EUR", ln=True, align='C')
        
        pdf.set_font('Arial', 'I', 11); pdf.set_text_color(100)
        pdf.cell(0, 10, f"(Lo que supone un ahorro del {round(porcentaje_ahorro_ganadora, 1)}% en tu factura)", ln=True, align='C')

        # PÁGINA 2: ANÁLISIS
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(45, 8, "Cliente:", 0); pdf.set_font('Arial', '', 11); pdf.cell(0, 8, nombre_cliente.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.cell(45, 8, "Dirección:".encode('latin-1', 'replace').decode('latin-1'), 0); pdf.cell(0, 8, direccion_cliente.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font('Arial', 'B', 11); pdf.cell(45, 8, "Suministro Actual:", 0); pdf.set_font('Arial', '', 11); pdf.set_text_color(200, 0, 0); pdf.cell(0, 8, compania_actual_manual, ln=True)
        
        pdf.ln(5); pdf.set_font('Arial', 'I', 9); pdf.set_text_color(100)
        pdf.cell(0, 5, "* Los importes de las siguientes tablas se muestran sin IVA ni impuestos especiales.", ln=True); pdf.ln(2)

        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        pdf.set_x(30); pdf.set_fill_color(210, 225, 240); pdf.set_font('Arial', 'B', 8)
        pdf.cell(45, 7, " Mes de Factura", 1, 0, 'C', True); pdf.cell(50, 7, " Consumo Total (kWh)", 1, 0, 'C', True); pdf.cell(55, 7, " Potencia Contratada", 1, 1, 'C', True)
        
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for fecha in lista_fechas:
            row = df_consumos[df_consumos['Fecha'] == fecha].iloc[0]
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.set_x(30); pdf.cell(45, 7, f" {fecha}", 1); pdf.cell(50, 7, f" {round(total_kwh, 2)} kWh", 1, 0, 'C'); pdf.cell(55, 7, f" {row['Potencia (kW)']} kW", 1, 1, 'C')
        
        # Gráfica de Ahorro Mensual
        pdf.ln(8)
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "2. COMPARATIVA DE COSTES Y AHORRO MENSUAL", ln=True)
        
        meses_grafica, ahorros_grafica = [], []
        for fecha in lista_fechas:
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_mes = c_act - c_pro
                meses_grafica.append(str(fecha)); ahorros_grafica.append(ahorro_mes)
            except: continue

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(meses_grafica, ahorros_grafica, color=['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica], edgecolor='black')
        ax.axhline(0, color='black', linewidth=0.8); plt.xticks(rotation=45); plt.tight_layout()
        grafica_path = "temp_plot.png"; fig.savefig(grafica_path, dpi=300); plt.close(fig); pdf.image(grafica_path, x=45, w=120)

        # PÁGINA 3: CONCLUSIÓN
        pdf.add_page(); pdf.set_fill_color(230, 240, 255); pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, " RECOMENDACIÓN FINAL", ln=True, fill=True, align='C')
        
        pdf.ln(10); pdf.set_x(20); pdf.set_font('Arial', 'B', 12); pdf.set_text_color(20, 50, 100)
        pdf.cell(170, 9, f"TARIFA GANADORA: {str(nombre_ganadora).upper()}", border='TLR', ln=True, align='C')
        pdf.set_font('Arial', 'B', 12); pdf.set_text_color(34, 139, 34)
        pdf.cell(170, 11, f"AHORRO ANUAL ESTIMADO CON IVA: {round(ahorro_anual_con_iva, 2)} EUR / AÑO", border='BLR', ln=True, align='C')

        # QR
        qr = qrcode.QRCode(box_size=10, border=2)
        url_wa = "https://wa.me/4915154663318?text=Hola,%20me%20interesa%20contratar%20la%20tarifa%20ganadora"
        qr.add_data(url_wa); qr.make(fit=True)
        qr_img = qr.make_image(fill_color=(20, 50, 100), back_color="white")
        qr_path = "temp_qr.png"; qr_img.save(qr_path)
        
        pdf.ln(10); pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "Escanea para contratacion directa:", ln=True, align='C')
        pdf.image(qr_path, x=85, w=40)

        return pdf.output(dest='S').encode('latin-1', 'replace')
    except Exception as e:
        st.error(f"Error en la generación del PDF: {e}"); return None

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
        # Cargamos las hojas por nombre o posición
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        df_pre = pd.read_excel(archivo, sheet_name="Precios Tarifa Ganadora")

        st.success("✅ Excel cargado correctamente.")
        
        if st.button("🚀 Generar PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran, df_con, df_pre, nombre_cliente, direccion_cliente, compania_actual_manual)
            if pdf_bytes:
                st.download_button(
                    label="📥 Descargar Informe",
                    data=pdf_bytes,
                    file_name=f"Auditoria_{nombre_cliente.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
