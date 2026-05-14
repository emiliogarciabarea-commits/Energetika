import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
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
        self.set_font('Arial', 'I', 9) 
        self.set_text_color(20, 50, 100) 
        texto_contacto = "www.energetikapro.com  |  Tel: +34 614 676 150"
        self.cell(0, 5, texto_contacto, ln=True, link="http://www.energetikapro.com")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Informe generado por Energetika - Auditoría Profesional Independiente.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking, df_consumos, df_precios_ganadora, nombre_cliente, direccion_cliente, compania_actual_manual, mostrar_nombres):
    try:
        pdf = EnergetikaPDF()
        
        # --- PROCESAMIENTO PREVIO ---
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)].copy()
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        nombre_busqueda_ganadora = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False).iloc[0, 0]

        if not mostrar_nombres:
            mapeo_nombres = {n: "Tarifa Óptima Energetika" if i==0 else f"Alternativa de Mercado {chr(64+i)}" 
                            for i, n in enumerate(ranking_ordenado.iloc[:, 0])}
            ranking_ordenado.iloc[:, 0] = ranking_ordenado.iloc[:, 0].map(mapeo_nombres)
            nombre_ganadora = "Tarifa Óptima Energetika"
        else:
            nombre_ganadora = ranking_ordenado.iloc[0, 0]

        ahorro_total_periodo = ranking_real.iloc[:, 1].max()
        coste_actual_total = df_detalle[df_detalle['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].sum()
        porcentaje_ahorro = (ahorro_total_periodo / coste_actual_total) * 100 if coste_actual_total > 0 else 0
        
        dias = df_consumos['Días'].sum()
        ahorro_anual_iva = ((ahorro_total_periodo / dias) * 365 * 1.21) if dias > 0 else 0
        costo_inaccion_5anos = ahorro_anual_iva * 5
        primer_nombre = nombre_cliente.split()[0] if nombre_cliente else "cliente"

        # PÁGINA 1: PORTADA IMPACTO
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 22); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, f"¡Hola, {primer_nombre}!", ln=True, align='C')
        pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 10, "Analizamos su consumo para optimizar su rentabilidad energética.", align='C')
        
        pdf.ln(10)
        pdf.set_fill_color(240, 248, 255); pdf.rect(20, 105, 170, 75, 'F')
        pdf.set_y(112); pdf.set_font('Arial', 'B', 15); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "AHORRO ANUAL DISPONIBLE:", ln=True, align='C')
        pdf.set_font('Arial', 'B', 40); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 22, f"{round(ahorro_anual_iva, 2)} EUR", ln=True, align='C')
        
        # Bloque de costo de inacción (Psicología de ventas)
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, f"ATENCIÓN: Mantener su contrato actual le costaría {round(costo_inaccion_5anos, 0)} EUR extra en 5 años", ln=True, align='C')

        # PÁGINA 2: ANÁLISIS Y SELLO INDEPENDENCIA
        pdf.add_page()
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(100)
        pdf.cell(0, 8, "ANÁLISIS TÉCNICO DE MERCADO", border='B', ln=True)
        pdf.ln(4)
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(45, 8, "Cliente:", 0); pdf.set_font('Arial', '', 11); pdf.cell(0, 8, nombre_cliente, ln=True)
        pdf.cell(45, 8, "Suministro Actual:", 0); pdf.set_text_color(200, 0, 0); pdf.cell(0, 8, compania_actual_manual, ln=True)
        
        # Sello de Independencia
        pdf.set_xy(130, 45); pdf.set_font('Arial', 'I', 8); pdf.set_text_color(50, 50, 150)
        pdf.multi_cell(60, 4, "Verificado: Comparativa objetiva entre +50 comercializadoras. Energetika no tiene exclusividad con ninguna marca.", border=1, align='C')
        
        pdf.set_xy(10, 75)
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "1. COMPARATIVA DE COSTES MENSUALES", ln=True)
        pdf.set_x(25); pdf.set_fill_color(210, 225, 240); pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0)
        pdf.cell(40, 7, " Periodo", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True); pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)
        
        meses_grafica, ahorros_grafica = [], []
        for fecha in df_consumos['Fecha'].unique():
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_busqueda_ganadora]['Coste (€)'].values[0]
                ahorro_mes = c_act - c_pro
                meses_grafica.append(str(fecha)); ahorros_grafica.append(ahorro_mes)
                pdf.set_x(25); pdf.set_font('Arial', '', 8)
                pdf.cell(40, 7, f" {fecha}", 1); pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R')
                pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                pdf.set_text_color(34, 139, 34) if ahorro_mes > 0 else pdf.set_text_color(200, 0, 0)
                pdf.cell(40, 7, f" {round(ahorro_mes, 2)} EUR", 1, 1, 'R'); pdf.set_text_color(0)
            except: continue

        # Gráfica
        pdf.ln(5)
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.bar(meses_grafica, ahorros_grafica, color=['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica], edgecolor='black')
        ax.axhline(0, color='black', linewidth=0.8); plt.xticks(rotation=45); plt.tight_layout()
        grafica_path = "temp_plot.png"; fig.savefig(grafica_path, dpi=300); plt.close(fig); pdf.image(grafica_path, x=45, w=120)

        # Ranking
        pdf.ln(5); pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "2. RANKING DE OPCIONES ANALIZADAS", ln=True)
        pdf.set_x(35); pdf.set_fill_color(20, 50, 100); pdf.set_text_color(255); pdf.cell(80, 7, " Compañía / Tarifa", 1, 0, 'L', True); pdf.cell(60, 7, " Ahorro Total Detectado", 1, 1, 'C', True)
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for _, row in ranking_ordenado.head(5).iterrows():
            pdf.set_x(35); pdf.cell(80, 7, f" {row.iloc[0]}", 1); pdf.set_text_color(34, 139, 34); pdf.cell(60, 7, f" +{round(row.iloc[1], 2)} EUR", 1, 1, 'C'); pdf.set_text_color(0)

        # PÁGINA 3: CIERRE COMERCIAL
        pdf.add_page(); pdf.set_fill_color(230, 240, 255); pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, " CONCLUSIÓN Y PRÓXIMOS PASOS", ln=True, fill=True, align='C')
        pdf.ln(15) 
        pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 7, f"Basándonos en su histórico de consumo, la recomendación de Energetika es tramitar el cambio a:", align='C')
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 16); pdf.set_text_color(20, 50, 100); pdf.cell(0, 12, f"{str(nombre_ganadora).upper()}", ln=True, align='C')
        pdf.set_font('Arial', 'B', 13); pdf.set_text_color(34, 139, 34); pdf.cell(0, 12, f"AHORRO TOTAL DISPONIBLE: {round(ahorro_anual_iva, 2)} EUR / AÑO", ln=True, align='C')
        
        pdf.ln(20)
        pdf.set_font('Arial', '', 10); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 6, "Como consultores, nosotros nos encargamos de toda la gestión administrativa del cambio sin costes adicionales. Para activar estas condiciones, contacte con su asesor asignado.", align='C')
        
        pdf.ln(10)
        url_wa = "https://wa.me/34614676150?text=Hola,%20quiero%20activar%20la%20Tarifa%20Optima%20de%20mi%20estudio"
        if os.path.exists("Whatsapp.png"):
            pdf.image("Whatsapp.png", x=97, y=pdf.get_y(), w=16, link=url_wa)

        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"Error técnico: {e}"); return None

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador Pro | Energetika")
c1, c2 = st.columns(2)
with c1: 
    nombre_cliente = st.text_input("Nombre completo cliente:", "Nombre Cliente")
    direccion_cliente = st.text_input("Dirección:", "Calle Ejemplo 123")
with c2: 
    compania_actual_manual = st.text_input("Compañía actual:", "Energía XXI")
    opcion_nombres = st.radio("Nomenclatura PDF:", 
                              ("Nombres Reales", "Profesional (Óptima / Alternativas)"))

mostrar_nombres = True if opcion_nombres == "Nombres Reales" else False
archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if archivo:
    try:
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        df_pre = pd.read_excel(archivo, sheet_name=3)

        st.success("✅ Excel cargado.")
        if st.button("🚀 Generar PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran, df_con, df_pre, nombre_cliente, direccion_cliente, compania_actual_manual, mostrar_nombres)
            if pdf_bytes:
                st.download_button(label="📥 Descargar Informe", data=pdf_bytes, file_name=f"Estudio_{nombre_cliente.replace(' ', '_')}.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Error: {e}")
