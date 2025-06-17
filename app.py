# --- VERSIÓN FINAL PREMIUM v4.0 (CORREGIDA Y ESTABLE) ---
# Corrige el error FPDFException al especificar anchos fijos en el PDF.
# Esta es la versión definitiva para la demostración.

import streamlit as st
from datetime import datetime
from fpdf import FPDF
import fitz  # PyMuPDF

# ====================================================================
# CLASE PDF PERSONALIZADA
# ====================================================================
class PDF_con_Sello_de_Agua(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 50)
        self.set_text_color(220, 220, 220)
        self.rotate(45, x=self.w / 2 - 60, y=self.h / 2 + 10)
        self.text(x=self.w / 2 - 60, y=self.h / 2 + 10, txt="Sebastián Careaga Quiroga")
        self.rotate(0)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Informe generado por Sebastián Careaga Quiroga', 0, 0, 'L')
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

# ====================================================================
# LÓGICA DE CÁLCULO Y GENERACIÓN DE PDF
# ====================================================================
FRANJAS = [(15, 0.22, 0.33), (45, 0.20, 0.26), (90, 0.18, 0.24), (150, 0.16, 0.22), (450, 0.14, 0.20), (750, 0.12, 0.17), (float('inf'), 0.10, 0.15)]
MIN_HONORARY_PROCESO_CONOCIMIENTO = 10.0

def create_pdf_report(amount_in_uma):
    # Pre-cálculo de los valores
    honorary_max = 0.0
    honorary_min_hybrid = 0.0
    previous_upper_limit = 0.0
    for i, (upper_limit, min_perc, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - previous_upper_limit
        honorary_max += amount_in_tranche * max_perc
        if amount_in_uma > upper_limit:
            honorary_min_hybrid += amount_in_tranche * max_perc
        else:
            honorary_min_hybrid += amount_in_tranche * min_perc
        previous_upper_limit = upper_limit
    final_min_honorary = max(honorary_min_hybrid, MIN_HONORARY_PROCESO_CONOCIMIENTO)

    # --- Generación del PDF ---
    pdf = PDF_con_Sello_de_Agua('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Ancho disponible para el contenido (A4: 210mm - 10mm margen izq - 10mm margen der)
    effective_width = pdf.w - 2 * pdf.l_margin 

    pdf.set_font('Helvetica', 'B', 16)
    pdf.multi_cell(effective_width, 10, 'INFORME TÉCNICO DE CÁLCULO DE HONORARIOS', 0, 'C')
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(effective_width, 6, f"FECHA DE EMISIÓN: {datetime.now().strftime('%d/%m/%Y')}", 0, 'L')
    pdf.multi_cell(effective_width, 6, f"MONTO DEL PROCESO: {amount_in_uma:.2f} UMA", 0, 'L')
    pdf.multi_cell(effective_width, 6, "NORMATIVA APLICABLE: Ley N° 27.423", 0, 'L')
    pdf.ln(3); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(3)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.multi_cell(effective_width, 8, "1. FUNDAMENTO NORMATIVO", 0, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(effective_width, 5, "El presente cálculo se efectúa en estricta conformidad con las disposiciones de la Ley N° 27.423 de Honorarios Profesionales, con especial observancia de:\n\n- Art. 21: Establecimiento de la UMA y la escala porcentual progresiva (\"in fine\").\n- Art. 58 inc. a): Establecimiento del honorario mínimo para procesos de conocimiento (10 UMA).")
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.multi_cell(effective_width, 8, "2. METODOLOGÍA APLICADA", 0, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(effective_width, 5, "Se determinan los límites del rango honorario mediante los siguientes métodos de cálculo progresivo:\n\n- Honorario Máximo: Aplicación escalonada de la alícuota MÁXIMA de cada tramo del Art. 21.\n- Honorario Mínimo: Aplicación de la alícuota MÁXIMA para tramos completos y la alícuota MÍNIMA sobre el excedente.")
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.multi_cell(effective_width, 8, "3. DESARROLLO DEL CÁLCULO", 0, 'L')
    pdf.ln(2)

    pdf.set_font('Courier', 'B', 10)
    pdf.multi_cell(effective_width, 5, "A. CÁLCULO DEL LÍMITE SUPERIOR (HONORARIO MÁXIMO)")
    pdf.set_font('Courier', '', 9)
    temp_previous_upper_limit = 0
    for i, (upper_limit, _, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= temp_previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - temp_previous_upper_limit
        line = f"  - Tramo {i+1}: {amount_in_tranche:8.2f} UMA x {max_perc:6.2%} = {(amount_in_tranche * max_perc):8.2f} UMA"
        pdf.multi_cell(effective_width, 5, line, 0, 'L')
        temp_previous_upper_limit = upper_limit
    pdf.set_font('Courier', 'B', 10)
    pdf.multi_cell(effective_width, 5, "  -----------------------------------------------------------")
    pdf.multi_cell(effective_width, 5, f"  >> TOTAL LÍMITE SUPERIOR: {honorary_max:26.2f} UMA")
    pdf.ln(5)

    pdf.set_font('Courier', 'B', 10)
    pdf.multi_cell(effective_width, 5, "B. CÁLCULO DEL LÍMITE INFERIOR (HONORARIO MÍNIMO)")
    pdf.set_font('Courier', '', 9)
    temp_previous_upper_limit = 0
    for i, (upper_limit, min_perc, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= temp_previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - temp_previous_upper_limit
        perc_to_use = max_perc if amount_in_uma > upper_limit else min_perc
        line = f"  - Tramo {i+1}: {amount_in_tranche:8.2f} UMA x {perc_to_use:6.2%} = {(amount_in_tranche * perc_to_use):8.2f} UMA"
        pdf.multi_cell(effective_width, 5, line, 0, 'L')
        temp_previous_upper_limit = upper_limit
    pdf.set_font('Courier', 'B', 10)
    pdf.multi_cell(effective_width, 5, "  -----------------------------------------------------------")
    pdf.multi_cell(effective_width, 5, f"  >> TOTAL LÍMITE INFERIOR: {honorary_min_hybrid:26.2f} UMA")
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.multi_cell(effective_width, 8, "4. CONCLUSIÓN: RANGO DE HONORARIOS SUGERIDO", 0, 'L')
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(effective_width, 5, f"Por lo expuesto, y considerando el mínimo legal de {MIN_HONORARY_PROCESO_CONOCIMIENTO:.2f} UMA (Art. 58), se determina que el rango de honorarios para un proceso de {amount_in_uma:.2f} UMA es:")
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.multi_cell(effective_width, 6, f"   HONORARIO MÍNIMO:  {final_min_honorary:.2f} UMA", 0, 'C')
    pdf.multi_cell(effective_width, 6, f"   HONORARIO MÁXIMO:  {honorary_max:.2f} UMA", 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# ====================================================================
# INTERFAZ DE LA APLICACIÓN WEB CON STREAMLIT
# ====================================================================
st.set_page_config(page_title="Calculadora de Honorarios | By Sebastián Careaga", page_icon="⚖️", layout="centered")

st.title("Calculadora Profesional de Honorarios")
st.markdown("Ley 27.423 - Una herramienta por y para abogados.")
st.divider()

amount_uma_input = st.number_input(
    label="Ingrese el Monto del Proceso en UMA:",
    min_value=0.0, value=None, step=10.0, format="%.2f", placeholder="Ej: 707.12"
)

calculate_button = st.button("Generar Informe PDF", type="primary", use_container_width=True)

if calculate_button:
    if amount_uma_input is not None and amount_uma_input > 0:
        with st.spinner('Generando su informe PDF, por favor espere...'):
            pdf_data = create_pdf_report(amount_uma_input)
        
        st.success("¡Su informe está listo! A continuación una vista previa:")

        try:
            with fitz.open(stream=pdf_data, filetype="pdf") as doc:
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                
                st.image(img_bytes, caption="Vista Previa de la Primera Página del Informe")
        except Exception as e:
            st.error(f"Ocurrió un error al generar la vista previa: {e}")

        st.download_button(
            label="📥 Descargar Informe Completo en PDF",
            data=pdf_data,
            file_name=f"Informe_Honorarios_{amount_uma_input:.2f}_UMA.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Por favor, ingrese un monto en UMA para poder calcular.")

st.divider()
st.caption("Creado por Sebastián Careaga Quiroga. Herramienta de referencia.")