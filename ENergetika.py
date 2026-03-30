import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import qrcode  # Librería para el QR

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

def generar_pdf(df_detalle, df_ranking, df_consumos, df_precios_ganadora, nombre_cliente, direccion_cliente, compania_actual_manual):
    def encode_text(text):
        """Limpia el texto para que sea compatible con el encoding latin-1 de FPDF"""
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    try:
        pdf = EnergetikaPDF()
        
        # --- PROCESAMIENTO PREVIO DE DATOS (FLEXIBLE) ---
        # 1. Encontrar la etiqueta "ACTUAL" dinámicamente
        mask_actual = df_detalle['Compañía/Tarifa'].str.contains("ACTUAL", na=False, case=False)
        if not mask_actual.any():
            st.error("No se encontró la fila 'ACTUAL' en la columna Compañía/Tarifa")
            return None
        label_actual = df_detalle[mask_actual]['Compañía/Tarifa'].unique()[0]

        # 2. Filtrar ranking y obtener ganadora
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False, case=False)]
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        ganadora_row = ranking_ordenado.iloc[0]
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_periodo = ganadora_row.iloc[1]
        
        coste_actual_total = df_detalle[df_detalle['Compañía/Tarifa'] == label_actual]['Coste (€)'].sum()
        porcentaje_ahorro_ganadora = (ahorro_total_periodo / coste_actual_total) * 100 if coste_actual_total > 0 else 0
        
        lista_fechas = df_consumos['Fecha'].unique()
        num_facturas = len(lista_fechas)
        ahorro_anual_sin_iva = (ahorro_total_periodo / num_facturas) * 12 if num_facturas > 0 else 0
        ahorro_anual_con_iva = ahorro_anual_sin_iva * 1.21

        primer_nombre = nombre_cliente.split()[0] if nombre_cliente else "cliente"

        # PÁGINA 1
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 22); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, encode_text(f"¡Hola, {primer_nombre}!"), ln=True, align='C')
        pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 10, encode_text("Hemos analizado tus facturas recientes y tenemos excelentes noticias.\nPuedes reducir tu gasto energético significativamente."), align='C')
        pdf.ln(20); pdf.set_fill_color(240, 248, 255); pdf.rect(20, 100, 170, 60, 'F')
        pdf.set_y(110); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "TU AHORRO ANUAL ESTIMADO ES DE:", ln=True, align='C')
        pdf.set_font('Arial', 'B', 40); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 25, f"{round(ahorro_anual_con_iva, 2)} EUR", ln=True, align='C')
        pdf.set_font('Arial', 'I', 11); pdf.set_text_color(100)
        pdf.cell(0, 10, f"(Lo que supone un ahorro del {round(porcentaje_ahorro_ganadora, 1)}% en tu factura)", ln=True, align='C')
        pdf.ln(30); pdf.set_font('Arial', '', 11); pdf.set_text_color(80); pdf.set_x(30)
        pdf.multi_cell(150, 7, encode_text("Este estudio ha sido realizado de forma independiente por Energetika, analizando y comparando entre más de 35 tarifas del mercado actual para encontrar la que mejor se adapta a tu perfil de consumo real."), align='C')

        # PÁGINA 2
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(45, 8, "Cliente:", 0); pdf.set_font('Arial', '', 11); pdf.cell(0, 8, encode_text(nombre_cliente), ln=True)
        pdf.cell(45, 8, encode_text("Dirección:"), 0); pdf.cell(0, 8, encode_text(direccion_cliente), ln=True)
        pdf.set_font('Arial', 'B', 11); pdf.cell(45, 8, "Suministro Actual:", 0); pdf.set_font('Arial', '', 11); pdf.set_text_color(200, 0, 0); pdf.cell(0, 8, encode_text(compania_actual_manual), ln=True)
        pdf.ln(5); pdf.set_font('Arial', 'I', 9); pdf.set_text_color(100)
        pdf.cell(0, 5, encode_text("* Los importes de las siguientes tablas se muestran sin IVA ni impuestos especiales."), ln=True); pdf.ln(2)

        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        pdf.set_x(30); pdf.set_fill_color(210, 225, 240); pdf.set_font('Arial', 'B', 8)
        pdf.cell(45, 7, " Mes de Factura", 1, 0, 'C', True); pdf.cell(50, 7, " Consumo Total (kWh)", 1, 0, 'C', True); pdf.cell(55, 7, " Potencia Contratada", 1, 1, 'C', True)
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for fecha in lista_fechas:
            row = df_consumos[df_consumos['Fecha'] == fecha].iloc[0]
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.set_x(30); pdf.cell(45, 7, f" {fecha}", 1); pdf.cell(50, 7, f" {round(total_kwh, 2)} kWh", 1, 0, 'C'); pdf.cell(55, 7, f" {row['Potencia (kW)']} kW", 1, 1, 'C')
        pdf.ln(8)

        # 2. COMPARATIVA DE COSTES (CORREGIDA)
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "2. COMPARATIVA DE COSTES Y AHORRO MENSUAL", ln=True)
        pdf.set_x(25); pdf.set_fill_color(210, 225, 240); pdf.cell(40, 7, " Periodo", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True); pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)
        pdf.set_font('Arial', '', 8); meses_grafica, ahorros_grafica = [], []
        for fecha in lista_fechas:
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'] == label_actual]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_mes = c_act - c_pro
                meses_grafica.append(str(fecha)); ahorros_grafica.append(ahorro_mes)
                pdf.set_x(25); pdf.set_text_color(0); pdf.cell(40, 7, f" {fecha}", 1); pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R'); pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                if ahorro_mes > 0: pdf.set_text_color(34, 139, 34); txt_ahorro = f" +{round(ahorro_mes, 2)} EUR"
                else: pdf.set_text_color(200, 0, 0); txt_ahorro = f" {round(ahorro_mes, 2)} EUR"
                pdf.cell(40, 7, txt_ahorro, 1, 1, 'R'); pdf.set_text_color(0)
            except: continue

        if meses_grafica:
            pdf.ln(15)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(meses_grafica, ahorros_grafica, color=['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica], edgecolor='black', alpha=0.8)
            ax.axhline(0, color='black', linewidth=0.8); plt.xticks(rotation=45); plt.tight_layout()
            grafica_path = "temp_plot.png"; fig.savefig(grafica_path, dpi=300); plt.close(fig); pdf.image(grafica_path, x=45, w=120)

        # DESGLOSE Y RESTO (SIN CAMBIOS ESTRUCTURALES)
        if pdf.get_y() > 180: pdf.add_page()
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, encode_text(f"4. DESGLOSE DE COSTES ESTIMADOS ({nombre_ganadora})"), ln=True)
        precios = df_precios_ganadora.set_index('Concepto')['Valor']
        total_potencia_real = sum(df_consumos['Potencia (kW)'] * df_consumos['Días'] * (precios.get('P1 Potencia (€/kW/día)', 0) + precios.get('P2 Potencia (€/kW/día)', 0)))
        total_energia_real = sum((df_consumos['Consumo Punta (kWh)'] * precios.get('Energía Punta (€/kWh)', 0)) + (df_consumos['Consumo Llano (kWh)'] * precios.get('Energía Llano (€/kWh)', 0)) + (df_consumos['Consumo Valle (kWh)'] * precios.get('Energía Valle (€/kWh)', 0)))
        total_excedente_real = sum(df_consumos.get('Excedente (kWh)', [0])) * precios.get('Excedente (€/kWh)', 0)
        
        fig_pie, ax_pie = plt.subplots(figsize=(6, 4)); ax_pie.pie([total_potencia_real, total_energia_real], labels=['Potencia', 'Energía'], autopct='%1.1f%%', startangle=140, colors=['#A9CCE3', '#ABEBC6'])
        pie_path = "temp_pie.png"; fig_pie.savefig(pie_path, dpi=300); plt.close(fig_pie); pdf.image(pie_path, x=55, w=100)

        pdf.add_page(); pdf.set_fill_color(230, 240, 255); pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, encode_text(" CONCLUSIÓN Y RECOMENDACIÓN FINAL"), ln=True, fill=True, align='C')
        pdf.ln(5)
        for _, row in ranking_ordenado.head(5).iterrows():
            pdf.set_x(10); pdf.cell(60, 7, encode_text(row.iloc[0]), 1)
            pdf.cell(45, 7, f" {round((row.iloc[1]/num_facturas)*12, 2)} EUR", 1)
            pdf.cell(45, 7, f" {round((row.iloc[1]/num_facturas)*12*1.21, 2)} EUR", 1)
            pdf.set_text_color(34, 139, 34); pdf.cell(40, 7, f" {round((row.iloc[1]/coste_actual_total)*100, 1)}%", 1, 1, 'C'); pdf.set_text_color(0)

        qr = qrcode.QRCode(box_size=6, border=2); qr.add_data("https://wa.me/4915154663318"); qr.make(fit=True)
        qr_path = "temp_qr.png"; qr.make_image().save(qr_path)
        pdf.ln(10); pdf.image(qr_path, x=92, w=25)

        pdf_output = pdf.output(dest='S')
        return pdf_output.encode('latin-1') if isinstance(pdf_output, str) else pdf_output
    except Exception as e:
        st.error(f"Error técnico: {e}"); return None

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador Pro | Energetika")
c1, c2 = st.columns(2)
with c1:
    nombre_cliente = st.text_input("Nombre completo cliente:", "Sheila Maria Gonzalez Ordoñez")
    direccion_cliente = st.text_input("Dirección:", "Calle Ejemplo 123")
with c2:
    compania_actual_manual = st.text_input("Compañía actual:", "Energía XXI")
archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if archivo:
    try:
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        df_pre = pd.read_excel(archivo, sheet_name="Precios Tarifa Ganadora")
        st.success("✅ Excel cargado correctamente.")
        if st.button("🚀 Generar PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran, df_con, df_pre, nombre_cliente, direccion_cliente, compania_actual_manual)
            if pdf_bytes:
                st.download_button("📥 Descargar Informe", pdf_bytes, f"Auditoria_{nombre_cliente.replace(' ', '_')}.pdf", "application/pdf")
    except Exception as e: st.error(f"Error: {e}")
