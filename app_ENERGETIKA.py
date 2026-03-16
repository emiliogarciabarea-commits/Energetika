import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Energetika | Auditoría Pro", layout="centered")

class EnergetikaPDF(FPDF):
    def header(self):
        # Logo en la parte superior derecha
        if os.path.exists("Logo_Energetika.jpg"):
            self.image("Logo_Energetika.jpg", 155, 10, 45)
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(20, 50, 100)
        self.cell(0, 10, 'ESTUDIO DE AHORRO ENERGÉTICO', ln=True)
        self.set_font('Arial', '', 10)
        self.set_text_color(100)
        self.cell(0, 5, f'Energetika - Consultoría Profesional | {datetime.now().strftime("%d/%m/%Y")}', ln=True)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Este informe es una simulación basada en datos reales de facturación proporcionados por el cliente.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking):
    pdf = EnergetikaPDF()
    pdf.add_page()

    # 1. IDENTIFICAR LA MEJOR COMPAÑÍA (GANADORA)
    # Excluimos "TU FACTURA ACTUAL" para encontrar la oferta real con más ahorro
    ranking_ofertas = df_ranking[df_ranking.iloc[:, 0] != "📍 TU FACTURA ACTUAL"]
    ganadora = ranking_ofertas.sort_values(by=ranking_ofertas.columns[1], ascending=False).iloc[0]
    
    nombre_ganadora = ganadora.iloc[0]
    ahorro_total_periodo = ganadora.iloc[1]

    # 2. CALCULAR AHORRO ANUAL ESTIMADO
    # Contamos cuántas facturas únicas se han analizado
    num_facturas = df_detalle['Mes/Fecha'].nunique()
    # Si el ahorro de X facturas es Y, en 12 meses es (Y / X) * 12
    ahorro_anual = (ahorro_total_periodo / num_facturas) * 12 if num_facturas > 0 else 0

    # 3. BLOQUE DE BIENVENIDA Y DESTACADO
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, "RESULTADOS DE LA AUDITORÍA:", ln=True)
    
    pdf.set_fill_color(240, 255, 240) # Fondo verde claro
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(30, 100, 30)
    pdf.cell(0, 15, f" COMPAÑÍA RECOMENDADA: {nombre_ganadora.upper()}", ln=True, fill=True, align='C')
    pdf.ln(5)

    # 4. CIFRAS CLAVE
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(95, 10, f"Ahorro acumulado (periodo analizado):", 0)
    pdf.set_text_color(40, 150, 40)
    pdf.cell(0, 10, f"{round(ahorro_total_periodo, 2)} EUR", ln=True)
    
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(95, 12, f"AHORRO ANUAL ESTIMADO:", 0)
    pdf.set_text_color(40, 150, 40)
    pdf.cell(0, 12, f"{round(ahorro_anual, 2)} EUR / AÑO", ln=True)
    pdf.ln(10)

    # 5. RESUMEN DE FACTURAS ANALIZADAS
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(0)
    pdf.cell(0, 10, "RESUMEN DE FACTURAS ANALIZADAS:", ln=True)
    
    # Tabla
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255)
    pdf.cell(50, 8, " Fecha Factura", 1, 0, 'C', True)
    pdf.cell(45, 8, " Coste Actual", 1, 0, 'C', True)
    pdf.cell(45, 8, " Coste Propuesto", 1, 0, 'C', True)
    pdf.cell(50, 8, " Ahorro", 1, 1, 'C', True)

    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 10)
    
    fechas = df_detalle['Mes/Fecha'].unique()
    for fecha in fechas:
        datos_mes = df_detalle[df_detalle['Mes/Fecha'] == fecha]
        # Extraer coste de la factura actual del cliente
        coste_actual = datos_mes[datos_mes['Compañía/Tarifa'] == "📍 TU FACTURA ACTUAL"]['Coste (€)'].values[0]
        # Extraer coste de la compañía ganadora para ese mismo mes
        coste_mejor = datos_mes[datos_mes['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
        ahorro_mes = coste_actual - coste_mejor

        pdf.cell(50, 8, f" {fecha}", 1)
        pdf.cell(45, 8, f" {round(coste_actual, 2)} EUR", 1, 0, 'R')
        pdf.cell(45, 8, f" {round(coste_mejor, 2)} EUR", 1, 0, 'R')
        pdf.cell(50, 8, f" {round(ahorro_mes, 2)} EUR", 1, 1, 'R')

    pdf.ln(15)

    # 6. RANKING FINAL (ESTUDIO DE MERCADO)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "COMPARATIVA GLOBAL DE MERCADO (AHORRO TOTAL):", ln=True)
    pdf.set_font('Arial', '', 10)
    
    # Mostrar el top 5 para no saturar el PDF
    for i, row in ranking_ofertas.sort_values(by=ranking_ofertas.columns[1], ascending=False).head(8).iterrows():
        color = (40, 150, 40) if row[1] > 0 else (150, 40, 40)
        pdf.set_text_color(0)
        pdf.cell(100, 8, f" {row[0]}:", 0)
        pdf.set_text_color(*color)
        pdf.cell(0, 8, f"{round(row[1], 2)} EUR", 0, 1)

    return pdf.output()

# --- INTERFAZ STREAMLIT ---
st.title("⚡ Energetika Report Generator")
st.info("Sube el archivo Excel generado por el comparador para crear el PDF de auditoría.")

uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        # Cargamos las pestañas del Excel que generamos anteriormente
        df_det = pd.read_excel(uploaded_file, sheet_name="Detalle")
        df_ran = pd.read_excel(uploaded_file, sheet_name="Ranking")
        
        st.success("Excel cargado con éxito.")
        
        if st.button("Generar PDF para el Cliente"):
            pdf_bytes = generar_pdf(df_det, df_ran)
            
            st.download_button(
                label="📥 Descargar Auditoría PDF",
                data=bytes(pdf_bytes),
                file_name=f"Auditoria_Energetika_{datetime.now().strftime('%d_%m_%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Error: Asegúrate de que el Excel tiene las pestañas 'Detalle' y 'Ranking'. Detalles: {e}")
