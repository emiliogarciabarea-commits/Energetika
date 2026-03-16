
import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Energetika Pro", layout="centered")

class EnergetikaPDF(FPDF):
    def header(self):
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

def generar_pdf(df_detalle, df_ranking, df_consumos):
    try:
        pdf = EnergetikaPDF()
        pdf.add_page()

        # --- 1. PROCESAMIENTO DE DATOS ---
        # Ordenar detalle por fecha (convertimos a datetime para ordenar y luego a string)
        df_detalle['fecha_dt'] = pd.to_datetime(df_detalle['Mes/Fecha'], dayfirst=True)
        df_detalle = df_detalle.sort_values('fecha_dt', ascending=True)
        
        # Identificar Ganadora
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ranking_sorted = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        ganadora_row = ranking_sorted.iloc[0]
        
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total = ganadora_row.iloc[1]

        # Cálculo Anual
        num_facturas = df_detalle['Mes/Fecha'].nunique()
        ahorro_anual = (ahorro_total / num_facturas) * 12 if num_facturas > 0 else 0

        # --- 2. RESUMEN EJECUTIVO ---
        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, f" RECOMENDACIÓN: {str(nombre_ganadora).upper()}", ln=True, fill=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 8, f"AHORRO TOTAL EN PERIODO ANALIZADO: {round(float(ahorro_total), 2)} EUR", ln=True)
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, f"ESTIMACIÓN DE AHORRO ANUAL: {round(float(ahorro_anual), 2)} EUR / AÑO", ln=True)
        pdf.ln(5)

        # --- 3. TABLA TOP 5 COMPAÑÍAS ---
        pdf.set_text_color(0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "TOP 5 MEJORES OPCIONES DE MERCADO:", ln=True)
        
        pdf.set_fill_color(100, 100, 100)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(100, 8, " Compania", 1, 0, 'C', True)
        pdf.cell(40, 8, " Ahorro Total", 1, 1, 'C', True)
        
        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)
        for i in range(min(5, len(ranking_sorted))):
            row = ranking_sorted.iloc[i]
            pdf.cell(100, 7, f" {row.iloc[0]}", 1)
            pdf.cell(40, 7, f"{round(float(row.iloc[1]), 2)} EUR", 1, 1, 'R')
        pdf.ln(10)

        # --- 4. TABLA RESUMEN DE CONSUMOS ---
        if df_consumos is not None:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 10, "RESUMEN DE CONSUMOS ANALIZADOS:", ln=True)
            pdf.set_fill_color(50, 50, 50)
            pdf.set_text_color(255)
            pdf.cell(45, 8, " Periodo", 1, 0, 'C', True)
            pdf.cell(35, 8, " Punta (kWh)", 1, 0, 'C', True)
            pdf.cell(35, 8, " Llano (kWh)", 1, 0, 'C', True)
            pdf.cell(35, 8, " Valle (kWh)", 1, 0, 'C', True)
            pdf.cell(40, 8, " Total Factura", 1, 1, 'C', True)
            
            pdf.set_text_color(0)
            pdf.set_font('Arial', '', 8)
            # Ordenar consumos por fecha
            df_consumos['fecha_dt'] = pd.to_datetime(df_consumos['Fecha'], dayfirst=True)
            df_consumos = df_consumos.sort_values('fecha_dt')
            
            for _, row in df_consumos.iterrows():
                pdf.cell(45, 7, f" {row['Fecha']}", 1)
                pdf.cell(35, 7, f"{row['Consumo Punta (kWh)']}", 1, 0, 'R')
                pdf.cell(35, 7, f"{row['Consumo Llano (kWh)']}", 1, 0, 'R')
                pdf.cell(35, 7, f"{row['Consumo Valle (kWh)']}", 1, 0, 'R')
                pdf.cell(40, 7, f"{row['Total Real']} EUR", 1, 1, 'R')
            pdf.ln(10)

        # --- 5. DETALLE COMPARATIVO (TABLA PRINCIPAL) ---
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "DETALLE COMPARATIVO MES A MES (VS GANADORA):", ln=True)
        
        pdf.set_fill_color(30, 70, 120)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(50, 8, " Periodo", 1, 0, 'C', True)
        pdf.cell(45, 8, " Factura Actual", 1, 0, 'C', True)
        pdf.cell(45, 8, " Propuesta", 1, 0, 'C', True)
        pdf.cell(50, 8, " Ahorro", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)
        
        for fecha in df_detalle['Mes/Fecha'].unique():
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                coste_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                coste_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_m = coste_act - coste_pro

                pdf.cell(50, 8, f" {fecha}", 1)
                pdf.cell(45, 8, f" {round(float(coste_act), 2)} EUR", 1, 0, 'R')
                pdf.cell(45, 8, f" {round(float(coste_pro), 2)} EUR", 1, 0, 'R')
                pdf.cell(50, 8, f" {round(float(ahorro_m), 2)} EUR", 1, 1, 'R')
            except:
                continue

        return pdf.output()
    except Exception as e:
        st.error(f"Error en la lógica del PDF: {e}")
        return None

# --- INTERFAZ ---
st.title("📄 Generador Profesional Energetika")

archivo = st.file_uploader("Cargar estudio_ahorro_energetico.xlsx", type=["xlsx"])

if archivo:
    try:
        # Cargamos las pestañas
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        
        # Intentamos cargar la pestaña de consumos si existe
        df_con = None
        try:
            df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        except:
            st.warning("No se encontró la pestaña 'Datos Facturas Originales'. La tabla de consumos se omitirá.")

        st.success("✅ Excel procesado correctamente.")
        
        if st.button("🚀 Generar Informe Completo"):
            pdf_bytes = generar_pdf(df_det, df_ran, df_con)
            if pdf_bytes:
                st.download_button(
                    label="📥 Descargar Auditoría PDF",
                    data=bytes(pdf_bytes),
                    file_name=f"Auditoria_Energetika_{datetime.now().strftime('%d%m%Y')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
