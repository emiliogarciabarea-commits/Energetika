
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
        self.set_text_color(20, 50, 100) # Azul Logo
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

def generar_pdf(df_detalle, df_ranking, df_consumos, nombre_cliente, direccion_cliente, compania_actual_manual):
    try:
        pdf = EnergetikaPDF()
        pdf.add_page()

        # 1. PROCESAMIENTO DE DATOS
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        ganadora_row = ranking_ordenado.iloc[0]
        
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_periodo = ganadora_row.iloc[1]
        lista_fechas = df_consumos['Fecha'].unique()

        # --- SECCIÓN: DATOS DEL CLIENTE ---
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(0)
        pdf.cell(45, 8, "Cliente:", 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, nombre_cliente, ln=True)
        
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(45, 8, "Dirección:", 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, direccion_cliente, ln=True)

        pdf.set_font('Arial', 'B', 11)
        pdf.cell(45, 8, "Suministro Actual:", 0)
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(200, 0, 0) 
        pdf.cell(0, 8, compania_actual_manual, ln=True)
        pdf.ln(5)

        # 2. TABLA 1: CONSUMOS
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        
        pdf.set_x(30)
        pdf.set_fill_color(20, 50, 100) # Azul Logo
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(45, 7, " Mes de Factura", 1, 0, 'C', True)
        pdf.cell(50, 7, " Consumo Total (kWh)", 1, 0, 'C', True)
        pdf.cell(55, 7, " Potencia Contratada", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 8)
        fill = False
        for fecha in lista_fechas:
            row = df_consumos[df_consumos['Fecha'] == fecha].iloc[0]
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.set_x(30)
            if fill: pdf.set_fill_color(240, 245, 255)
            pdf.cell(45, 7, f" {fecha}", 1, 0, 'L', fill)
            pdf.cell(50, 7, f" {round(total_kwh, 2)} kWh", 1, 0, 'C', fill)
            pdf.cell(55, 7, f" {row['Potencia (kW)']} kW", 1, 1, 'C', fill)
            fill = not fill
        
        pdf.ln(8)

        # 3. TABLA 2 Y GRÁFICA
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "2. COMPARATIVA DE COSTES Y AHORRO MENSUAL", ln=True)
        
        pdf.set_x(25)
        pdf.set_fill_color(20, 50, 100)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(40, 7, " Periodo", 1, 0, 'C', True)
        pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True)
        pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True)
        pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)

        pdf.set_font('Arial', '', 8)
        meses_grafica = []
        ahorros_grafica = []
        fill = False

        for fecha in lista_fechas:
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_mes = c_act - c_pro
                
                meses_grafica.append(str(fecha))
                ahorros_grafica.append(ahorro_mes)

                pdf.set_x(25)
                pdf.set_text_color(0)
                if fill: pdf.set_fill_color(240, 245, 255)
                pdf.cell(40, 7, f" {fecha}", 1, 0, 'L', fill)
                pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R', fill)
                pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R', fill)
                
                if ahorro_mes > 0:
                    pdf.set_text_color(34, 139, 34)
                    txt = f" +{round(ahorro_mes, 2)} EUR"
                else:
                    pdf.set_text_color(200, 0, 0)
                    txt = f" {round(ahorro_mes, 2)} EUR"
                
                pdf.cell(40, 7, txt, 1, 1, 'R', fill)
                fill = not fill
            except: continue

        # Gráfica de Barras
        fig, ax = plt.subplots(figsize=(8, 4))
        colores = ['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica]
        ax.bar(meses_grafica, ahorros_grafica, color=colores, edgecolor='black', alpha=0.8)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_ylabel('Ahorro (€)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        grafica_path = "temp_plot.png"
        fig.savefig(grafica_path, dpi=300)
        plt.close(fig) 
        pdf.ln(5)
        pdf.image(grafica_path, x=45, w=120)

        # --- GRÁFICO DE PASTEL ---
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, f"3. DESGLOSE DE COSTES ESTIMADOS ({nombre_ganadora})", ln=True)

        total_potencia = sum(df_consumos['Potencia (kW)'] * df_consumos['Días'] * 0.13)
        total_energia = sum(df_consumos['Consumo Punta (kWh)'] + df_consumos['Consumo Llano (kWh)']) * 0.15
        
        labels, values, colors_pie = ['Potencia', 'Energía'], [total_potencia, total_energia], ['#143264', '#2ecc71']
        fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
        ax_pie.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors_pie)
        pie_path = "temp_pie.png"
        fig_pie.savefig(pie_path, dpi=300)
        plt.close(fig_pie)
        pdf.image(pie_path, x=55, w=100)

        # --- SALTO DE PÁGINA PARA CONCLUSIÓN ---
        pdf.add_page()

        # 4. TABLA TOP 5
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "4. OTRAS OPCIONES DE MERCADO ANALIZADAS", ln=True)
        pdf.set_x(35)
        pdf.set_fill_color(20, 50, 100)
        pdf.set_text_color(255)
        pdf.cell(80, 7, " Compañía / Tarifa", 1, 0, 'L', True)
        pdf.cell(60, 7, " Ahorro Total Detectado", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 8)
        for _, row in ranking_ordenado.head(5).iterrows():
            pdf.set_x(35)
            pdf.cell(80, 7, f" {row.iloc[0]}", 1)
            pdf.set_text_color(34, 139, 34)
            pdf.cell(60, 7, f" +{round(row.iloc[1], 2)} EUR", 1, 1, 'C')
            pdf.set_text_color(0)

        # 5. CONCLUSIÓN FINAL (CON IVA)
        pdf.ln(15)
        num_facturas = len(lista_fechas)
        ahorro_anual_base = (ahorro_total_periodo / num_facturas) * 12 if num_facturas > 0 else 0
        ahorro_anual_iva = ahorro_anual_base * 1.21 # Añadiendo el 21% de IVA

        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, " RECOMENDACIÓN FINAL", ln=True, fill=True, align='C')
        pdf.ln(5)
        
        pdf.set_x(20)
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0)
        pdf.multi_cell(170, 8, f"Basado en su consumo, le recomendamos cambiar a {nombre_ganadora.upper()}. El beneficio económico real proyectado es de:", border='TLR', align='C')
        
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(170, 15, f"{round(ahorro_anual_iva, 2)} EUR / AÑO (IVA INCLUIDO)", border='BLR', ln=True, align='C')

        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- INTERFAZ ---
st.title("📄 Generador Energetika")
col1, col2 = st.columns(2)
with col1:
    nombre_cliente = st.text_input("Cliente:", "Sheila Maria Gonzalez Ordoñez")
    direccion_cliente = st.text_input("Dirección:", "Calle Ramón Pérez 10")
with col2:
    compania_actual_manual = st.text_input("Compañía actual:", "Repsol")

archivo = st.file_uploader("Excel de Comparativa", type=["xlsx"])

if archivo:
    df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
    df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
    df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
    
    if st.button("🚀 Crear Informe PDF"):
        pdf_bytes = generar_pdf(df_det, df_ran, df_con, nombre_cliente, direccion_cliente, compania_actual_manual)
        if pdf_bytes:
            st.download_button("📥 Descargar Auditoría", pdf_bytes, f"Auditoria_{nombre_cliente}.pdf", "application/pdf")
