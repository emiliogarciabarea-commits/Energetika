import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import qrcode  # Nueva librería para el QR

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
        self.cell(0, 10, 'Informe generado por Energetika - Auditoría Profesional.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking, df_consumos, df_precios_ganadora, nombre_cliente, direccion_cliente, compania_actual_manual, mostrar_nombres):
    try:
        pdf = EnergetikaPDF()
        
        # --- PROCESAMIENTO PREVIO ---
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)].copy()
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        nombre_busqueda_ganadora = ranking_ordenado.iloc[0, 0]

        if not mostrar_nombres:
            mapeo_nombres = {n: "Tarifa Óptima Energetika" if i==0 else f"Alternativa de Mercado {chr(64+i)}" 
                            for i, n in enumerate(ranking_ordenado.iloc[:, 0])}
            ranking_ordenado.iloc[:, 0] = ranking_ordenado.iloc[:, 0].map(mapeo_nombres)
            nombre_ganadora = "Tarifa Óptima Energetika"
        else:
            nombre_ganadora = nombre_busqueda_ganadora

        ahorro_total_periodo = ranking_real.iloc[:, 1].max()
        coste_actual_total = df_detalle[df_detalle['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].sum()
        porcentaje_ahorro = (ahorro_total_periodo / coste_actual_total) * 100 if coste_actual_total > 0 else 0
        
        dias = df_consumos['Días'].sum()
        ahorro_anual_con_iva = ((ahorro_total_periodo / dias) * 365 * 1.21) if dias > 0 else 0
        # Cálculo de coste de inacción (5 años)
        coste_5_anos = ahorro_anual_con_iva * 5

        # PÁGINA 1: PORTADA
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 22); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, f"¡Hola, {nombre_cliente.split()[0]}!", ln=True, align='C')
        pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 10, "Tu contrato actual está por encima del precio óptimo de mercado.\nHemos diseñado una estrategia para optimizar tu gasto.", align='C')
        
        pdf.ln(15); pdf.set_fill_color(240, 248, 255); pdf.rect(20, 110, 170, 65, 'F')
        pdf.set_y(118); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "AHORRO ANUAL ESTIMADO:", ln=True, align='C')
        pdf.set_font('Arial', 'B', 45); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 25, f"{round(ahorro_anual_con_iva, 2)} EUR", ln=True, align='C')
        pdf.set_font('Arial', 'B', 12); pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, f"COSTE DE NO ACTUAR (5 AÑOS): - {round(coste_5_anos, 2)} EUR", ln=True, align='C')

        # PÁGINA 2: ANÁLISIS
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(45, 8, "Suministro Actual:", 0); pdf.set_text_color(200, 0, 0); pdf.cell(0, 8, compania_actual_manual, ln=True)
        pdf.ln(5)
        
        # Tabla comparativa
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "1. ANÁLISIS DE EFICIENCIA POR PERIODO", ln=True)
        pdf.set_x(25); pdf.set_fill_color(210, 225, 240); pdf.set_font('Arial', 'B', 8); pdf.set_text_color(0)
        pdf.cell(40, 7, " Periodo", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True); pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)
        
        meses_grafica, ahorros_grafica = [], []
        for fecha in df_consumos['Fecha'].unique():
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_busqueda_ganadora]['Coste (€)'].values[0]
                ahorro_m = c_act - c_pro
                meses_grafica.append(str(fecha)); ahorros_grafica.append(ahorro_m)
                pdf.set_x(25); pdf.set_font('Arial', '', 8); pdf.cell(40, 7, f" {fecha}", 1)
                pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R'); pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                pdf.set_text_color(34, 139, 34) if ahorro_m > 0 else pdf.set_text_color(200, 0, 0)
                pdf.cell(40, 7, f" {round(ahorro_m, 2)} EUR", 1, 1, 'R'); pdf.set_text_color(0)
            except: continue

        # Gráfica
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.bar(meses_grafica, ahorros_grafica, color=['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica])
        ax.axhline(0, color='black', linewidth=0.5); plt.xticks(rotation=30, fontsize=8); plt.tight_layout()
        fig.savefig("temp_plot.png", dpi=200); plt.close(fig); pdf.image("temp_plot.png", x=45, w=120)

        # PÁGINA 3: CONCLUSIÓN + QR
        pdf.add_page(); pdf.set_fill_color(20, 50, 100); pdf.set_font('Arial', 'B', 14); pdf.set_text_color(255)
        pdf.cell(0, 12, " RECOMENDACIÓN PROFESIONAL", ln=True, fill=True, align='C')
        pdf.ln(10); pdf.set_text_color(0); pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 7, "Tras auditar los precios de más de 50 comercializadoras, nuestra recomendación es el cambio inmediato a la siguiente tarifa para detener el sobrecoste:", align='C')
        
        pdf.ln(5); pdf.set_x(30); pdf.set_font('Arial', 'B', 14); pdf.set_text_color(20, 50, 100)
        pdf.cell(150, 15, f"{str(nombre_ganadora).upper()}", border=1, ln=True, align='C')
        pdf.set_x(30); pdf.set_font('Arial', 'B', 12); pdf.set_text_color(34, 139, 34)
        pdf.cell(150, 10, f"AHORRO TOTAL GARANTIZADO: {round(porcentaje_ahorro, 1)}%", border='LRB', ln=True, align='C')

        # Sección de cierre con QR
        pdf.ln(20); pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(0, 10, "GESTIÓN DE CONTRATACIÓN", ln=True, align='C')
        
        url_wa = "https://wa.me/34614676150?text=Hola,%20quiero%20tramitar%20el%20ahorro%20de%20mi%20estudio"
        qr = qrcode.make(url_wa); qr.save("temp_qr.png")
        
        pdf.image("temp_qr.png", x=85, y=pdf.get_y()+2, w=40)
        pdf.set_y(pdf.get_y() + 45)
        pdf.set_font('Arial', 'I', 9); pdf.set_text_color(100)
        pdf.cell(0, 5, "Escanea este código con tu móvil para validar tu oferta vía WhatsApp", ln=True, align='C')

        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"Error técnico: {e}"); return None

# --- INTERFAZ ---
st.title("📄 Generador Pro | Energetika")
c1, c2 = st.columns(2)
with c1: 
    nombre_cliente = st.text_input("Nombre cliente:", "Nombre Cliente")
    direccion_cliente = st.text_input("Dirección:", "Calle Ejemplo 123")
with c2: 
    compania_actual_manual = st.text_input("Compañía actual:", "Energía XXI")
    opcion_nombres = st.radio("Formato PDF:", ("Nombres Reales", "Nomenclatura Energetika"))

archivo = st.file_uploader("Sube el Excel", type=["xlsx"])
if archivo:
    try:
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        df_pre = pd.read_excel(archivo, sheet_name=3)
        
        if st.button("🚀 Generar Estudio"):
            res = generar_pdf(df_det, df_ran, df_con, df_pre, nombre_cliente, direccion_cliente, compania_actual_manual, (opcion_nombres == "Nombres Reales"))
            if res:
                st.download_button("📥 Descargar Informe", res, f"Estudio_{nombre_cliente.replace(' ','_')}.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Error: {e}")
