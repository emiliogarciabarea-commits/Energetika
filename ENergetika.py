
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

        # 2. TABLA 1: CONSUMOS (AZUL CORPORATIVO)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0)
        pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        
        pdf.set_x(30)
        pdf.set_fill_color(20, 50, 100) # AZUL LOGO
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

        # 3. TABLA 2 Y GRÁFICA DE BARRAS (AZUL CORPORATIVO)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0)
        pdf.cell(0, 10, "2. COMPARATIVA DE COSTES Y AHORRO MENSUAL", ln=True)
        
        pdf.set_x(25)
        pdf.set_fill_color(20, 50, 100) # AZUL LOGO
        pdf.set_text_color(255)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(40, 7, " Periodo", 1, 0, 'C', True)
        pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True)
        pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True)
        pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)

        pdf.set_font('Arial', '', 8)
        meses_grafica = []
        ahorros_grafica = []

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
                pdf.cell(40, 7, f" {fecha}", 1)
                pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R')
                pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                
                if ahorro_mes > 0:
                    pdf.set_text_color(34, 139, 34)
                    txt_ahorro = f" +{round(ahorro_mes, 2)} EUR"
                elif ahorro_mes < 0:
                    pdf.set_text_color(200, 0, 0)
                    txt_ahorro = f" {round(ahorro_mes, 2)} EUR"
                else:
                    pdf.set_text_color(0)
                    txt_ahorro = f" {round(ahorro_mes, 2)} EUR"
                
                pdf.cell(40, 7, txt_ahorro, 1, 1, 'R')
                pdf.set_text_color(0)
            except: continue

        fig, ax = plt.subplots(figsize=(8, 4))
        colores = ['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica]
        ax.bar(meses_grafica, ahorros_grafica, color=colores, edgecolor='black', alpha=0.8)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_ylabel('Ahorro (€)')
        ax.set_title('Ahorro Mensual Estimado')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        grafica_path = "temp_plot.png"
        fig.savefig(grafica_path, dpi=300)
        plt.close(fig) 
        
        pdf.ln(5)
        pdf.image(grafica_path, x=45, w=120)
        pdf.ln(5)

        # --- SECCIÓN: GRÁFICO DE PASTEL (COLORES CLAROS) ---
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"4. DESGLOSE DE COSTES ESTIMADOS ({nombre_ganadora})", ln=True)

        total_potencia = sum(df_consumos['Potencia (kW)'] * df_consumos['Días'] * 0.13)
        total_energia = sum((df_consumos['Consumo Punta (kWh)'] + df_consumos['Consumo Llano (kWh)'] + df_consumos['Consumo Valle (kWh)']) * 0.15)
        total_excedente = sum(df_consumos['Excedente (kWh)'] * 0.05)

        labels = ['Potencia (Fijo)', 'Energía (Consumo)']
        values = [total_potencia, total_energia]
        colors_pie = ['#A9CCE3', '#ABEBC6'] # Azul claro y Verde claro

        if total_excedente > 0:
            labels.append('Excedentes')
            values.append(total_excedente)
            colors_pie.append('#FCF3CF') # Amarillo claro

        fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
        ax_pie.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors_pie, wedgeprops={'edgecolor': 'white'})
        ax_pie.axis('equal') 
        plt.tight_layout()

        pie_path = "temp_pie.png"
        fig_pie.savefig(pie_path, dpi=300)
        plt.close(fig_pie)

        pdf.image(pie_path, x=55, w=100)
        pdf.ln(5)

        # 4. TABLA 3: TOP 5
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0)
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

        # --- SALTO DE PÁGINA PARA LA CONCLUSIÓN FINAL ---
        pdf.add_page() 

        num_facturas = len(lista_fechas)
        ahorro_anual_sin_iva = (ahorro_total_periodo / num_facturas) * 12 if num_facturas > 0 else 0
        ahorro_anual_con_iva = ahorro_anual_sin_iva * 1.21 

        pdf.set_fill_color(230, 240, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 15, " CONCLUSIÓN Y RECOMENDACIÓN FINAL", ln=True, fill=True, align='C')
        pdf.ln(5)
        
        pdf.set_x(20)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(170, 8, "Tras analizar su historial de consumo, la opción más eficiente para su suministro es la tarifa:", border='TLR', align='C')
        
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(20, 50, 100)
        pdf.cell(170, 10, f"{str(nombre_ganadora).upper()}", border='LR', ln=True, align='C')
        
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(170, 10, f"AHORRO ANUAL ESTIMADO (SIN IVA): {round(ahorro_anual_sin_iva, 2)} EUR", border='LR', ln=True, align='C')
        
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(34, 139, 34)
        pdf.cell(170, 12, f"AHORRO ANUAL ESTIMADO (CON IVA 21%): {round(ahorro_anual_con_iva, 2)} EUR / AÑO", border='BLR', ln=True, align='C')

        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# --- INTERFAZ ---
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
        
        st.success("✅ Excel cargado.")
        
        if st.button("🚀 Generar PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran, df_con, nombre_cliente, direccion_cliente, compania_actual_manual)
            if pdf_bytes:
                st.download_button(
                    label="📥 Descargar Informe",
                    data=pdf_bytes,
                    file_name=f"Auditoria_{nombre_cliente.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error("Error en las pestañas del Excel.")
