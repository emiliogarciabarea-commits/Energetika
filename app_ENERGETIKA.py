import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Energetika | Generador de Informes", layout="centered")

class EnergetikaPDF(FPDF):
    def header(self):
        # Logo en la parte superior derecha
        if os.path.exists("Logo_Energetika.jpg"):
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
        self.cell(0, 10, 'Informe generado por Energetika basado en el estudio comparativo de mercado.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking):
    try:
        pdf = EnergetikaPDF()
        pdf.add_page()

        # 1. IDENTIFICAR LA MEJOR COMPAÑÍA
        # Buscamos en el ranking la opción con mayor ahorro (que no sea la actual)
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ganadora_row = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False).iloc[0]
        
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total = ganadora_row.iloc[1]

        # 2. CÁLCULO DE AHORRO ANUAL
        num_facturas = df_detalle['Mes/Fecha'].nunique()
        ahorro_anual = (ahorro_total / num_facturas) * 12 if num_facturas > 0 else 0

        # 3. DISEÑO DEL CUERPO
        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 15, f" RECOMENDACIÓN: {str(nombre_ganadora).upper()}", ln=True, fill=True, align='C')
        pdf.ln(10)

        # 4. CIFRAS
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0)
        pdf.cell(90, 10, "Ahorro total analizado:")
        pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 10, f"{round(float(ahorro_total), 2)} EUR", ln=True)
        
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(0)
        pdf.cell(90, 12, "AHORRO ANUAL ESTIMADO:")
        pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 12, f"{round(float(ahorro_anual), 2)} EUR / AÑO", ln=True)
        pdf.ln(10)

        # 5. TABLA DE COMPARATIVA
        pdf.set_fill_color(50, 50, 50)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(50, 8, " Mes", 1, 0, 'C', True)
        pdf.cell(45, 8, " Factura Actual", 1, 0, 'C', True)
        pdf.cell(45, 8, " Propuesta", 1, 0, 'C', True)
        pdf.cell(50, 8, " Ahorro", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)
        
        for fecha in df_detalle['Mes/Fecha'].unique():
            mes = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
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
        st.error(f"Error interno en la generación: {e}")
        return None

# --- INTERFAZ ---
st.title("📄 Generador de Informes Energetika")

archivo = st.file_uploader("Cargar Excel de resultados", type=["xlsx"])

if archivo:
    try:
        # Cargamos las pestañas exactamente como se llaman en tu Excel
        df_det = pd.read_excel(archivo, sheet_name="Detalle")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking")
        
        st.success("Estudio cargado correctamente.")
        
        if st.button("🚀 Crear PDF Profesional"):
            res_pdf = generar_pdf(df_det, df_ran)
            if res_pdf:
                st.download_button(
                    label="📥 Descargar Auditoría",
                    data=bytes(res_pdf),
                    file_name="Auditoria_Energetika.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error("Error: Asegúrate de que el Excel tiene las hojas 'Detalle' y 'Ranking'.")
