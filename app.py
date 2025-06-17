# --- VERSIÓN FINAL v7.0 (Generador de PDF Robusto) ---
# Se reescribe por completo la generación del PDF para usar un solo bloque
# de texto pre-formateado, solucionando todos los problemas de layout.

import streamlit as st
from datetime import datetime
from fpdf import FPDF
import fitz  # PyMuPDF

# ====================================================================
# CLASE PDF PERSONALIZADA
# ====================================================================
class PDF_con_Sello_de_Agua(FPDF):
    def header(self):
        # El sello de agua de fondo
        self.set_font('Courier', 'B', 40)
        self.set_text_color(220, 220, 220)
        self.rotate(45, x=self.w / 2 - 60, y=self.h / 2 + 10)
        self.text(x=self.w / 2 - 60, y=self.h / 2 + 10, txt="Sebastian Careaga Quiroga")
        self.rotate(0)
        self.set_text_color(0, 0, 0)

    def footer(self):
        # El pie de página
        self.set_y(-15)
        self.set_font('Courier', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Informe generado por Sebastian Careaga Quiroga', 0, 0, 'L')
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'R')

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

    # --- Generación del contenido del PDF como una lista de strings ---
    report_lines = []
    separator = "*" * 70
    
    report_lines.append(separator)
    report_lines.append("INFORME TECNICO DE CALCULO DE HONORARIOS".center(70))
    report_lines.append(separator)
    report_lines.append("")
    report_lines.append(f"FECHA DE EMISION: {datetime.now().strftime('%d/%m/%Y')}")
    report_lines.append(f"MONTO DEL PROCESO: {amount_in_uma:.2f} UMA")
    report_lines.append("NORMATIVA APLICABLE: Ley N° 27.423")
    report_lines.append("-" * 70)
    
    report_lines.append("1. FUNDAMENTO NORMATIVO")
    report_lines.append("-" * 70)
    report_lines.append("El calculo se efectua segun Art. 21 (metodo 'in fine') y")
    report_lines.append("Art. 58 de la Ley N° 27.423 de Honorarios Profesionales.")
    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("2. METODOLOGIA APLICADA")
    report_lines.append("-" * 70)
    report_lines.append("- Honorario Maximo: Aplicacion escalonada de la alicuota")
    report_lines.append("  MAXIMA de cada tramo del Art. 21.")
    report_lines.append("- Honorario Minimo: Aplicacion de la alicuota MAXIMA para")
    report_lines.append("  tramos completos y la alicuota MINIMA sobre el excedente.")
    report_lines.append("")

    report_lines.append("-" * 70)
    report_lines.append("3. DESARROLLO DEL CALCULO")
    report_lines.append("-" * 70)
    report_lines.append("\nA. CALCULO DEL LIMITE SUPERIOR (HONORARIO MAXIMO)")
    
    temp_previous_upper_limit = 0
    for i, (upper_limit, _, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= temp_previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - temp_previous_upper_limit
        calc_str = f"{amount_in_tranche:>9.2f} UMA x {max_perc:6.2%}"
        result_str = f"{(amount_in_tranche * max_perc):>8.2f} UMA"
        report_lines.append(f"  - Tramo {i+1}: {calc_str:<25} = {result_str}")
        temp_previous_upper_limit = upper_limit
    report_lines.append("  " + "-" * 50)
    report_lines.append(f"  >> TOTAL LIMITE SUPERIOR:".ljust(43) + f"{honorary_max:>12.2f} UMA")

    report_lines.append("\nB. CALCULO DEL LIMITE INFERIOR (HONORARIO MINIMO)")
    temp_previous_upper_limit = 0
    for i, (upper_limit, min_perc, max_perc) in enumerate(FRANJAS):
        if amount_in_uma <= temp_previous_upper_limit: break
        amount_in_tranche = min(amount_in_uma, upper_limit) - temp_previous_upper_limit
        perc_to_use = max_perc if amount_in_uma > upper_limit else min_perc
        calc_str = f"{amount_in_tranche:>9.2f} UMA x {perc_to_use:6.2%}"
        result_str = f"{(amount_in_tranche * perc_to_use):>8.2f} UMA"
        report_lines.append(f"  - Tramo {i+1}: {calc_str:<25} = {result_str}")
        temp_previous_upper_limit = upper_limit
    report_lines.append("  " + "-" * 50)
    report_lines.append(f"  >> TOTAL LIMITE INFERIOR:".ljust(43) + f"{honorary_min_hybrid:>12.2f} UMA")
    
    report_lines.append("")
    report_lines.append("-" * 70)
    report_lines.append("4. CONCLUSION: RANGO DE HONORARIOS SUGERIDO")
    report_lines.append("-" * 70)
    report_lines.append(f"Considerando el piso legal de {MIN_HONORARY_PROCESO_CONOCIMIENTO:.2f} UMA (Art. 58),")
    report_lines.append(f"el rango sugerido es:")
    report_lines.append("")
    report_lines.append(f"    HONORARIO MINIMO:  {final_min_honorary:.2f} UMA")
    report_lines.append(f"    HONORARIO MAXIMO:  {honorary_max:.2f} UMA")
    report_lines.append(separator)

    # --- Creación del PDF a partir del texto ---
    pdf = PDF_con_Sello_de_Agua('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Courier', '', 10) # Usamos una sola fuente para todo
    
    # Unimos todas las líneas en un solo bloque de texto
    full_report_text = "\n".join(report_lines)
    
    pdf.multi_cell(0, 5, full_report_text)
    
    return pdf.output()

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
            pdf_data_bytearray = create_pdf_report(amount_uma_input)
            pdf_data_bytes = bytes(pdf_data_bytearray)
        
        st.success("¡Su informe está listo! A continuación una vista previa:")

        try:
            with fitz.open(stream=pdf_data_bytes, filetype="pdf") as doc:
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                
                st.image(img_bytes, caption="Vista Previa de la Primera Página del Informe")
        except Exception as e:
            st.error(f"Ocurrió un error al generar la vista previa: {e}")

        st.download_button(
            label="📥 Descargar Informe Completo en PDF",
            data=pdf_data_bytes,
            file_name=f"Informe_Honorarios_{amount_uma_input:.2f}_UMA.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Por favor, ingrese un monto en UMA para poder calcular.")

st.divider()
st.caption("Creado por Sebastián Careaga Quiroga. Herramienta de referencia.")