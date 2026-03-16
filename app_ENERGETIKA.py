import streamlit as st
import pdfplumber
import re
import pandas as pd
import io
import os
from fpdf import FPDF
from datetime import datetime

# --- CLASE PARA EL PDF PERSONALIZADO ---
class AuditoriaPDF(FPDF):
    def header(self):
        # Logo en la parte superior derecha (x=150, y=8, ancho=50)
        if os.path.exists("Logo_Energetika.jpg"):
            self.image("Logo_Energetika.jpg", 145, 8, 55)
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(30, 70, 120)
        self.cell(0, 10, 'AUDITORÍA DE AHORRO ENERGÉTICO', ln=True)
        self.set_font('Arial', '', 10)
        self.set_text_color(100)
        self.cell(0, 5, f'Fecha del informe: {datetime.now().strftime("%d/%m/%Y")}', ln=True)
        self.ln(15)
        # Línea decorativa
        self.set_draw_color(46, 204, 113)
        self.line(10, 35, 200, 35)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Energetika Asesoramiento Energético - Informe Confidencial', 0, 0, 'L')
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

# --- LÓGICA DE EXTRACCIÓN (Optimizada para Iberdrola/Naturgy/ECI) ---
def extraer_datos_factura(pdf_file):
    texto_completo = ""
    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"

    # Detección de empresa
    es_iberdrola = re.search(r'IBERDROLA\s+CLIENTES', texto_completo, re.IGNORECASE)
    es_naturgy = re.search(r'Naturgy', texto_completo, re.IGNORECASE)

    # Inicializar valores
    res = {"Titular": "No encontrado", "Fecha": "No encontrada", "Días": 0, "Potencia": 0.0, 
           "Punta": 0.0, "Llano": 0.0, "Valle": 0.0, "Total": 0.0, "CUPS": "No encontrado"}

    # Extraer Titular (Ejemplo específico de tu factura)
    m_titular = re.search(r'Titular\n(.*?)\n', texto_completo)
    if m_titular: res["Titular"] = m_titular.group(1).strip()

    # Extraer CUPS
    m_cups = re.search(r'ES\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\w{2}', texto_completo)
    if m_cups: res["CUPS"] = m_cups.group(0)

    if es_iberdrola:
        # Consumos según tu factura 
        res["Punta"] = float(re.search(r'Punta:?\s*([\d,.]+)\s*kWh', texto_completo).group(1).replace(',', '.'))
        res["Llano"] = float(re.search(r'Llano:?\s*([\d,.]+)\s*kWh', texto_completo).group(1).replace(',', '.'))
        res["Valle"] = float(re.search(r'Valle:?\s*([\d,.]+)\s*kWh', texto_completo).group(1).replace(',', '.'))
        res["Potencia"] = float(re.search(r'Potencia punta:\s*([\d,.]+)\s*kW', texto_completo).group(1).replace(',', '.'))
        res["Días"] = int(re.search(r'Potencia\s+facturada.*?(\d+)\s+días', texto_completo, re.DOTALL).group(1))
        res["Total"] = float(re.search(r'TOTAL\s+IMPORTE\s+FACTURA.*?([\d,.]+)\s*€', texto_completo, re.DOTALL).group(1).replace(',', '.'))
        res["Fecha"] = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo).group(1)

    return res

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Energetika Pro", layout="wide")

col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("Logo_Energetika.jpg"):
        st.image("Logo_Energetika.jpg", width=150)
with col2:
    st.title("Sistema de Auditoría Energética")

uploaded_file = st.file_uploader("Sube la factura del cliente (PDF)", type="pdf")

if uploaded_file:
    datos = extraer_datos_factura(uploaded_file)
    
    st.subheader("📋 Datos detectados")
    # Permitir corrección manual antes de generar el PDF
    col_a, col_b, col_c = st.columns(3)
    titular = col_a.text_input("Titular", datos["Titular"])
    total_actual = col_b.number_input("Total Factura Actual (€)", value=datos["Total"])
    cups = col_c.text_input("CUPS", datos["CUPS"])

    if st.button("🚀 Generar Informe de Ahorro para Cliente"):
        pdf = AuditoriaPDF()
        pdf.add_page()
        
        # Cuerpo del informe
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"CLIENTE: {titular}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 7, f"CUPS: {cups}", ln=True)
        pdf.ln(5)

        # Resumen de Consumo
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, " RESUMEN DE CONSUMO ANALIZADO", ln=True, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(60, 8, f"Potencia Contratada: {datos['Potencia']} kW", ln=True)
        pdf.cell(60, 8, f"Consumo Punta: {datos['Punta']} kWh")
        pdf.cell(60, 8, f"Consumo Llano: {datos['Llano']} kWh")
        pdf.cell(60, 8, f"Consumo Valle: {datos['Valle']} kWh", ln=True)
        pdf.ln(10)

        # Tabla de Comparativa (Simulada para el ejemplo)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(46, 204, 113)
        pdf.set_text_color(255)
        pdf.cell(90, 10, " Concepto", 1, 0, 'L', True)
        pdf.cell(50, 10, " Factura Actual", 1, 0, 'C', True)
        pdf.cell(50, 10, " Propuesta Energetika", 1, 1, 'C', True)
        
        pdf.set_text_color(0)
        pdf.set_font("Arial", '', 10)
        pdf.cell(90, 10, " Importe Total del Periodo", 1)
        pdf.cell(50, 10, f" {total_actual} EUR", 1, 0, 'C')
        pdf.cell(50, 10, f" {round(total_actual * 0.82, 2)} EUR", 1, 1, 'C') # Ejemplo 18% ahorro

        pdf.ln(15)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(30, 130, 70)
        ahorro_estimado = round(total_actual * 0.18, 2)
        pdf.cell(0, 10, f"AHORRO MENSUAL ESTIMADO: {ahorro_estimado} EUR", ln=True, align='C')

        # Generar descarga
        pdf_output = pdf.output()
        st.download_button(
            label="📥 Descargar Auditoría PDF",
            data=bytes(pdf_output),
            file_name=f"Auditoria_{titular.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
