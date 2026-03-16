
import streamlit as st
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # <--- CRUCIAL: Fuerza el backend para servidores web
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

        # 2. TABLA 1: RESUMEN DE CONSUMOS
        pdf.set_text_color(0)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        
        pdf.set_x(30)
        pdf.set_fill_color(100, 100, 100)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(45, 7, " Mes de Factura", 1, 0, 'C', True)
        pdf.cell(50, 7, " Consumo Total (kWh)", 1, 0, 'C', True)
        pdf.cell(55, 7, " Potencia Contratada", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 8)
        for fecha in lista_fechas:
            row = df_consumos[df_consumos['Fecha'] == fecha].iloc[0]
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.set_x(30)
            pdf.cell(45, 7, f" {fecha}", 1)
            pdf.cell(50, 7, f" {round(total_kwh, 2)} kWh", 1, 0, 'C')
            pdf.cell(55, 7, f" {row['Potencia (kW)']} kW", 1, 1, 'C')
        
        pdf.ln(8)

        # 3. TABLA 2 Y LÓGICA DE GRÁFICA
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, "2. COMPARATIVA DE COSTES Y AHORRO MENSUAL", ln=True)
        
        pdf.set_x(25)
        pdf.set_fill_color(50, 50, 50)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(40, 7, " Periodo", 1, 0, 'C', True)
        pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True)
        pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True)
        pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)

        pdf.set_text_color(0)
        pdf.set_font('Arial', '', 8)
        
        meses_grafica = []
        ahorros_grafica = []

        for fecha in lista_fechas:
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_mes = float(c_act - c_pro)
                
                meses_grafica.append(str(fecha))
                ahorros_grafica.append(ahorro_mes)

                pdf.set_x(25)
                pdf.cell(40, 7, f" {fecha}", 1)
                pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R')
                pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                pdf.cell(40, 7, f" {round(ahorro_mes, 2)} EUR", 1, 1, 'R')
            except: continue

        # --- GENERACIÓN DE GRÁFICA CORREGIDA ---
        plt.clf() # Limpia cualquier dibujo previo
        fig, ax = plt.subplots(figsize=(8, 4))
        colores = ['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica]
        ax.bar(meses_grafica, ahorros_grafica, color=colores, edgecolor='black', alpha=0.8)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_ylabel('Ahorro (€)', fontsize=10)
        ax.set_title(f'Proyección de Ahorro Mensual con {nombre_ganadora}', fontsize=12, pad=15)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        
        grafica_path = "temp_grafica.png"
        fig.savefig(grafica_path, dpi=300, bbox_inches='tight')
        plt.close(fig) # Cierra la figura para liberar memoria
        
        pdf.ln(5)
        pdf.image(grafica_path, x=45, w=120)
        pdf.ln(5)

        # 4. TABLA 3: TOP 5
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, "3. COMPARATIVA CON OTRAS OPCIONES DE MERCADO", ln=True)
        pdf.set_x(35)
        pdf.set_fill_color(20, 50, 100)
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 8)
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

        pdf.ln(10)

        # 5. CONCLUSIÓN FINAL EN TABLA
        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 15, " CONCLUSIÓN Y RECOMENDACIÓN FINAL", ln=True, fill=True, align='C')
        pdf.ln(5)

        num_facturas = len(lista_fechas)
        ahorro_anual = (ahorro_total_periodo / num_facturas) * 12 if num_facturas > 0 else 0

        pdf.set_x(20)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(170, 8, "Tras analizar su historial de consumo, la opción más eficiente para su suministro es la tarifa:", border='TLR', align='C')
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(170, 10, f"{str(nombre_ganadora).upper()}", border='LR', ln=True, align='C')
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(170, 12, f"AHORRO ANUAL ESTIMADO: {round(float(ahorro_anual), 2)} EUR / AÑO", border='BLR', ln=True, align='C')

        return pdf.output()
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")
        return None

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador Pro | Energetika")

col1, col2 = st.columns(2)
with col1:
    nombre_cliente = st.text_input("Nombre del cliente:", "Cliente Energetika")
    direccion_cliente = st.text_input("Dirección del cliente:", "Calle Ejemplo 123")
with col2:
    compania_actual_manual = st.text_input("Compañía actual:", "Energía XXI")

archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if archivo:
    try:
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        
        st.success("✅ Excel cargado con éxito.")
        
        if st.button("🚀 Generar Informe Completo"):
            pdf_out = generar_pdf(df_det, df_ran, df_con, nombre_cliente, direccion_cliente, compania_actual_manual)
            if pdf_out:
                st.download_button(
                    label="📥 Descargar Auditoría Energetika",
                    data=bytes(pdf_out),
                    file_name=f"Auditoria_{nombre_cliente.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error: Asegúrate de que el Excel tiene las pestañas correctas.")
