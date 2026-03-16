import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF
from datetime import datetime

# --- CLASE PARA EL PDF DE ENERGETIKA ---
class EnergetikaPDF(FPDF):
    def header(self):
        # Logo en la parte superior derecha
        if os.path.exists("Logo_Energetika.jpg"):
            self.image("Logo_Energetika.jpg", 150, 8, 50)
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(33, 47, 61)
        self.cell(0, 10, 'INFORME DE AUDITORÍA ENERGÉTICA', ln=True)
        self.set_font('Arial', '', 10)
        self.set_text_color(100)
        self.cell(0, 5, f'Generado el: {datetime.now().strftime("%d/%m/%Y")}', ln=True)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Energetika - Asesoramiento Energético Profesional', 0, 0, 'L')
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

def generar_pdf(df_detalle, df_ranking):
    pdf = EnergetikaPDF()
    pdf.add_page()

    # 1. IDENTIFICAR GANADORA Y DATOS CLAVE
    # Filtramos para no incluir la "Factura Actual" en el ranking del PDF
    ranking_real = df_ranking[df_ranking.iloc[:, 0] != "📍 TU FACTURA ACTUAL"].sort_values(by=df_ranking.columns[1], ascending=False)
    mejor_cia = ranking_real.iloc[0, 0]
    ahorro_total = ranking_real.iloc[0, 1]
    
    # Cálculo de ahorro anual estimado (basado en el promedio de las facturas subidas)
    num_facturas = df_detalle['Mes/Fecha'].nunique()
    ahorro_anual = (ahorro_total / num_facturas) * 12 if num_facturas > 0 else ahorro_total

    # 2. BLOQUE DESTACADO: LA GANADORA
    pdf.set_fill_color(235, 245, 251)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 15, f" RESULTADO: PROPUESTA DE AHORRO CON {mejor_cia.upper()}", ln=True, fill=True, align='C')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(40, 180, 99) # Verde
    pdf.cell(0, 10, f"AHORRO TOTAL ACUMULADO ANALIZADO: {round(ahorro_total, 2)} EUR", ln=True)
    pdf.set_font('Arial', 'B', 13)
    pdf.cell(0, 10, f"AHORRO ANUAL ESTIMADO: {round(ahorro_anual, 2)} EUR*", ln=True)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(100)
    pdf.cell(0, 5, "*(Cálculo proyectado basado en el histórico de facturas facilitado)", ln=True)
    pdf.ln(10)

    # 3. RESUMEN DE FACTURAS ANALIZADAS
    pdf.set_text_color(0)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "DETALLE DE FACTURAS PROCESADAS:", ln=True)
    
    # Cabecera tabla facturas
    pdf.set_fill_color(52, 73, 94)
    pdf.set_text_color(255)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(40, 8, " Periodo", 1, 0, 'C', True)
    pdf.cell(50, 8, " Coste Actual", 1, 0, 'C', True)
    pdf.cell(50, 8, f" Coste {mejor_cia[:10]}...", 1, 0, 'C', True)
    pdf.cell(40, 8, " Ahorro", 1, 1, 'C', True)

    # Filas de la tabla (solo comparando actual vs mejor opción)
    pdf.set_text_color(0)
    pdf.set_font('Arial', '', 9)
    
    for fecha in df_detalle['Mes/Fecha'].unique():
        datos_mes = df_detalle[df_detalle['Mes/Fecha'] == fecha]
        coste_actual = datos_mes[datos_mes['Compañía/Tarifa'] == "📍 TU FACTURA ACTUAL"]['Coste (€)'].values[0]
        coste_mejor = datos_mes[datos_mes['Compañía/Tarifa'] == mejor_cia]['Coste (€)'].values[0]
        ahorro_mes = coste_actual - coste_mejor
        
        pdf.cell(40, 8, f" {fecha}", 1)
        pdf.cell(50, 8, f" {round(coste_actual, 2)} EUR", 1, 0, 'R')
        pdf.cell(50, 8, f" {round(coste_mejor, 2)} EUR", 1, 0, 'R')
        pdf.cell(40, 8, f" {round(ahorro_mes, 2)} EUR", 1, 1, 'R')

    pdf.ln(10)

    # 4. RANKING DE COMPAÑÍAS
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "COMPARATIVA DE OTRAS COMPAÑÍAS (AHORRO TOTAL):", ln=True)
    
    pdf.set_font('Arial', '', 10)
    for i, row in ranking_real.iterrows():
        color = (40, 180, 99) if row[1] > 0 else (203, 67, 53)
        pdf.set_text_color(0)
        pdf.cell(100, 8, f"{row[0]}:", 0)
        pdf.set_text_color(*color)
        pdf.cell(0, 8, f"{round(row[1], 2)} EUR", 0, 1)

    return pdf.output()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Energetika | Generador de Informes", layout="centered")

st.title("📄 Generador de Informes Energetika")
st.write("Sube el archivo Excel generado por el comparador para crear el PDF para el cliente.")

archivo_excel = st.file_uploader("Cargar Excel (estudio_ahorro_energetico.xlsx)", type="xlsx")

if archivo_excel:
    try:
        # Leer las dos pestañas necesarias
        df_detalle = pd.read_excel(archivo_excel, sheet_name='Detalle')
        df_ranking = pd.read_excel(archivo_excel, sheet_name='Ranking')
        
        st.success("✅ Excel cargado correctamente")
        
        if st.button("🎨 Generar PDF Profesional"):
            with st.spinner("Creando informe..."):
                pdf_bytes = generar_pdf(df_detalle, df_ranking)
                
                st.download_button(
                    label="📥 Descargar Informe PDF para el Cliente",
                    data=bytes(pdf_bytes),
                    file_name=f"Informe_Ahorro_Energetika_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error al procesar el Excel: {e}. Asegúrate de que las pestañas se llamen 'Detalle' y 'Ranking'.")
        )
