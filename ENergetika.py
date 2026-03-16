
import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# Configuración de la página de Streamlit
st.set_page_config(page_title="Generador de PDF - Energetika", page_icon="⚡")

class PDF(FPDF):
    def header(self):
        # Insertar Logo en la parte superior derecha
        # logo, x, y, ancho (w)
        try:
            self.image('Logo_Energetika.jpg', x=160, y=10, w=40)
        except:
            pass # Si no encuentra la imagen, continúa sin ella
        
        self.set_font('Arial', 'B', 15)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_pdf(user_text, client_name):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título del documento
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Informe de Asesoramiento Energético", ln=True, align='L')
    pdf.ln(10)
    
    # Datos del cliente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Cliente: {client_name}", ln=True)
    pdf.ln(5)
    
    # Cuerpo del texto
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=user_text)
    
    return pdf.output(dest='S').encode('latin-1')

# Interfaz de Usuario en Streamlit
st.title("📄 Generador de Informes Energetika")
st.markdown("Introduce los datos para generar el PDF con el membrete oficial.")

with st.form("pdf_form"):
    cliente = st.text_input("Nombre del Cliente")
    contenido = st.text_area("Contenido del Informe", height=200)
    submit_button = st.form_submit_button("Generar PDF")

if submit_button:
    if cliente and contenido:
        pdf_bytes = generate_pdf(contenido, cliente)
        
        st.success("✅ PDF generado con éxito")
        
        # Botón de descarga
        st.download_button(
            label="⬇️ Descargar Informe PDF",
            data=pdf_bytes,
            file_name=f"Informe_{cliente.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Por favor, rellena todos los campos.")
