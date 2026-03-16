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
        self.cell(0, 10, 'Informe generado por Energetika basado en el histórico de facturación del cliente.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking):
    pdf = EnergetikaPDF()
    pdf.add_page()

    # 1. IDENTIFICAR LA MEJOR COMPAÑÍA (GANADORA)
    # Filtramos para quitar la factura actual y ordenamos por ahorro
    ranking_ofertas = df_ranking[df_ranking.iloc[:, 0] != "📍 TU FACTURA ACTUAL"]
    ganadora = ranking_ofertas.sort_values(by=ranking_ofertas.columns[1], ascending=False).iloc[0]
    
    nombre_ganadora = ganadora.iloc[0]
    ahorro_total_periodo = ganadora.iloc[1]

    # 2. CALCULAR AHORRO ANUAL ESTIMADO
    num_facturas = df_detalle['Mes/Fecha'].nunique()
    ahorro_anual = (ahorro_total_periodo / num_facturas) * 12 if num_facturas > 0 else 0

    # 3. DESTACADO: LA GANADORA
    pdf.set_fill_color(230, 245, 255) 
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, f" RECOMENDACIÓN: {nombre_ganadora.upper()}", ln=True, fill=True, align='C')
    pdf.ln(5)

    # 4. CIFRAS DE AHORRO
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(95, 10, f"Ahorro acumulado detectado:", 0)
    pdf.set_text_color(40, 150, 40)
    pdf.cell(0, 10, f"{round(ahorro_total_periodo, 2)} EUR", ln=True)
    
    pdf.set_font('Arial', 'B', 15)
    pdf.set_text_color(0)
    pdf.cell(95, 12, f"AHORRO ANUAL ESTIMADO:", 0)
    pdf.set_text_color(40, 150, 40)
    pdf.cell(0, 12, f"{round(ahorro_anual, 2)} EUR / AÑO", ln=True)
    pdf.ln(10)

    # 5. TABLA COMPARATIVA
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "DETALLE COMPARATIVO POR FACTURA:", ln=True)
    
    # Cabeceras
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(50, 8, " Mes / Periodo", 1, 0, 'C', True)
    pdf.cell(45, 8, " Coste Actual", 1, 0, 'C', True)
    pdf.cell(45, 8, " Propuesta", 1, 0, 'C', True)
    pdf.cell(50, 8, " Ahorro", 1, 1, 'C', True)

    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 9)
    
    fechas = df_detalle['Mes/Fecha'].unique()
    for fecha in fechas:
        datos_mes = df_detalle[df_detalle['Mes/Fecha'] == fecha]
        try:
            coste_actual = datos_mes[datos_mes['Compañía/Tarifa'] == "📍 TU FACTURA ACTUAL"]['Coste (€)'].values[0]
            coste_mejor = datos_mes[datos_mes['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
            ahorro_mes = coste_actual - coste_mejor

            pdf.cell(50, 8, f" {fecha}", 1)
            pdf.cell(45, 8, f" {round(coste_actual, 2)} EUR", 1, 0, 'R')
            pdf.cell(45, 8, f" {round(coste_mejor, 2)} EUR", 1, 0, 'R')
            pdf.cell(50, 8, f" {round(ahorro_mes, 2)} EUR", 1, 1, 'R')
        except:
            continue

    pdf.ln(15)

    # 6. RANKING DE MERCADO
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "OTRAS OPCIONES ANALIZADAS (AHORRO TOTAL):", ln=True)
    pdf.set_font('Arial', '', 9)
    
    top_ranking = ranking_ofertas.sort_values(by=ranking_ofertas.columns[1], ascending=False).head(10)
    for _, row in top_ranking.iterrows():
        pdf.set_text_color(0)
        pdf.cell(100, 7, f" {row[0]}", 0)
        pdf.set_text_color(40, 150, 40) if row[1] > 0 else pdf.set_text_color(150, 40, 40)
        pdf.cell(0, 7, f"{round(row[1], 2)} EUR", 0, 1)

    return pdf.output()

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador de Informes Energetika")
st.write("Sube tu archivo Excel para generar la auditoría en PDF para el cliente.")

uploaded_file = st.file_uploader("Subir estudio_ahorro_energetico.xlsx", type=["xlsx"])

if uploaded_file:
    try:
        # Importante: leer por nombre de hoja
        df_det = pd.read_excel(uploaded_file, sheet_name="Detalle")
        df_ran = pd.read_excel(uploaded_file, sheet_name="Ranking")
        
        st.success("✅ Datos del estudio cargados correctamente.")
        
        if st.button("🎨 Generar Informe PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran)
            
            st.download_button(
                label="📥 Descargar Auditoría Energetika",
                data=bytes(pdf_bytes),
                file_name=f"Auditoria_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Error: No se pudieron leer las pestañas del Excel. Asegúrate de que se llaman 'Detalle' y 'Ranking'.")
