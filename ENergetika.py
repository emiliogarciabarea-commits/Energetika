
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
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Informe generado por Energetika. Todos los precios incluyen impuestos calculados.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking):
    try:
        pdf = EnergetikaPDF()
        pdf.add_page()

        # 1. IDENTIFICAR GANADORA
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ganadora_row = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False).iloc[0]
        
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_base = ganadora_row.iloc[1]

        # 2. CÁLCULOS DE IVA (21%)
        ahorro_total_iva = ahorro_total_base * 1.21
        
        # 3. CÁLCULO ANUAL (Considerando 12 meses)
        num_facturas = df_detalle['Mes/Fecha'].nunique()
        ahorro_anual_base = (ahorro_total_base / num_facturas) * 12 if num_facturas > 0 else 0
        ahorro_anual_iva = ahorro_anual_base * 1.21

        # 4. CUADRO DE RECOMENDACIÓN CON ICONO
        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        # Añadimos el símbolo de ganador
        pdf.cell(0, 15, f" GANADOR: {str(nombre_ganadora).upper()}  [WINNER]", ln=True, fill=True, align='C')
        pdf.ln(10)

        # 5. BLOQUE DE AHORROS DESTACADOS
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(0)
        pdf.cell(90, 8, "Concepto de Ahorro", 1, 0, 'C', True)
        pdf.cell(50, 8, "Sin IVA", 1, 0, 'C', True)
        pdf.cell(50, 8, "Con IVA (21%)", 1, 1, 'C', True)

        pdf.set_text_color(34, 139, 34)
        pdf.cell(90, 10, "Ahorro Total Analizado:", 1)
        pdf.cell(50, 10, f"{round(float(ahorro_total_base), 2)} EUR", 1, 0, 'C')
        pdf.cell(50, 10, f"{round(float(ahorro_total_iva), 2)} EUR", 1, 1, 'C')

        pdf.set_font('Arial', 'B', 13)
        pdf.cell(90, 12, "AHORRO ANUAL ESTIMADO:", 1)
        pdf.cell(50, 12, f"{round(float(ahorro_anual_base), 2)} EUR", 1, 0, 'C')
        pdf.cell(50, 12, f"{round(float(ahorro_anual_iva), 2)} EUR", 1, 1, 'C')
        pdf.ln(15)

        # 6. TABLA COMPARATIVA ORDENADA POR FECHA
        pdf.set_fill_color(50, 50, 50)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(50, 8, " Periodo", 1, 0, 'C', True)
        pdf.cell(45, 8, " Factura Actual", 1, 0, 'C', True)
        pdf.cell(45, 8, " Propuesta", 1, 0, 'C', True)
        pdf.cell(50, 8, " Ahorro (con IVA)", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)

        # --- Lógica de Ordenación por Fecha ---
        # Convertimos temporalmente a datetime para ordenar de más antigua a más reciente
        df_detalle['Fecha_Temp'] = pd.to_datetime(df_detalle['Mes/Fecha'], errors='coerce')
        # Ordenamos el DataFrame por la columna de fecha real
        df_detalle_sorted = df_detalle.sort_values(by='Fecha_Temp', ascending=True)

        for fecha_texto in df_detalle_sorted['Mes/Fecha'].unique():
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha_texto]
            try:
                coste_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                coste_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                
                # Ahorro del mes con el IVA aplicado
                ahorro_m_iva = (coste_act - coste_pro) * 1.21

                pdf.cell(50, 8, f" {fecha_texto}", 1)
                pdf.cell(45, 8, f" {round(float(coste_act), 2)} EUR", 1, 0, 'R')
                pdf.cell(45, 8, f" {round(float(coste_pro), 2)} EUR", 1, 0, 'R')
                pdf.cell(50, 8, f" {round(float(ahorro_m_iva), 2)} EUR", 1, 1, 'R')
            except:
                continue

        return pdf.output()
    except Exception as e:
        st.error(f"Error en la lógica del PDF: {e}")
        return None

# --- INTERFAZ ---
st.title("📄 Generador de Informes Energetika")

archivo = st.file_uploader("Cargar estudio_ahorro_energetico.xlsx", type=["xlsx"])

if archivo:
    try:
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        
        st.success("✅ Datos cargados. La tabla se ordenará cronológicamente.")
        
        if st.button("🚀 Generar Informe PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran)
            if pdf_bytes:
                st.download_button(
                    label="📥 Descargar Auditoría (IVA 21% Incluido)",
                    data=bytes(pdf_bytes),
                    file_name=f"Auditoria_Energetika_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
