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
        # Intenta cargar el logo si existe
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

def generar_pdf(df_detalle, df_ranking, df_consumos, df_precios_ganadora, nombre_cliente, direccion_cliente, compania_actual_manual):
    try:
        pdf = EnergetikaPDF()
        
        # --- PROCESAMIENTO PREVIO DE DATOS ---
        # Identificar la fila de la factura actual y la ganadora
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("FACTURA", na=False)]
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        
        ganadora_row = ranking_ordenado.iloc[0]
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_periodo = ganadora_row.iloc[1]
        
        # Buscar el coste actual en el detalle (usando el marcador del Excel)
        coste_actual_total = df_detalle[df_detalle['Compañía/Tarifa'].str.contains("FACTURA", na=False)]['Coste (€)'].sum()
        
        porcentaje_ahorro_ganadora = (ahorro_total_periodo / coste_actual_total) * 100 if coste_actual_total > 0 else 0
        lista_fechas = df_consumos['Fecha'].unique()
        
        # --- LOGICA DE CALCULO ANUALIZADO ---
        total_dias_analizados = df_consumos['Días'].sum()
        ahorro_anual_sin_iva = (ahorro_total_periodo / total_dias_analizados) * 365 if total_dias_analizados > 0 else 0
        ahorro_anual_con_iva = ahorro_anual_sin_iva * 1.21

        primer_nombre = nombre_cliente.split()[0] if nombre_cliente else "cliente"

        # PÁGINA 1: PORTADA
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 22); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, f"Hola, {primer_nombre}!".encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        
        pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 10, "Hemos analizado tus facturas recientes y tenemos excelentes noticias.\nPuedes reducir tu gasto energetico significativamente.".encode('latin-1', 'replace').decode('latin-1'), align='C')
        
        pdf.ln(20); pdf.set_fill_color(240, 248, 255); pdf.rect(20, 100, 170, 60, 'F')
        pdf.set_y(110); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "TU AHORRO ANUAL ESTIMADO ES DE:", ln=True, align='C')
        pdf.set_font('Arial', 'B', 40); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 25, f"{round(ahorro_anual_con_iva, 2)} EUR", ln=True, align='C')
        
        pdf.set_font('Arial', 'I', 11); pdf.set_text_color(100)
        pdf.cell(0, 10, f"(Lo que supone un ahorro del {round(porcentaje_ahorro_ganadora, 1)}% en tu factura)", ln=True, align='C')

        # PÁGINA 2: DETALLE TÉCNICO
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(45, 8, "Cliente:", 0); pdf.set_font('Arial', '', 11); pdf.cell(0, 8, nombre_cliente.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.cell(45, 8, "Direccion:".encode('latin-1', 'replace').decode('latin-1'), 0); pdf.cell(0, 8, direccion_cliente.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font('Arial', 'B', 11); pdf.cell(45, 8, "Suministro Actual:", 0); pdf.set_font('Arial', '', 11); pdf.set_text_color(200, 0, 0); pdf.cell(0, 8, compania_actual_manual, ln=True)
        
        pdf.ln(5); pdf.set_font('Arial', 'I', 9); pdf.set_text_color(100)
        pdf.cell(0, 5, "* Los importes se muestran sin IVA ni impuestos especiales.", ln=True); pdf.ln(2)

        # TABLA DE CONSUMOS
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS", ln=True)
        pdf.set_x(30); pdf.set_fill_color(210, 225, 240); pdf.set_font('Arial', 'B', 8)
        pdf.cell(45, 7, " Fecha", 1, 0, 'C', True); pdf.cell(50, 7, " Consumo Total (kWh)", 1, 0, 'C', True); pdf.cell(55, 7, " Potencia", 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 8); pdf.set_text_color(0)
        for _, row in df_consumos.iterrows():
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.set_x(30); pdf.cell(45, 7, f" {row['Fecha']}", 1); pdf.cell(50, 7, f" {round(total_kwh, 2)} kWh", 1, 0, 'C'); pdf.cell(55, 7, f" {row['Potencia (kW)']} kW", 1, 1, 'C')

        # GRÁFICA DE COMPARATIVA
        pdf.ln(10)
        meses_grafica, ahorros_grafica = [], []
        for fecha in lista_fechas:
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("FACTURA", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                meses_grafica.append(str(fecha)); ahorros_grafica.append(c_act - c_pro)
            except: continue

        if meses_grafica:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(meses_grafica, ahorros_grafica, color='#2ecc71', edgecolor='black')
            ax.set_title("Ahorro Mensual Detectado")
            plt.tight_layout()
            fig.savefig("temp_plot.png", dpi=300); plt.close(fig)
            pdf.image("temp_plot.png", x=45, w=120)

        # PÁGINA 3: RANKING Y CIERRE
        pdf.add_page()
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "2. RANKING DE MEJORES OPCIONES", ln=True)
        pdf.set_x(35); pdf.set_fill_color(20, 50, 100); pdf.set_text_color(255)
        pdf.cell(80, 7, " Compania / Tarifa", 1, 0, 'L', True); pdf.cell(60, 7, " Ahorro en Periodo", 1, 1, 'C', True)
        
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for _, row in ranking_ordenado.head(5).iterrows():
            pdf.set_x(35); pdf.cell(80, 7, f" {row.iloc[0]}", 1); pdf.set_text_color(34, 139, 34)
            pdf.cell(60, 7, f" +{round(row.iloc[1], 2)} EUR", 1, 1, 'C'); pdf.set_text_color(0)

        # QR Y CONTACTO
        pdf.ln(10)
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data("https://wa.me/4915154663318?text=Hola, quiero contratar la tarifa ganadora")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=(20, 50, 100), back_color="white")
        qr_img.save("temp_qr.png")
        
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, "ESCANEA PARA CONTRATACION DIRECTA VIA WHATSAPP", ln=True, align='C')
        pdf.image("temp_qr.png", x=85, w=40)

        return pdf.output(dest='S').encode('latin-1', 'replace')
    except Exception as e:
        st.error(f"Error técnico en el PDF: {e}"); return None

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador de Informes | Energetika")

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre Cliente:", "Diego Bueno Lozano")
    direccion = st.text_input("Dirección:", "Calle Santa Teresa 46, Prado del Rey")
with col2:
    cia_actual = st.text_input("Compañía Actual:", "Octopus Energy")

archivo_excel = st.file_uploader("Carga el Excel generado", type=["xlsx"])

if archivo_excel:
    try:
        # Carga de datos
        df_det = pd.read_excel(archivo_excel, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo_excel, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo_excel, sheet_name="Datos Facturas Originales")
        df_pre = pd.read_excel(archivo_excel, sheet_name="Precios Tarifa Ganadora")

        st.success("✅ Datos cargados con éxito.")

        if st.button("🚀 Generar Informe PDF"):
            pdf_out = generar_pdf(df_det, df_ran, df_con, df_pre, nombre, direccion, cia_actual)
            if pdf_out:
                st.download_button(
                    label="📥 Descargar Auditoria PDF",
                    data=pdf_out,
                    file_name=f"Auditoria_{nombre.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
