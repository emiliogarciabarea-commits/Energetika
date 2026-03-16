
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

        # 1. IDENTIFICAR GANADORA
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        ganadora_row = ranking_ordenado.iloc[0]
        
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total = ganadora_row.iloc[1]

        # 2. CÁLCULOS
        num_facturas = df_detalle['Mes/Fecha'].nunique()
        ahorro_anual = (ahorro_total / num_facturas) * 12 if num_facturas > 0 else 0

        # 3. CABECERA DE RESULTADOS
        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 15, f" RECOMENDACIÓN: {str(nombre_ganadora).upper()}", ln=True, fill=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 10, f"AHORRO TOTAL EN EL PERIODO: {round(float(ahorro_total), 2)} EUR", ln=True)
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(0, 12, f"AHORRO ANUAL ESTIMADO: {round(float(ahorro_anual), 2)} EUR / AÑO", ln=True)
        pdf.ln(10)

        # 4. TABLA: RESUMEN DE CONSUMOS (NUEVA)
        pdf.set_text_color(0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        
        pdf.set_fill_color(100, 100, 100)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(60, 8, " Mes de Factura", 1, 0, 'C', True)
        pdf.cell(60, 8, " Consumo Total (kWh)", 1, 0, 'C', True)
        pdf.cell(70, 8, " Potencia Contratada", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)
        for _, row in df_consumos.iterrows():
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.cell(60, 8, f" {row['Fecha']}", 1)
            pdf.cell(60, 8, f" {round(total_kwh, 2)} kWh", 1, 0, 'C')
            pdf.cell(70, 8, f" {row['Potencia (kW)']} kW", 1, 1, 'C')
        
        pdf.ln(10)

        # 5. TABLA: COMPARATIVA DE AHORRO (MES A MES)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "2. DETALLE DE AHORRO CON LA OPCIÓN RECOMENDADA", ln=True)
        pdf.set_fill_color(50, 50, 50)
        pdf.set_text_color(255)
        pdf.cell(50, 8, " Periodo", 1, 0, 'C', True)
        pdf.cell(45, 8, " Coste Actual", 1, 0, 'C', True)
        pdf.cell(45, 8, " Coste Propuesta", 1, 0, 'C', True)
        pdf.cell(50, 8, " Ahorro", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)
        for fecha in df_detalle['Mes/Fecha'].unique():
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                pdf.cell(50, 8, f" {fecha}", 1)
                pdf.cell(45, 8, f" {round(c_act, 2)} EUR", 1, 0, 'R')
                pdf.cell(45, 8, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                pdf.cell(50, 8, f" {round(c_act - c_pro, 2)} EUR", 1, 1, 'R')
            except: continue

        pdf.ln(10)

        # 6. TABLA: TOP 5 COMPAÑÍAS CON MÁS AHORRO (NUEVA)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "3. TOP 5 MEJORES ALTERNATIVAS DE MERCADO", ln=True)
        pdf.set_fill_color(20, 50, 100)
        pdf.set_text_color(255)
        pdf.cell(120, 8, " Compañía / Tarifa", 1, 0, 'L', True)
        pdf.cell(70, 8, " Ahorro Total Detectado", 1, 1, 'C', True)

        pdf.set_text_color(0)
        top_5 = ranking_ordenado.head(5)
        for _, row in top_5.iterrows():
            pdf.cell(120, 8, f" {row.iloc[0]}", 1)
            pdf.set_text_color(34, 139, 34)
            pdf.cell(70, 8, f" +{round(row.iloc[1], 2)} EUR", 1, 1, 'C')
            pdf.set_text_color(0)

        return pdf.output()
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")
        return None

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador Pro | Energetika")

archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if archivo:
    try:
        # Cargamos las 3 pestañas necesarias
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        
        st.success("✅ Excel cargado con éxito.")
        
        if st.button("🚀 Generar Informe Completo"):
            pdf_out = generar_pdf(df_det, df_ran, df_con)
            if pdf_out:
                st.download_button(
                    label="📥 Descargar Auditoría Energetika",
                    data=bytes(pdf_out),
                    file_name=f"Auditoria_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error: Asegúrate de que el Excel tiene las pestañas: 'Detalle Comparativa', 'Ranking Ahorro' y 'Datos Facturas Originales'.")
