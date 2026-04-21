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
        # Nueva línea con Web (Clicable) y Teléfono
        self.set_font('Arial', 'I', 9) # Cursiva para diferenciar
        self.set_text_color(20, 50, 100) # Un tono azulado para el link
        texto_contacto = "www.energetikapro.com  |  Tel: +34 614 676 150"
        # El parámetro 'link' permite que al pulsar en el texto abra la web
        self.cell(0, 5, texto_contacto, ln=True, link="http://www.energetikapro.com")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Informe generado por Energetika - Auditoría Profesional.', 0, 0, 'C')

def generar_pdf(df_detalle, df_ranking, df_consumos, df_precios_ganadora, nombre_cliente, direccion_cliente, compania_actual_manual):
    try:
        pdf = EnergetikaPDF()
        
        # --- PROCESAMIENTO PREVIO DE DATOS ---
        ranking_real = df_ranking[~df_ranking.iloc[:, 0].str.contains("ACTUAL", na=False)]
        ranking_ordenado = ranking_real.sort_values(by=ranking_real.columns[1], ascending=False)
        ganadora_row = ranking_ordenado.iloc[0]
        nombre_ganadora = ganadora_row.iloc[0]
        ahorro_total_periodo = ganadora_row.iloc[1]
        
        coste_actual_total = df_detalle[df_detalle['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].sum()
        porcentaje_ahorro_ganadora = (ahorro_total_periodo / coste_actual_total) * 100 if coste_actual_total > 0 else 0
        
        lista_fechas = df_consumos['Fecha'].unique()
        # NUEVA LÓGICA: Cálculo por días reales
        dias_totales_periodo = df_consumos['Días'].sum()
        ahorro_anual_sin_iva = (ahorro_total_periodo / dias_totales_periodo) * 365 if dias_totales_periodo > 0 else 0
        ahorro_anual_con_iva = ahorro_anual_sin_iva * 1.21

        primer_nombre = nombre_cliente.split()[0] if nombre_cliente else "cliente"

        # ==========================================
        # PÁGINA 1: PORTADA DE IMPACTO
        # ==========================================
        pdf.add_page()
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 22); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 15, f"¡Hola, {primer_nombre}!", ln=True, align='C')
        
        pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 10, "Hemos analizado tus facturas recientes y tenemos excelentes noticias.\nPuedes reducir tu gasto energético significativamente.", align='C')
        
        pdf.ln(20); pdf.set_fill_color(240, 248, 255); pdf.rect(20, 110, 170, 60, 'F')
        pdf.set_y(120); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 10, "TU AHORRO ANUAL ESTIMADO ES DE:", ln=True, align='C')
        pdf.set_font('Arial', 'B', 40); pdf.set_text_color(34, 139, 34)
        pdf.cell(0, 25, f"{round(ahorro_anual_con_iva, 2)} EUR", ln=True, align='C')
        
        pdf.set_font('Arial', 'I', 11); pdf.set_text_color(100)
        pdf.cell(0, 10, f"(Lo que supone un ahorro del {round(porcentaje_ahorro_ganadora, 1)}% en tu factura)", ln=True, align='C')
        
        pdf.ln(30); pdf.set_font('Arial', '', 11); pdf.set_text_color(80); pdf.set_x(30)
        pdf.multi_cell(150, 7, "Este estudio ha sido realizado de forma independiente por Energetika, analizando y comparando entre más de 50 tarifas del mercado actual para encontrar la que mejor se adapta a tu perfil de consumo real.", align='C')

        # ==========================================
        # PÁGINA 2: ANÁLISIS DETALLADO
        # ==========================================
        pdf.add_page()
        pdf.set_font('Arial', 'B', 11); pdf.set_text_color(0)
        pdf.cell(45, 8, "Cliente:", 0); pdf.set_font('Arial', '', 11); pdf.cell(0, 8, nombre_cliente, ln=True)
        pdf.cell(45, 8, "Dirección:", 0); pdf.cell(0, 8, direccion_cliente, ln=True)
        pdf.set_font('Arial', 'B', 11); pdf.cell(45, 8, "Suministro Actual:", 0); pdf.set_font('Arial', '', 11); pdf.set_text_color(200, 0, 0); pdf.cell(0, 8, compania_actual_manual, ln=True)
        
        pdf.ln(5); pdf.set_font('Arial', 'I', 9); pdf.set_text_color(100)
        pdf.cell(0, 5, "* Los importes de las siguientes tablas se muestran sin IVA ni impuestos especiales.", ln=True); pdf.ln(2)

        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "1. RESUMEN DE CONSUMOS POR MESES ANALIZADOS", ln=True)
        pdf.set_x(30); pdf.set_fill_color(210, 225, 240); pdf.set_font('Arial', 'B', 8)
        pdf.cell(45, 7, " Mes de Factura", 1, 0, 'C', True); pdf.cell(50, 7, " Consumo Total (kWh)", 1, 0, 'C', True); pdf.cell(55, 7, " Potencia Contratada", 1, 1, 'C', True)
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for fecha in lista_fechas:
            row = df_consumos[df_consumos['Fecha'] == fecha].iloc[0]
            total_kwh = row['Consumo Punta (kWh)'] + row['Consumo Llano (kWh)'] + row['Consumo Valle (kWh)']
            pdf.set_x(30); pdf.cell(45, 7, f" {fecha}", 1); pdf.cell(50, 7, f" {round(total_kwh, 2)} kWh", 1, 0, 'C'); pdf.cell(55, 7, f" {row['Potencia (kW)']} kW", 1, 1, 'C')
        pdf.ln(8)

        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "2. COMPARATIVA DE COSTES Y AHORRO MENSUAL", ln=True)
        pdf.set_x(25); pdf.set_fill_color(210, 225, 240); pdf.cell(40, 7, " Periodo", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Actual", 1, 0, 'C', True); pdf.cell(40, 7, " Coste Propuesta", 1, 0, 'C', True); pdf.cell(40, 7, " Ahorro", 1, 1, 'C', True)
        pdf.set_font('Arial', '', 8); meses_grafica, ahorros_grafica = [], []
        for fecha in lista_fechas:
            mes_data = df_detalle[df_detalle['Mes/Fecha'] == fecha]
            try:
                c_act = mes_data[mes_data['Compañía/Tarifa'].str.contains("ACTUAL", na=False)]['Coste (€)'].values[0]
                c_pro = mes_data[mes_data['Compañía/Tarifa'] == nombre_ganadora]['Coste (€)'].values[0]
                ahorro_mes = c_act - c_pro
                meses_grafica.append(str(fecha)); ahorros_grafica.append(ahorro_mes)
                pdf.set_x(25); pdf.set_text_color(0); pdf.cell(40, 7, f" {fecha}", 1); pdf.cell(40, 7, f" {round(c_act, 2)} EUR", 1, 0, 'R'); pdf.cell(40, 7, f" {round(c_pro, 2)} EUR", 1, 0, 'R')
                if ahorro_mes > 0: pdf.set_text_color(34, 139, 34); txt_ahorro = f" +{round(ahorro_mes, 2)} EUR"
                else: pdf.set_text_color(200, 0, 0); txt_ahorro = f" {round(ahorro_mes, 2)} EUR"
                pdf.cell(40, 7, txt_ahorro, 1, 1, 'R'); pdf.set_text_color(0)
            except: continue

        pdf.ln(15)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(meses_grafica, ahorros_grafica, color=['#2ecc71' if x >= 0 else '#e74c3c' for x in ahorros_grafica], edgecolor='black', alpha=0.8)
        ax.axhline(0, color='black', linewidth=0.8); plt.xticks(rotation=45); plt.tight_layout()
        grafica_path = "temp_plot.png"; fig.savefig(grafica_path, dpi=300); plt.close(fig); pdf.image(grafica_path, x=45, w=120)

        if pdf.get_y() > 180: pdf.add_page()
        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, f"4. DESGLOSE DE COSTES ESTIMADOS ({nombre_ganadora})", ln=True)

        precios = df_precios_ganadora.set_index('Concepto')['Valor']
        p_potencia_P1 = precios.get('P1 Potencia (€/kW/día)', 0)
        p_potencia_P2 = precios.get('P2 Potencia (€/kW/día)', 0)
        p_energia_punta = precios.get('Energía Punta (€/kWh)', 0)
        p_energia_llano = precios.get('Energía Llano (€/kWh)', 0)
        p_energia_valle = precios.get('Energía Valle (€/kWh)', 0)
        p_excedente = precios.get('Excedente (€/kWh)', 0)

        total_potencia_real = sum(df_consumos['Potencia (kW)'] * df_consumos['Días'] * (p_potencia_P1 + p_potencia_P2))
        total_energia_real = sum(
            (df_consumos['Consumo Punta (kWh)'] * p_energia_punta) +
            (df_consumos['Consumo Llano (kWh)'] * p_energia_llano) +
            (df_consumos['Consumo Valle (kWh)'] * p_energia_valle)
        )
        total_excedente_real = sum(df_consumos.get('Excedente (kWh)', [0])) * p_excedente

        labels, values, colors_pie = ['Potencia', 'Energía'], [total_potencia_real, total_energia_real], ['#A9CCE3', '#ABEBC6']
        if total_excedente_real > 0: labels.append('Excedentes'); values.append(total_excedente_real); colors_pie.append('#FCF3CF')
        
        fig_pie, ax_pie = plt.subplots(figsize=(6, 4)); ax_pie.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors_pie, wedgeprops={'edgecolor': 'white'})
        plt.tight_layout(); pie_path = "temp_pie.png"; fig_pie.savefig(pie_path, dpi=300); plt.close(fig_pie); pdf.image(pie_path, x=55, w=100)

        pdf.set_font('Arial', 'B', 10); pdf.set_text_color(20, 50, 100); pdf.cell(0, 10, "3. COMPARATIVA CON OTRAS OPCIONES DE MERCADO", ln=True)
        pdf.set_x(35); pdf.set_fill_color(20, 50, 100); pdf.set_text_color(255); pdf.cell(80, 7, " Compañía / Tarifa", 1, 0, 'L', True); pdf.cell(60, 7, " Ahorro Total Detectado", 1, 1, 'C', True)
        pdf.set_text_color(0); pdf.set_font('Arial', '', 8)
        for _, row in ranking_ordenado.head(5).iterrows():
            pdf.set_x(35); pdf.cell(80, 7, f" {row.iloc[0]}", 1); pdf.set_text_color(34, 139, 34); pdf.cell(60, 7, f" +{round(row.iloc[1], 2)} EUR", 1, 1, 'C'); pdf.set_text_color(0)

        # ==========================================
        # PÁGINA 3: CONCLUSIÓN FINAL 
        # ==========================================
        pdf.add_page(); pdf.set_fill_color(230, 240, 255); pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, " CONCLUSIÓN Y RECOMENDACIÓN FINAL", ln=True, fill=True, align='C')
        pdf.ln(3); pdf.set_x(20); pdf.set_font('Arial', '', 11); pdf.set_text_color(0)
        pdf.multi_cell(170, 7, "Proyección de ahorro anual para las opciones más competitivas del mercado:", align='C')
        pdf.ln(3)

        pdf.set_x(10); pdf.set_fill_color(245, 245, 245); pdf.set_font('Arial', 'B', 8)
        pdf.cell(60, 7, " Compañía / Tarifa", 1, 0, 'C', True)
        pdf.cell(45, 7, " Ahorro Anual Sin IVA", 1, 0, 'C', True)
        pdf.cell(45, 7, " Ahorro Anual Con IVA", 1, 0, 'C', True)
        pdf.cell(40, 7, " % Ahorro", 1, 1, 'C', True)

        pdf.set_font('Arial', '', 8)
        for _, row in ranking_ordenado.head(5).iterrows():
            nombre_cia = row.iloc[0]; ah_per = row.iloc[1]
            # NUEVA LÓGICA: Cálculo por días reales en el ranking
            an_si = (ah_per / dias_totales_periodo) * 365 if dias_totales_periodo > 0 else 0
            an_ci = an_si * 1.21
            porc = (ah_per / coste_actual_total) * 100 if coste_actual_total > 0 else 0
            pdf.set_x(10); pdf.cell(60, 7, f" {nombre_cia}", 1)
            pdf.cell(45, 7, f" {round(an_si, 2)} EUR", 1, 0, 'C')
            pdf.cell(45, 7, f" {round(an_ci, 2)} EUR", 1, 0, 'C')
            pdf.set_text_color(34, 139, 34); pdf.cell(40, 7, f" {round(porc, 1)}%", 1, 1, 'C'); pdf.set_text_color(0)

        pdf.ln(5) 
        pdf.set_x(20); pdf.set_font('Arial', '', 11); pdf.multi_cell(170, 7, f"La opción más eficiente para su suministro es {nombre_ganadora}:", align='C')
        pdf.set_x(20); pdf.set_font('Arial', 'B', 12); pdf.set_text_color(20, 50, 100); pdf.cell(170, 9, f"{str(nombre_ganadora).upper()}", border='TLR', ln=True, align='C')
        pdf.set_x(20); pdf.set_font('Arial', 'B', 11); pdf.set_text_color(34, 139, 34); pdf.cell(170, 9, f"AHORRO ANUAL ESTIMADO SIN IVA: {round(ahorro_anual_sin_iva, 2)} EUR", border='LR', ln=True, align='C')
        pdf.set_x(20); pdf.set_font('Arial', 'B', 12); pdf.set_text_color(34, 139, 34); pdf.cell(170, 11, f"AHORRO ANUAL ESTIMADO CON IVA (21%): {round(ahorro_anual_con_iva, 2)} EUR / AÑO", border='BLR', ln=True, align='C')
        
        # --- NUEVA LÍNEA: AHORRO A 5 AÑOS ---
        ahorro_5_anos = ahorro_anual_con_iva * 5
        pdf.ln(2); pdf.set_x(20); pdf.set_font('Arial', 'I', 11); pdf.set_text_color(60, 60, 60)
        pdf.cell(170, 8, f"Con este cambio, dejarás de pagar {round(ahorro_5_anos, 2)} EUR extra en los próximos 5 años.", ln=True, align='C')

        # --- GRÁFICA COMPARATIVA ---
        pdf.ln(3)
        fig_vs, ax_vs = plt.subplots(figsize=(6, 3)) 
        # NUEVA LÓGICA: Proyección gasto actual anualizado por días
        g_act_an = (coste_actual_total / dias_totales_periodo) * 365 * 1.21 if dias_totales_periodo > 0 else 0
        g_ah_an = ahorro_anual_con_iva
        g_fin_an = g_act_an - g_ah_an
        ax_vs.bar(['Situación Actual', 'Nuestra Propuesta'], [g_act_an, 0], color='#e74c3c', label='Gasto Actual', width=0.4)
        ax_vs.bar(['Situación Actual', 'Nuestra Propuesta'], [0, g_fin_an], color='#2ecc71', label='Nuevo Coste', width=0.4)
        ax_vs.bar(['Situación Actual', 'Nuestra Propuesta'], [0, g_ah_an], bottom=[0, g_fin_an], color='#f1c40f', label='Tu Ahorro', width=0.4)
        
        ax_vs.set_ylabel('Euros (€) al año', fontsize=9); ax_vs.set_title('PROYECCIÓN DE GASTO ANUAL CON IVA', fontsize=10)
        ax_vs.tick_params(axis='both', which='major', labelsize=8)
        ax_vs.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=3, fontsize=7); plt.tight_layout()
        
        vs_p = "temp_vs.png"; fig_vs.savefig(vs_p, dpi=300); plt.close(fig_vs)
        pdf.image(vs_p, x=40, w=130) 

        # --- SECCIÓN QR ---
        pdf.ln(3) 
        qr = qrcode.QRCode(box_size=6, border=2) 
        url_wa = "https://wa.me/34614676150?text=Hola,%20me%20interesa%20contratar%20la%20tarifa%20ganadora"
        qr.add_data(url_wa)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=(20, 50, 100), back_color="white")
        qr_path = "temp_qr.png"
        qr_img.save(qr_path)
        
        pdf.set_font('Arial', 'B', 9); pdf.set_text_color(20, 50, 100)
        pdf.cell(0, 4, "Escanea para contratación directa vía WhatsApp:", ln=True, align='C')
        pdf.image(qr_path, x=92, w=25) 

        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"Error técnico: {e}"); return None

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador Pro | Energetika")
c1, c2 = st.columns(2)
with c1: nombre_cliente = st.text_input("Nombre completo cliente:", "Nombre Cliente"); direccion_cliente = st.text_input("Dirección:", "Calle Ejemplo 123")
with c2: compania_actual_manual = st.text_input("Compañía actual:", "Energía XXI")
archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if archivo:
    try:
        df_det = pd.read_excel(archivo, sheet_name="Detalle Comparativa")
        df_ran = pd.read_excel(archivo, sheet_name="Ranking Ahorro")
        df_con = pd.read_excel(archivo, sheet_name="Datos Facturas Originales")
        df_pre = pd.read_excel(archivo, sheet_name=3)

        st.success("✅ Excel cargado.")
        if st.button("🚀 Generar PDF"):
            pdf_bytes = generar_pdf(df_det, df_ran, df_con, df_pre, nombre_cliente, direccion_cliente, compania_actual_manual)
            if pdf_bytes:
                st.download_button(label="📥 Descargar Informe", data=pdf_bytes, file_name=f"Auditoria_{nombre_cliente.replace(' ', '_')}.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
