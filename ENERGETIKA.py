import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Energetika Pro", layout="centered")

class EnergetikaPDF(FPDF):
    def header(self):
        if os.path.exists("Logo_Energetika.jpg"):
            # Ajusta la posición del logo (x=155, y=10)
            self.image("Logo_Energetika.jpg", 155, 10, 40)
        
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
        self.cell(0, 10, 'Documento generado por Energetika basado en análisis de datos reales.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking):
    try:
        pdf = EnergetikaPDF()
        pdf.add_page()

        # 1. ENCONTRAR GANADORA
        # Filtramos para no comparar con la factura actual del cliente
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ganadora_row = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False).iloc[0]
        
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total = ganadora_row.iloc[1]

        # 2. CÁLCULO ANUAL (Ahorro / Facturas analizadas * 12)
        num_facturas = df_detalle['Mes/Fecha'].nunique()
        ahorro_anual = (ahorro_total / num_facturas) * 12 if num_facturas > 0 else 0

        # 3. DISEÑO
        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 15, f" COMPAÑÍA RECOMENDADA: {str(nombre_ganadora).upper()}", ln=True, fill=True, align='C')
        pdf.ln(10)

        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 10, f"AHORRO TOTAL ANALIZADO: {round(float(ahorro_total), 2)} EUR", ln=True)
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(0, 12, f"AHORRO ANUAL ESTIMADO: {round(float(ahorro_anual), 2)} EUR / AÑO", ln=True)
        pdf.ln(10)

        # 4. TABLA
        pdf.set_fill_color(50, 50, 50)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(50, 8, " Periodo", 1, 0, 'C', True)
        pdf.cell(45, 8, " Factura Actual", 1, 0, 'C', True)
        pdf.cell(45, 8, " Propuesta", 1, 0, 'C', True)
        pdf.cell(50, 8, " Ahorro", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)
        
        for fecha in df_detalle['Mes/Fecha'].unique():
            mes = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                # Buscamos la fila "ACTUAL" y la fila de la "GANADORA" para ese mes
                coste_act = mes[mes['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                coste_pro = mes[mes['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_m = coste_act - coste_pro

                pdf.cell(50, 8, f" {fecha}", 1)
                pdf.cell(45, 8, f" {round(float(coste_act), 2)} EUR", 1, 0, 'R')
                pdf.cell(45, 8, f" {round(float(coste_pro), 2)} EUR", 1, 0, 'R')
                pdf.cell(50, 8, f" {round(float(ahorro_m), 2)} EUR", 1, 1, 'R')
            except:
                continue

        return pdf.output()
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")
        return None

# --- INTERFAZ ---
st.title("📄 Generador de Informes Energetika")

archivo = st.file_uploader("Sube el archivo Excel (estudio_ahorro_energetico.xlsx)", type=["xlsx"])

if archivo:
    try:
        # Importante: Estas hojas deben existir en tu Excel
        df_det = pd.read_excel(archivo, sheet_name="Detalle")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking")
        
        st.success("Estudio cargado correctamente.")
        
        if st.button("🚀 Crear Auditoría PDF"):
            res_pdf = generar_pdf(df_det, df_ran)
            if res_pdf:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=bytes(res_pdf),
                    file_name=f"Auditoria_Energetika_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}. Asegúrate de que las hojas se llamen 'Detalle' y 'Ranking'.")
