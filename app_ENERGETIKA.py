import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Energetika | Generador de Informes", layout="centered")

class EnergetikaPDF(FPDF):
    def header(self):
        # Logo en la parte superior derecha (con manejo de error si no existe)
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
        self.cell(0, 10, 'Este informe es una simulación basada en datos de facturación facilitados por el cliente.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking):
    try:
        pdf = EnergetikaPDF()
        pdf.add_page()

        # 1. VALIDACIÓN Y LIMPIEZA DE DATOS
        # Aseguramos que los nombres de las columnas coincidan con tu Excel
        # ranking: [Compañía/Tarifa, Ahorro]
        # detalle: [Mes/Fecha, Compañía/Tarifa, Coste (€), Ahorro, Dias_Factura, Estado]
        
        # Filtrar la factura actual para encontrar la mejor oferta real
        ranking_ofertas = df_ranking[df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False) == False]
        if ranking_ofertas.empty:
            return None
            
        ganadora_row = ranking_ofertas.sort_values(by=ranking_ofertas.columns[1], ascending=False).iloc[0]
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_periodo = ganadora_row.iloc[1]

        # 2. CALCULAR AHORRO ANUAL ESTIMADO
        num_facturas = df_detalle['Mes/Fecha'].nunique()
        ahorro_anual = (ahorro_total_periodo / num_facturas) * 12 if num_facturas > 0 else 0

        # 3. CUADRO DESTACADO
        pdf.set_fill_color(235, 245, 255) 
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 15, f" RECOMENDACIÓN: {str(nombre_ganadora).upper()}", ln=True, fill=True, align='C')
        pdf.ln(5)

        # 4. MÉTRICAS DE AHORRO
        pdf.set_text_color(0)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(95, 10, f"Ahorro total en el periodo analizado:", 0)
        pdf.set_text_color(46, 139, 87) # Verde bosque
        pdf.cell(0, 10, f"{round(float(ahorro_total_periodo), 2)} EUR", ln=True)
        
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(0)
        pdf.cell(95, 12, f"AHORRO ANUAL ESTIMADO:", 0)
        pdf.set_text_color(46, 139, 87)
        pdf.cell(0, 12, f"{round(float(ahorro_anual), 2)} EUR / AÑO", ln=True)
        pdf.ln(10)

        # 5. TABLA DE DETALLE (FACTURA A FACTURA)
        pdf.set_text_color(0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "DESGLOSE DE LAS FACTURAS ANALIZADAS:", ln=True)
        
        # Cabeceras de tabla
        pdf.set_fill_color(50, 50, 50)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(50, 8, " Fecha / Mes", 1, 0, 'C', True)
        pdf.cell(45, 8, " Factura Cliente", 1, 0, 'C', True)
        pdf.cell(45, 8, " Oferta Propuesta", 1, 0, 'C', True)
        pdf.cell(50, 8, " Ahorro Mes", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 9)
        
        fechas = df_detalle['Mes/Fecha'].unique()
        for fecha in fechas:
            datos_mes = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                # Localizamos coste actual y coste de la ganadora
                v_actual = datos_mes[datos_mes['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                v_mejor = datos_mes[datos_mes['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_m = v_actual - v_mejor

                pdf.cell(50, 8, f" {fecha}", 1)
                pdf.cell(45, 8, f" {round(float(v_actual), 2)} EUR", 1, 0, 'R')
                pdf.cell(45, 8, f" {round(float(v_mejor), 2)} EUR", 1, 0, 'R')
                pdf.cell(50, 8, f" {round(float(ahorro_m), 2)} EUR", 1, 1, 'R')
            except:
                continue # Si falta un dato en una fila, salta a la siguiente sin romper el programa

        pdf.ln(10)
        # 6. RANKING TOP 5
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "ESTUDIO COMPARATIVO DE MERCADO (TOP OPCIONES):", ln=True)
        pdf.set_font('Arial', '', 9)
        
        top_8 = ranking_ofertas.sort_values(by=ranking_ofertas.columns[1], ascending=False).head(8)
        for _, row in top_8.iterrows():
            pdf.set_text_color(0)
            pdf.cell(100, 7, f" {row.iloc[0]}", 0)
            pdf.set_text_color(46, 139, 87) if row.iloc[1] > 0 else pdf.set_text_color(178, 34, 34)
            pdf.cell(0, 7, f"{round(float(row.iloc[1]), 2)} EUR", 0, 1)

        return pdf.output()
    except Exception as e:
        st.error(f"Fallo crítico al generar PDF: {e}")
        return None

# --- INTERFAZ ---
st.title("📄 Generador de Auditorías Energetika")
st.markdown("Carga el archivo Excel de resultados para generar el PDF profesional.")

archivo = st.file_uploader("Subir estudio_ahorro_energetico.xlsx", type=["xlsx"])

if archivo:
    try:
        # Cargamos las pestañas. Si los nombres fallan, avisamos al usuario.
        hojas = pd.ExcelFile(archivo).sheet_names
        if "Detalle" in hojas and "Ranking" in hojas:
            df_det = pd.read_excel(archivo, sheet_name="Detalle")
            df_ran = pd.read_excel(archivo, sheet_name="Ranking")
            
            st.success("✅ Archivo leído correctamente.")
            
            if st.button("🚀 Crear Informe PDF para el Cliente"):
                with st.spinner("Generando documento..."):
                    pdf_bytes = generar_pdf(df_det, df_ran)
                    if pdf_bytes:
                        st.download_button(
                            label="📥 Descargar Auditoría PDF",
                            data=bytes(pdf_bytes),
                            file_name=f"Auditoria_Energetika_{datetime.now().strftime('%d%m%Y')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
        else:
            st.error(f"El Excel no tiene las pestañas necesarias ('Detalle' y 'Ranking'). Hojas encontradas: {hojas}")
    except Exception as e:
        st.error(f"Error al procesar el Excel: {e}")
