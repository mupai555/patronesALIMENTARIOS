import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re

# ==================== FUNCIONES DE VALIDACIÓN PROGRESIVA ====================

def validate_step_1():
    """Valida que se haya seleccionado al menos una opción en proteínas grasas"""
    selections = (
        st.session_state.get('huevos_embutidos', []) + 
        st.session_state.get('carnes_res_grasas', []) + 
        st.session_state.get('carnes_cerdo_grasas', []) + 
        st.session_state.get('carnes_pollo_grasas', []) + 
        st.session_state.get('organos_grasos', []) + 
        st.session_state.get('quesos_grasos', []) + 
        st.session_state.get('lacteos_enteros', []) + 
        st.session_state.get('pescados_grasos', []) + 
        st.session_state.get('mariscos_grasos', [])
    )
    return len(selections) > 0

def validate_step_2():
    """Valida que se haya seleccionado al menos una opción en proteínas magras"""
    selections = (
        st.session_state.get('carnes_res_magras', []) + 
        st.session_state.get('carnes_cerdo_magras', []) + 
        st.session_state.get('carnes_pollo_magras', []) + 
        st.session_state.get('organos_magros', []) + 
        st.session_state.get('pescados_magros', []) + 
        st.session_state.get('mariscos_magros', []) + 
        st.session_state.get('quesos_magros', []) + 
        st.session_state.get('lacteos_light', []) + 
        st.session_state.get('huevos_embutidos_light', [])
    )
    return len(selections) > 0

def validate_step_3():
    """Valida que se haya seleccionado al menos una opción en grasas saludables"""
    selections = (
        st.session_state.get('grasas_naturales', []) + 
        st.session_state.get('frutos_secos_semillas', []) + 
        st.session_state.get('mantequillas_vegetales', [])
    )
    return len(selections) > 0

def validate_step_4():
    """Valida que se haya seleccionado al menos una opción en carbohidratos"""
    selections = (
        st.session_state.get('cereales_integrales', []) + 
        st.session_state.get('pastas', []) + 
        st.session_state.get('tortillas_panes', []) + 
        st.session_state.get('raices_tuberculos', []) + 
        st.session_state.get('leguminosas', [])
    )
    return len(selections) > 0

def validate_step_5():
    """Valida que se haya seleccionado al menos una opción en vegetales"""
    return len(st.session_state.get('vegetales_lista', [])) > 0

def validate_step_6():
    """Valida que se haya seleccionado al menos una opción en frutas"""
    return len(st.session_state.get('frutas_lista', [])) > 0

def validate_step_7():
    """Valida aceites de cocción - opcional"""
    return True  # Este paso es opcional

def validate_step_8():
    """Valida bebidas - opcional"""
    return True  # Este paso es opcional

def validate_step_9():
    """Valida que se haya seleccionado al menos una opción en alergias/intolerancias"""
    alergias_selections = st.session_state.get('alergias_alimentarias', [])
    intolerancias_selections = st.session_state.get('intolerancias_digestivas', [])
    
    # Al menos una selección en alguno de los dos grupos (puede ser "Ninguna")
    return len(alergias_selections) > 0 or len(intolerancias_selections) > 0

def validate_step_10():
    """Valida que se haya seleccionado al menos una opción en antojos"""
    selections = (
        st.session_state.get('antojos_dulces', []) +
        st.session_state.get('antojos_salados', []) +
        st.session_state.get('antojos_comida_rapida', []) +
        st.session_state.get('antojos_bebidas', []) +
        st.session_state.get('antojos_picantes', [])
    )
    return len(selections) > 0

def validate_step_11():
    """Valida frecuencia de comidas - opcional"""
    return True  # Este paso es opcional

def validate_step_12():
    """Valida sugerencias de menús - opcional"""
    return True  # Este paso es opcional

def get_step_validator(step_number):
    """Obtiene la función de validación para un paso específico"""
    validators = {
        1: validate_step_1,
        2: validate_step_2, 
        3: validate_step_3,
        4: validate_step_4,
        5: validate_step_5,
        6: validate_step_6,
        7: validate_step_7,
        8: validate_step_8,
        9: validate_step_9,
        10: validate_step_10,
        11: validate_step_11,
        12: validate_step_12
    }
    return validators.get(step_number, lambda: True)

def advance_to_next_step():
    """Avanza al siguiente paso si la validación es exitosa"""
    current_step = st.session_state.get('current_step', 1)
    validator = get_step_validator(current_step)
    
    if validator():
        # Marcar el paso actual como completado
        st.session_state.step_completed[current_step] = True
        # Avanzar al siguiente paso
        if current_step < 12:
            st.session_state.current_step = current_step + 1
            st.session_state.max_unlocked_step = max(st.session_state.max_unlocked_step, current_step + 1)
        return True
    else:
        # Mostrar mensaje de error profesional
        st.error("Para continuar, por favor selecciona al menos una opción en este grupo. Esto permitirá generar una evaluación nutricional personalizada y precisa.")
        return False

def go_to_previous_step():
    """Retrocede al paso anterior"""
    current_step = st.session_state.get('current_step', 1)
    if current_step > 1:
        st.session_state.current_step = current_step - 1

# ==================== FUNCIONES DE VALIDACIÓN ESTRICTA ====================
def validate_name(name):
    """
    Valida que el nombre tenga al menos dos palabras.
    Retorna (es_válido, mensaje_error)
    """
    if not name or not name.strip():
        return False, "El nombre es obligatorio"
    
    # Limpiar espacios extra y dividir en palabras
    words = name.strip().split()
    
    if len(words) < 2:
        return False, "El nombre debe contener al menos dos palabras (nombre y apellido)"
    
    # Verificar que cada palabra tenga al menos 2 caracteres y solo contenga letras y espacios
    for word in words:
        if len(word) < 2:
            return False, "Cada palabra del nombre debe tener al menos 2 caracteres"
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+$', word):
            return False, "El nombre solo puede contener letras y espacios"
    
    return True, ""

def validate_phone(phone):
    """
    Valida que el teléfono tenga exactamente 10 dígitos.
    Retorna (es_válido, mensaje_error)
    """
    if not phone or not phone.strip():
        return False, "El teléfono es obligatorio"
    
    # Limpiar espacios y caracteres especiales
    clean_phone = re.sub(r'[^0-9]', '', phone.strip())
    
    if len(clean_phone) != 10:
        return False, "El teléfono debe tener exactamente 10 dígitos"
    
    # Verificar que todos sean dígitos
    if not clean_phone.isdigit():
        return False, "El teléfono solo puede contener números"
    
    return True, ""

def validate_email(email):
    """
    Valida que el email tenga formato estándar.
    Retorna (es_válido, mensaje_error)
    """
    if not email or not email.strip():
        return False, "El email es obligatorio"
    
    # Patrón regex para email estándar
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email.strip()):
        return False, "El email debe tener un formato válido (ejemplo: usuario@dominio.com)"
    
    return True, ""

# ==================== CONFIGURACIÓN DE PÁGINA Y CSS MEJORADO ====================
st.set_page_config(
    page_title="MUPAI - Evaluación de Patrones Alimentarios",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
:root {
    --mupai-yellow: #F4C430;
    --mupai-dark-yellow: #DAA520;
    --mupai-black: #181A1B;
    --mupai-gray: #232425;
    --mupai-light-gray: #EDEDED;
    --mupai-white: #FFFFFF;
    --mupai-success: #27AE60;
    --mupai-warning: #F39C12;
    --mupai-danger: #E74C3C;
}
/* Fondo general */
.stApp {
    background: linear-gradient(135deg, #1E1E1E 0%, #232425 100%);
}
.main-header {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    color: #181A1B;
    padding: 2rem 1rem;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(244, 196, 48, 0.20);
    animation: fadeIn 0.5s ease-out;
}
.content-card {
    background: #1E1E1E;
    padding: 2rem 1.3rem;
    border-radius: 16px;
    box-shadow: 0 5px 22px 0px rgba(244,196,48,0.07), 0 1.5px 8px rgba(0,0,0,0.11);
    margin-bottom: 1.7rem;
    border-left: 5px solid var(--mupai-yellow);
    animation: slideIn 0.5s;
}
.card-psmf {
    border-left-color: var(--mupai-warning)!important;
}
.card-success {
    border-left-color: var(--mupai-success)!important;
}
.content-card, .content-card * {
    color: #FFF !important;
    font-weight: 500;
    letter-spacing: 0.02em;
}
.stButton > button {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    color: #232425;
    border: none;
    padding: 0.85rem 2.3rem;
    font-weight: bold;
    border-radius: 28px;
    transition: all 0.3s;
    box-shadow: 0 4px 16px rgba(244, 196, 48, 0.18);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 1.15rem;
}
.stButton > button:hover {
    filter: brightness(1.04);
    box-shadow: 0 7px 22px rgba(244, 196, 48, 0.24);
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    border: 2px solid var(--mupai-yellow)!important;
    border-radius: 11px!important;
    padding: 0.7rem 0.9rem!important;
    background: #232425!important;
    color: #fff!important;
    font-size: 1.13rem!important;
    font-weight: 600!important;
}
/* Special styling for selectboxes */
.stSelectbox[data-testid="stSelectbox"] > div > div > select {
    background: #F8F9FA!important;
    color: #1E1E1E!important;
    border: 2px solid #DAA520!important;
    font-weight: bold!important;
}
.stSelectbox[data-testid="stSelectbox"] option {
    background: #FFFFFF!important;
    color: #1E1E1E!important;
    font-weight: bold!important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stRadio label, .stCheckbox label, .stDateInput label, .stMarkdown,
.stExpander .streamlit-expanderHeader, .stExpander label, .stExpander p, .stExpander div {
    color: #FFD600 !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    font-size: 1.04rem !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
}
/* Enhanced styling for multiselect labels and info messages */
.stMultiSelect label, 
div[data-testid="stAlert"] p,
div[data-testid="stInfo"] p {
    color: #FFD600 !important;
    font-weight: 700 !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
}
.stTextInput input::placeholder,
.stNumberInput input::placeholder {
    color: #e0e0e0 !important;
    opacity: 1 !important;
}
.stAlert > div {
    border-radius: 11px;
    padding: 1.1rem;
    border-left: 5px solid;
    background: #222326 !important;
    color: #FFF !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(125deg, #252525 0%, #303030 100%);
    padding: 1.1rem 1rem;
    border-radius: 12px;
    border-left: 4px solid var(--mupai-yellow);
    box-shadow: 0 2.5px 11px rgba(0,0,0,0.11);
    color: #fff !important;
}
.streamlit-expanderHeader {
    background: linear-gradient(135deg, var(--mupai-gray) 70%, #242424 100%);
    border-radius: 12px;
    font-weight: bold;
    color: #FFF !important;
    border: 2px solid var(--mupai-yellow);
    font-size: 1.16rem;
}
.stRadio > div {
    background: #181A1B !important;
    padding: 1.1rem 0.5rem;
    border-radius: 10px;
    border: 2px solid transparent;
    transition: all 0.3s;
    color: #FFF !important;
}
.stRadio > div:hover {
    border-color: var(--mupai-yellow);
}
.stCheckbox > label, .stCheckbox > span {
    color: #FFF !important;
    opacity: 1 !important;
    font-size: 1.05rem;
}
.stProgress > div > div > div {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%)!important;
    border-radius: 10px;
    animation: pulse 1.2s infinite;
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.92; }
    100% { opacity: 1; }
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px);} to { opacity: 1; transform: translateY(0);} }
@keyframes slideIn { from { opacity: 0; transform: translateX(-18px);} to { opacity: 1; transform: translateX(0);} }
.badge {
    display: inline-block;
    padding: 0.32rem 0.98rem;
    border-radius: 18px;
    font-size: 0.97rem;
    font-weight: 800;
    margin: 0.27rem;
    color: #FFF;
    background: #313131;
    border: 1px solid #555;
}
.badge-success { background: var(--mupai-success); }
.badge-warning { background: var(--mupai-warning); color: #222; border: 1px solid #b78a09;}
.badge-danger { background: var(--mupai-danger); }
.badge-info { background: var(--mupai-yellow); color: #1E1E1E;}
.dataframe {
    border-radius: 10px !important;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    background: #2A2A2A!important;
    color: #FFF!important;
}
hr {
    border: none;
    height: 2.5px;
    background: linear-gradient(to right, transparent, var(--mupai-yellow), transparent);
    margin: 2.1rem 0;
}
@media (max-width: 768px) {
    .main-header { padding: 1.2rem;}
    .content-card { padding: 1.1rem;}
    .stButton > button { padding: 0.5rem 1.1rem; font-size: 0.96rem;}
}
.content-card:hover {
    transform: translateY(-1.5px);
    box-shadow: 0 8px 27px rgba(0,0,0,0.17);
    transition: all 0.25s;
}
.gradient-text {
    background: linear-gradient(135deg, var(--mupai-yellow) 0%, var(--mupai-dark-yellow) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    font-size: 1.11rem;
}
.footer-mupai {
    text-align: center;
    padding: 2.2rem 0.3rem 2.2rem 0.3rem;
    background: linear-gradient(135deg, #202021 0%, #232425 100%);
    border-radius: 15px;
    color: #FFF;
    margin-top: 2.2rem;
}
.footer-mupai h4 { color: var(--mupai-yellow); margin-bottom: 1.1rem;}
.footer-mupai a {
    color: var(--mupai-yellow);
    text-decoration: none;
    margin: 0 1.2rem;
    font-weight: 600;
    font-size: 1.01rem;
}
</style>
""", unsafe_allow_html=True)

# Header principal visual con logos
import base64

# Cargar y codificar los logos desde la raíz del repo
try:
    with open('LOGO MUPAI.png', 'rb') as f:
        logo_mupai_b64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    logo_mupai_b64 = ""

try:
    with open('LOGO MUP.png', 'rb') as f:
        logo_gym_b64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    logo_gym_b64 = ""

st.markdown(f"""
<style>
.header-container {{
    background: #000000;
    padding: 2rem 1rem;
    border-radius: 18px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.5s ease-out;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
}}

.logo-left, .logo-right {{
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    max-width: 150px;
}}

.logo-left img, .logo-right img {{
    max-height: 80px;
    max-width: 100%;
    height: auto;
    width: auto;
    object-fit: contain;
}}

.header-center {{
    flex: 1;
    text-align: center;
    padding: 0 2rem;
}}

.header-title {{
    color: #FFB300;
    font-size: 2.2rem;
    font-weight: 900;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    line-height: 1.2;
}}

.header-subtitle {{
    color: #FFFFFF;
    font-size: 1rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
}}

@media (max-width: 768px) {{
    .header-container {{
        flex-direction: column;
        text-align: center;
    }}
    
    .logo-left, .logo-right {{
        margin-bottom: 1rem;
    }}
    
    .header-center {{
        padding: 0;
    }}
    
    .header-title {{
        font-size: 1.8rem;
    }}
}}
</style>

<div class="header-container">
    <div class="logo-left">
        <img src="data:image/png;base64,{logo_mupai_b64}" alt="LOGO MUPAI" />
    </div>
    <div class="header-center">
        <h1 class="header-title">TEST MUPAI: PATRONES ALIMENTARIOS</h1>
        <p class="header-subtitle">Tu evaluación personalizada de hábitos y preferencias alimentarias basada en ciencia</p>
    </div>
    <div class="logo-right">
        <img src="data:image/png;base64,{logo_gym_b64}" alt="LOGO MUSCLE UP GYM" />
    </div>
</div>
""", unsafe_allow_html=True)

# --- Inicialización de estado de sesión robusta (solo una vez)
defaults = {
    "datos_completos": False,
    "correo_enviado": False,
    "preferencias_alimentarias": {},
    "restricciones_dieteticas": {},
    "nombre": "",
    "telefono": "",
    "email_cliente": "",
    "edad": "",
    "sexo": "Hombre",
    "fecha_llenado": datetime.now().strftime("%Y-%m-%d"),
    "acepto_terminos": False,
    "authenticated": False,  # Nueva variable para controlar el login
    # Variables para el flujo progresivo
    "current_step": 1,
    "step_completed": {
        1: False,  # Proteínas grasas
        2: False,  # Proteínas magras
        3: False,  # Grasas saludables
        4: False,  # Carbohidratos
        5: False,  # Vegetales
        6: False,  # Frutas
        7: False,  # Aceites de cocción
        8: False,  # Bebidas
        9: False,  # Alergias/intolerancias
        10: False,  # Antojos
        11: False,  # Frecuencia de comidas
        12: False   # Sugerencias de menús
    },
    "max_unlocked_step": 1
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================== SISTEMA DE AUTENTICACIÓN ====================
ADMIN_PASSWORD = "MUPAI2025"  # Contraseña predefinida

# Si no está autenticado, mostrar login
if not st.session_state.authenticated:
    st.markdown("""
    <div class="content-card" style="max-width: 500px; margin: 2rem auto; text-align: center;">
        <h2 style="color: var(--mupai-yellow); margin-bottom: 1.5rem;">
            🔐 Acceso Exclusivo
        </h2>
        <p style="margin-bottom: 2rem; color: #CCCCCC;">
            Ingresa la contraseña para acceder al sistema de evaluación de patrones alimentarios MUPAI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Container centrado para el formulario de login
    login_container = st.container()
    with login_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password_input = st.text_input(
                "Contraseña", 
                type="password", 
                placeholder="Ingresa la contraseña de acceso",
                key="password_input"
            )
            
            if st.button("🚀 Acceder al Sistema", use_container_width=True):
                if password_input == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("✅ Acceso autorizado. Bienvenido al sistema MUPAI de patrones alimentarios.")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Acceso denegado.")
    
    # Mostrar información mientras no esté autenticado
    st.markdown("""
    <div class="content-card" style="margin-top: 3rem; text-align: center; background: #1A1A1A;">
        <h3 style="color: var(--mupai-yellow);">Sistema de Evaluación de Patrones Alimentarios</h3>
        <p style="color: #CCCCCC;">
            MUPAI utiliza metodologías científicas avanzadas para evaluar patrones alimentarios 
            personalizados, preferencias dietéticas y crear planes nutricionales adaptativos.
        </p>
        <p style="color: #999999; font-size: 0.9rem; margin-top: 1.5rem;">
            © 2025 MUPAI - Muscle up GYM 
            Digital Nutrition Science
            Alimentary Pattern Assessment Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()  # Detener la ejecución hasta que se autentique

# Tarjetas visuales robustas
def crear_tarjeta(titulo, contenido, tipo="info"):
    colores = {
        "info": "var(--mupai-yellow)",
        "success": "var(--mupai-success)",
        "warning": "var(--mupai-warning)",
        "danger": "var(--mupai-danger)"
    }
    color = colores.get(tipo, "var(--mupai-yellow)")
    return f"""
    <div class="content-card" style="border-left-color: {color};">
        <h3 style="margin-bottom: 1rem;">{titulo}</h3>
        <div>{contenido}</div>
    </div>
    """

def enviar_email_resumen(contenido, nombre_cliente, email_cliente, fecha, edad, telefono):
    """Envía el email con el resumen completo de la evaluación de patrones alimentarios."""
    try:
        email_origen = "administracion@muscleupgym.fitness"
        email_destino = "administracion@muscleupgym.fitness"
        password = st.secrets.get("zoho_password", "TU_PASSWORD_AQUI")

        msg = MIMEMultipart()
        msg['From'] = email_origen
        msg['To'] = email_destino
        msg['Subject'] = f"Evaluación patrones alimentarios MUPAI - {nombre_cliente} ({fecha})"

        msg.attach(MIMEText(contenido, 'plain'))

        server = smtplib.SMTP('smtp.zoho.com', 587)
        server.starttls()
        server.login(email_origen, password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Error al enviar email: {str(e)}")
        return False

# ==================== VISUALES INICIALES ====================

# Misión, Visión y Compromiso con diseño mejorado
with st.expander("🎯 **Misión, Visión y Compromiso MUPAI**", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(crear_tarjeta(
            "🎯 Misión",
            "Hacer accesible la evaluación nutricional basada en ciencia, ofreciendo análisis de patrones alimentarios personalizados que se adaptan a todos los estilos de vida.",
            "info"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta(
            "👁️ Visión",
            "Ser el referente global en evaluación de patrones alimentarios digitales, uniendo investigación nutricional con experiencia práctica personalizada.",
            "success"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(crear_tarjeta(
            "🤝 Compromiso",
            "Nos guiamos por la ética, transparencia y precisión científica para ofrecer recomendaciones nutricionales reales, medibles y sostenibles.",
            "warning"
        ), unsafe_allow_html=True)

# BLOQUE 0: Datos personales con diseño mejorado
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown("### 👤 Información Personal")
st.markdown("Por favor, completa todos los campos para comenzar tu evaluación de patrones alimentarios personalizada.")

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre completo*", value=st.session_state.get('nombre', ''), placeholder="Ej: Juan Pérez García", help="Tu nombre legal completo")
    telefono = st.text_input("Teléfono*", value=st.session_state.get('telefono', ''), placeholder="Ej: 8661234567", help="10 dígitos sin espacios")
    email_cliente = st.text_input("Email*", value=st.session_state.get('email_cliente', ''), placeholder="correo@ejemplo.com", help="Email válido para recibir resultados")

with col2:
    # Fix edad type issue by ensuring it's an integer
    edad_value = st.session_state.get('edad', 25)
    if isinstance(edad_value, str):
        try:
            edad_value = int(edad_value)
        except (ValueError, TypeError):
            edad_value = 25
    
    edad = st.number_input("Edad (años)*", min_value=15, max_value=80, value=edad_value, help="Tu edad actual")
    sexo = st.selectbox("Sexo biológico*", options=["Hombre", "Mujer"], index=0 if st.session_state.get('sexo', 'Hombre') == 'Hombre' else 1, placeholder="Selecciona una opción", help="Necesario para análisis nutricionales precisos")
    fecha_llenado = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 Fecha de evaluación: {fecha_llenado}")

acepto_terminos = st.checkbox("He leído y acepto la política de privacidad y el descargo de responsabilidad", value=st.session_state.get('acepto_terminos', False))

if st.button("🚀 COMENZAR EVALUACIÓN", disabled=not acepto_terminos):
    # Validación estricta de cada campo
    name_valid, name_error = validate_name(nombre)
    phone_valid, phone_error = validate_phone(telefono)
    email_valid, email_error = validate_email(email_cliente)
    
    # Mostrar errores específicos para cada campo que falle
    validation_errors = []
    if not name_valid:
        validation_errors.append(f"**Nombre:** {name_error}")
    if not phone_valid:
        validation_errors.append(f"**Teléfono:** {phone_error}")
    if not email_valid:
        validation_errors.append(f"**Email:** {email_error}")
    
    # Solo proceder si todas las validaciones pasan
    if name_valid and phone_valid and email_valid:
        st.session_state.datos_completos = True
        st.session_state.nombre = nombre
        st.session_state.telefono = telefono
        st.session_state.email_cliente = email_cliente
        st.session_state.edad = edad
        st.session_state.sexo = sexo
        st.session_state.fecha_llenado = fecha_llenado
        st.session_state.acepto_terminos = acepto_terminos
        st.success("✅ Datos registrados correctamente. ¡Continuemos con tu evaluación de patrones alimentarios!")
    else:
        # Mostrar todos los errores de validación
        error_message = "⚠️ **Por favor corrige los siguientes errores:**\n\n" + "\n\n".join(validation_errors)
        st.error(error_message)

st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.datos_completos:
    st.markdown("""
    <div class="content-card" style="margin-top:2rem; padding:3rem; background: #181A1B; color: #F5F5F5; border-left: 5px solid #F4C430;">
        <div style="text-align:center;">
            <h2 style="color: #F5C430; font-weight:900; margin:0;">
                🍽️ Bienvenido a MUPAI Patrones Alimentarios
            </h2>
            <p style="color: #F5F5F5;font-size:1.1rem;font-weight:600;margin-top:1.5rem;">
                <span style="font-size:1.15rem; font-weight:700;">¿Cómo funciona la evaluación?</span>
            </p>
            <div style="text-align:left;display:inline-block;max-width:650px;">
                <ul style="list-style:none;padding:0;">
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">📝</span> <b>Paso 1:</b> Información personal<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Recopilamos tu información básica para personalizar la evaluación nutricional.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🥩</span> <b>Paso 2:</b> Proteínas animales con más contenido graso<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Identificamos huevos, embutidos, carnes grasas, quesos altos en grasa y pescados grasos.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🍗</span> <b>Paso 3:</b> Proteínas animales magras<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Evaluamos carnes magras, pescados blancos, quesos bajos en grasa y lácteos light.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🥑</span> <b>Paso 4:</b> Fuentes de grasa saludable<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Analizamos grasas naturales, frutos secos, semillas y mantequillas vegetales.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🍞</span> <b>Paso 5:</b> Carbohidratos complejos y cereales<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Evaluamos cereales integrales, tortillas, panes, raíces, tubérculos y leguminosas.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🥬</span> <b>Paso 6:</b> Vegetales y frutas<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Identificamos todos los vegetales y frutas que consumes o toleras fácilmente.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🍳</span> <b>Paso 7:</b> Aceites de cocción y bebidas<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Evaluamos tus preferencias de aceites para cocinar y bebidas sin calorías.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🚨</span> <b>Paso 8:</b> Alergias, intolerancias y métodos de cocción<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Identificamos restricciones alimentarias y métodos de cocción disponibles.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">😋</span> <b>Paso 9:</b> Patrones de antojos alimentarios<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Analizamos antojos dulces, salados, comida rápida y condimentos estimulantes.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">📈</span> <b>Resultado final:</b> Perfil alimentario completo<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Recibes un análisis detallado de tus patrones alimentarios y recomendaciones personalizadas.
                        </span>
                    </li>
                </ul>
                <div style="margin-top:1.2em; font-size:1rem; color:#F4C430;">
                    <b>Finalidad:</b> Esta evaluación integra principios de nutrición personalizada para ofrecerte recomendaciones alimentarias que se ajusten a tu estilo de vida y preferencias específicas. <br>
                    <b>Tiempo estimado:</b> Menos de 10 minutos.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# VALIDACIÓN DATOS PERSONALES PARA CONTINUAR
datos_personales_completos = all([nombre, telefono, email_cliente]) and acepto_terminos

if datos_personales_completos and st.session_state.datos_completos:
    # Progress bar mejorado y más prominente
    st.markdown("### 📊 Progreso de tu Evaluación")
    progress = st.progress(0, text="Iniciando evaluación...")
    progress_container = st.container()
    
    # CUESTIONARIO DE SELECCIÓN ALIMENTARIA PERSONALIZADA CON MEJOR DISEÑO
    st.markdown("""
    <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
        <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1.5rem;">
            🧾 CUESTIONARIO DE SELECCIÓN ALIMENTARIA PERSONALIZADA
        </h2>
        <div style="text-align: left; font-size: 1.1rem; line-height: 1.6;">
            <p><strong>📋 Instrucciones importantes:</strong></p>
            <ul style="margin-left: 1rem;">
                <li><strong>✅ Selecciona múltiples opciones:</strong> Puedes marcar TODOS los alimentos que consumes o disfrutas en cada categoría</li>
                <li><strong>🎯 Sé específico:</strong> Entre más alimentos marques, más personalizado será tu plan nutricional</li>
                <li><strong>⏱️ Tiempo estimado:</strong> 5-8 minutos para completar toda la evaluación</li>
                <li><strong>💡 Consejo:</strong> Si tienes dudas sobre un alimento, márcalo. Es mejor incluir más opciones</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navegación mejorada por pasos - Ahora refleja el progreso real
    current_step = st.session_state.get('current_step', 1)
    max_unlocked = st.session_state.get('max_unlocked_step', 1)
    step_completed = st.session_state.get('step_completed', {})
    
    # Verificar estado de validación en tiempo real
    step_validators = {
        1: validate_step_1(),
        2: validate_step_2(),
        3: validate_step_3(),
        4: validate_step_4(),
        5: validate_step_5(),
        6: validate_step_6(),
        7: validate_step_7(),
        8: validate_step_8(),
        9: validate_step_9(),
        10: validate_step_10(),
        11: validate_step_11(),
        12: validate_step_12()
    }
    
    st.markdown(f"""
    <div class="content-card" style="background: #2A2A2A; border-left: 5px solid #F4C430;">
        <h3 style="color: #F4C430; text-align: center; margin-bottom: 1rem;">🗺️ Progreso del Cuestionario</h3>
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 1 else '#27AE60' if step_validators[1] else '#E74C3C'}; color: #1E1E1E; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">{'✓' if step_validators[1] else '1'}</div>
                <small>Proteínas Grasas</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 2 else '#27AE60' if step_validators[2] else '#E74C3C' if max_unlocked >= 2 else '#666'}; color: {'#1E1E1E' if current_step == 2 or step_validators[2] else '#FFF'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">{'✓' if step_validators[2] else '2'}</div>
                <small>Proteínas Magras</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 3 else '#27AE60' if step_validators[3] else '#E74C3C' if max_unlocked >= 3 else '#666'}; color: {'#1E1E1E' if current_step == 3 or step_validators[3] else '#FFF'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">{'✓' if step_validators[3] else '3'}</div>
                <small>Grasas Saludables</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 4 else '#27AE60' if step_validators[4] else '#E74C3C' if max_unlocked >= 4 else '#666'}; color: {'#1E1E1E' if current_step == 4 or step_validators[4] else '#FFF'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">{'✓' if step_validators[4] else '4'}</div>
                <small>Carbohidratos</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 5 else '#27AE60' if step_validators[5] else '#E74C3C' if max_unlocked >= 5 else '#666'}; color: {'#1E1E1E' if current_step == 5 or step_validators[5] else '#FFF'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">{'✓' if step_validators[5] else '5'}</div>
                <small>Vegetales</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 6 else '#27AE60' if step_validators[6] else '#E74C3C' if max_unlocked >= 6 else '#666'}; color: {'#1E1E1E' if current_step == 6 or step_validators[6] else '#FFF'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">{'✓' if step_validators[6] else '6'}</div>
                <small>Frutas</small>
            </div>
        </div>
        <div style="text-align: center; margin-top: 1rem; color: #CCCCCC;">
            <small>Paso {current_step} de 12 - {'✅ Completado' if step_validators.get(current_step, False) else '⏳ En progreso'}</small>
        </div>
        <div style="text-align: center; margin-top: 0.5rem; font-size: 0.9rem;">
            <span style="color: #27AE60;">● Completo</span> | 
            <span style="color: #F4C430;">● Actual</span> | 
            <span style="color: #E74C3C;">● Incompleto</span> | 
            <span style="color: #666;">● Bloqueado</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar solo el paso actual
    current_step = st.session_state.get('current_step', 1)

    # GRUPO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO
    if current_step == 1:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
            border: 3px solid #4CAF50;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🥩 PASO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 1 de 12 - Selecciona las proteínas grasas que consumes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso1"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso1');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥩 PASO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(8, text="Paso 1 de 12: Proteínas con más contenido graso")
        
        # Actualizar indicador visual
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="background: #F4C430; color: #1E1E1E; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">1</div>
            <h4 style="color: #F4C430; margin-top: 0.5rem;">PASO ACTUAL</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        En este paso evaluaremos las **proteínas animales con mayor contenido graso** que consumes. 
        Estos alimentos son importantes para la saciedad y el aporte de grasas esenciales.
        
        **💡 Instrucción:** Marca TODOS los alimentos que consumes habitualmente o que disfrutas comer.
        """)
        
        st.markdown("#### 🍳 Huevos y embutidos")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        huevos_embutidos = st.multiselect(
            "¿Cuáles de estos huevos y embutidos consumes? (Puedes seleccionar varios)",
            ["Huevo entero", "Chorizo", "Salchicha (Viena, alemana, parrillera)", "Longaniza", "Tocino", "Jamón serrano", "Jamón ibérico", "Salami", "Mortadela", "Pastrami", "Pepperoni", "Ninguno"],
            key="huevos_embutidos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los que consumes. Marca 'Ninguno' si no consumes ninguno de estos alimentos."
        )
        
        st.markdown("#### 🥩 Carnes de res grasas")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        carnes_res_grasas = st.multiselect(
            "¿Cuáles de estas carnes de res grasas consumes? (Puedes seleccionar varios)",
            ["Aguja norteña", "Diezmillo marmoleado", "Costilla/Costillar", "Ribeye", "New York", "T-bone", "Porterhouse", "Prime rib", "Arrachera", "Picaña", "Suadero", "Brisket/Pecho de res", "Chamberete con tuétano", "Falda marmoleada", "Molida 80/20", "Molida 85/15", "Carne para asar con grasa", "Chuck roast (diezmillo graso)", "Paleta con grasa", "Retazo con grasa", "Short ribs", "Cowboy steak", "Tomahawk", "Matambre", "Entraña", "Ninguno"],
            key="carnes_res_grasas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los cortes que consumes. Marca 'Ninguno' si no consumes ninguno de estos cortes."
        )
        
        st.markdown("#### 🐷 Carnes de cerdo grasas")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        carnes_cerdo_grasas = st.multiselect(
            "¿Cuáles de estas carnes de cerdo grasas consumes? (Puedes seleccionar varios)",
            ["Costilla de cerdo", "Panceta (belly)", "Chuleta con grasa", "Carnitas", "Chicharrón prensado", "Codillo", "Espalda (Boston butt)", "Picnic shoulder", "Pata de cerdo", "Ninguno"],
            key="carnes_cerdo_grasas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los cortes que consumes. Marca 'Ninguno' si no consumes ninguno de estos cortes."
        )
        
        st.markdown("#### 🐔 Carnes de pollo/pavo grasas")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        carnes_pollo_grasas = st.multiselect(
            "¿Cuáles de estas carnes de pollo/pavo grasas consumes? (Puedes seleccionar varios)",
            ["Muslo de pollo con piel", "Pierna de pollo con piel", "Alitas de pollo", "Pollo entero con piel", "Pavo con piel", "Muslo de pavo", "Ninguno"],
            key="carnes_pollo_grasas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los cortes que consumes. Marca 'Ninguno' si no consumes ninguno de estos cortes."
        )
        
        st.markdown("#### 🫀 Órganos y vísceras grasas")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        organos_grasos = st.multiselect(
            "¿Cuáles de estos órganos y vísceras grasas consumes? (Puedes seleccionar varios)",
            ["Sesos de res", "Tuétano de res", "Molleja de res", "Hígado de res", "Riñón de res", "Ninguno"],
            key="organos_grasos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los órganos que consumes. Marca 'Ninguno' si no consumes ninguno de estos alimentos."
        )
        
        st.markdown("#### 🧀 Quesos altos en grasa")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        quesos_grasos = st.multiselect(
            "¿Cuáles de estos quesos altos en grasa consumes? (Puedes seleccionar varios)",
            ["Queso manchego", "Queso doble crema", "Queso oaxaca", "Queso gouda", "Queso crema", "Queso cheddar", "Queso roquefort", "Queso brie", "Queso camembert", "Queso parmesano", "Queso gruyere", "Queso de cabra maduro", "Ninguno"],
            key="quesos_grasos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los quesos que consumes. Marca 'Ninguno' si no consumes ninguno de estos quesos."
        )
        
        st.markdown("#### 🥛 Lácteos enteros")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        lacteos_enteros = st.multiselect(
            "¿Cuáles de estos lácteos enteros consumes? (Puedes seleccionar varios)",
            ["Leche entera", "Yogur entero azucarado", "Yogur tipo griego entero", "Yogur de frutas azucarado", 
             "Yogur bebible regular", "Crema", "Queso para untar (tipo Philadelphia original)", "Nata", "Crema agria", "Ninguno"],
            key="lacteos_enteros",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los lácteos enteros que uses. Marca 'Ninguno' si no consumes ninguno de estos lácteos."
        )
        
        st.markdown("#### 🐟 Pescados grasos")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        pescados_grasos = st.multiselect(
            "¿Cuáles de estos pescados grasos consumes? (Puedes seleccionar varios)",
            ["Atún en aceite", "Salmón", "Sardinas", "Macarela", "Trucha", "Arenque", "Anchovetas", "Pez espada", "Anguila", "Ninguno"],
            key="pescados_grasos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los pescados grasos que consumes. Marca 'Ninguno' si no consumes ninguno de estos pescados."
        )
        
        st.markdown("#### 🦐 Mariscos/comida marina grasos")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        mariscos_grasos = st.multiselect(
            "¿Cuáles de estos mariscos/comida marina grasos consumes? (Puedes seleccionar varios)",
            ["Pulpo", "Calamar", "Mejillones", "Ostras", "Cangrejo", "Langosta", "Caracol de mar", "Ninguno"],
            key="mariscos_grasos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los mariscos grasos que consumes. Marca 'Ninguno' si no consumes ninguno de estos mariscos."
        )

        # Resumen del paso actual
        total_seleccionados = (len(st.session_state.get('huevos_embutidos', [])) + 
                              len(st.session_state.get('carnes_res_grasas', [])) + 
                              len(st.session_state.get('carnes_cerdo_grasas', [])) + 
                              len(st.session_state.get('carnes_pollo_grasas', [])) + 
                              len(st.session_state.get('organos_grasos', [])) + 
                              len(st.session_state.get('quesos_grasos', [])) + 
                              len(st.session_state.get('lacteos_enteros', [])) + 
                              len(st.session_state.get('pescados_grasos', [])) + 
                              len(st.session_state.get('mariscos_grasos', [])))
        if total_seleccionados > 0:
            st.success(f"✅ **¡Excelente!** Has seleccionado {total_seleccionados} alimentos en este grupo. Esto nos ayudará a personalizar mejor tu plan.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior", disabled=True):
                pass
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # GRUPO 2: PROTEÍNA ANIMAL MAGRA
    elif current_step == 2:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
            border: 3px solid #2196F3;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🍗 PASO 2: PROTEÍNA ANIMAL MAGRA
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 2 de 12 - Selecciona las proteínas magras que consumes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso2"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso2');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍗 PASO 2: PROTEÍNA ANIMAL MAGRA
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(17, text="Paso 2 de 12: Proteínas animales magras")
        
        # Actualizar indicador visual
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="background: #F4C430; color: #1E1E1E; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">2</div>
            <h4 style="color: #F4C430; margin-top: 0.5rem;">PASO ACTUAL</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        En este paso evaluaremos las **proteínas animales magras** que consumes. 
        Estos alimentos son excelentes fuentes de proteína con menor contenido graso.
        
        **💡 Instrucción:** Marca TODOS los alimentos que te resultan fáciles de consumir o que disfrutas.
        """)
        
        st.markdown("#### 🐄 Carnes de res magras")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        carnes_res_magras = st.multiselect(
            "¿Cuáles de estas carnes de res magras consumes? (Puedes seleccionar varios)",
            ["Filete (lomo fino)", "Lomo bajo (striploin limpio)", "Centro de diezmillo limpio", "Sirloin limpio/Aguayón", "Bola/Pulpa bola", "Cuete", "Pulpa negra", "Pulpa blanca", "Espaldilla limpia", "Milanesa de bola", "Bistec de pierna", "Molida 90/10", "Molida 95/5", "Molida 97/3", "Falda limpia", "Chamorro limpio", "Tampiqueña magra", "Medallones de res magros", "Top round", "Bottom round", "Flank steak limpio", "Maciza limpia", "Ninguno"],
            key="carnes_res_magras",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las carnes de res magras que consumas. Marca 'Ninguno' si no consumes ninguna de estas carnes."
        )
        
        st.markdown("#### 🐷 Carnes de cerdo magras")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        carnes_cerdo_magras = st.multiselect(
            "¿Cuáles de estas carnes de cerdo magras consumes? (Puedes seleccionar varios)",
            ["Lomo de cerdo", "Filete de cerdo", "Chuleta magra sin grasa", "Solomillo de cerdo", "Tenderloin", "Ninguno"],
            key="carnes_cerdo_magras",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las carnes de cerdo magras que consumas. Marca 'Ninguno' si no consumes ninguna de estas carnes."
        )
        
        st.markdown("#### 🐔 Carnes de pollo/pavo magras")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        carnes_pollo_magras = st.multiselect(
            "¿Cuáles de estas carnes de pollo/pavo magras consumes? (Puedes seleccionar varios)",
            ["Pechuga de pollo sin piel", "Pechuga de pavo sin piel", "Muslo de pollo sin piel", "Pierna de pavo sin piel", "Ninguno"],
            key="carnes_pollo_magras",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las carnes de pollo/pavo magras que consumas. Marca 'Ninguno' si no consumes ninguna de estas carnes."
        )
        
        st.markdown("#### 🫀 Órganos y vísceras magros")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        organos_magros = st.multiselect(
            "¿Cuáles de estos órganos y vísceras magros consumes? (Puedes seleccionar varios)",
            ["Corazón de res", "Lengua de res", "Hígado de ternera", "Riñones de ternera", "Corazón de pollo", "Hígado de pollo", "Molleja de ternera", "Ninguno"],
            key="organos_magros",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los órganos magros que consumas. Marca 'Ninguno' si no consumes ninguno de estos alimentos."
        )
        
        st.markdown("#### 🐟 Pescados magros")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        pescados_magros = st.multiselect(
            "¿Cuáles de estos pescados magros consumes? (Puedes seleccionar varios)",
            ["Tilapia", "Basa", "Huachinango", "Merluza", "Robalo", "Atún en agua", "Bacalao", "Lenguado", "Mero", "Dorado", "Pargo", "Ninguno"],
            key="pescados_magros",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los pescados magros que consumas. Marca 'Ninguno' si no consumes ninguno de estos pescados."
        )
        
        st.markdown("#### 🦐 Mariscos/comida marina magros")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        mariscos_magros = st.multiselect(
            "¿Cuáles de estos mariscos/comida marina magros consumes? (Puedes seleccionar varios)",
            ["Camarón", "Callo de hacha", "Almeja", "Langostino", "Jaiba", "Ninguno"],
            key="mariscos_magros",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los mariscos magros que consumas. Marca 'Ninguno' si no consumes ninguno de estos mariscos."
        )
        
        st.markdown("#### 🧀 Quesos magros")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        quesos_magros = st.multiselect(
            "¿Cuáles de estos quesos magros consumes? (Puedes seleccionar varios)",
            ["Queso panela", "Queso cottage", "Queso ricotta light", "Queso oaxaca reducido en grasa", 
             "Queso mozzarella light", "Queso fresco bajo en grasa", "Queso de cabra magro", "Ninguno"],
            key="quesos_magros",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los quesos magros que consumes. Marca 'Ninguno' si no consumes ninguno de estos quesos."
        )
        
        st.markdown("#### 🥛 Lácteos light o reducidos")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        lacteos_light = st.multiselect(
            "¿Cuáles de estos lácteos light o reducidos consumes? (Puedes seleccionar varios)",
            ["Leche descremada", "Leche deslactosada light", "Leche de almendra sin azúcar", 
             "Leche de coco sin azúcar", "Leche de soya sin azúcar", "Yogur griego natural sin azúcar", 
             "Yogur griego light", "Yogur bebible bajo en grasa", "Yogur sin azúcar añadida", 
             "Yogur de frutas bajo en grasa y sin azúcar añadida", "Queso crema light", "Ninguno"],
            key="lacteos_light",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los lácteos light que uses. Marca 'Ninguno' si no consumes ninguno de estos lácteos."
        )
        
        st.markdown("#### 🥚 Huevos y embutidos light")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        huevos_embutidos_light = st.multiselect(
            "¿Cuáles de estos huevos y embutidos light consumes? (Puedes seleccionar varios)",
            ["Clara de huevo", "Jamón de pechuga de pavo", "Jamón de pierna bajo en grasa", "Salchicha de pechuga de pavo (light)", "Pechuga de pavo rebanada", "Jamón serrano magro", "Ninguno"],
            key="huevos_embutidos_light",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los huevos y embutidos light que consumes. Marca 'Ninguno' si no consumes ninguno de estos alimentos."
        )
        # Resumen del paso actual
        total_seleccionados = (len(st.session_state.get('carnes_res_magras', [])) + 
                              len(st.session_state.get('carnes_cerdo_magras', [])) + 
                              len(st.session_state.get('carnes_pollo_magras', [])) + 
                              len(st.session_state.get('organos_magros', [])) + 
                              len(st.session_state.get('pescados_magros', [])) + 
                              len(st.session_state.get('mariscos_magros', [])) + 
                              len(st.session_state.get('quesos_magros', [])) + 
                              len(st.session_state.get('lacteos_light', [])) + 
                              len(st.session_state.get('huevos_embutidos_light', [])))
        if total_seleccionados > 0:
            st.success(f"✅ **¡Excelente!** Has seleccionado {total_seleccionados} alimentos en este grupo. Las proteínas magras son fundamentales para tu plan.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # GRUPO 3: FUENTES DE GRASA SALUDABLE
    elif current_step == 3:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3);
            border: 3px solid #FF9800;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🥑 PASO 3: FUENTES DE GRASA SALUDABLE
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 3 de 12 - Selecciona las grasas saludables que consumes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso3"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso3');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥑 PASO 3: FUENTES DE GRASA SALUDABLE
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(25, text="Paso 3 de 12: Fuentes de grasa saludable")
        
        # Actualizar indicador visual
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="background: #F4C430; color: #1E1E1E; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">3</div>
            <h4 style="color: #F4C430; margin-top: 0.5rem;">PASO ACTUAL</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        En este paso evaluaremos las **fuentes de grasa saludable** que consumes. 
        Estas grasas son esenciales para la absorción de vitaminas y el funcionamiento hormonal.
        
        **💡 Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.
        """)
        
        st.markdown("#### 🥑 Grasas naturales de alimentos")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        grasas_naturales = st.multiselect(
            "¿Cuáles de estas grasas naturales consumes? (Puedes seleccionar varios)",
            ["Aguacate", "Yema de huevo", "Aceitunas (negras, verdes)", "Coco rallado natural", 
             "Coco fresco", "Leche de coco sin azúcar", "Ninguno"],
            key="grasas_naturales",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las grasas naturales que consumes. Marca 'Ninguno' si no consumes ninguna de estas grasas."
        )
        
        st.markdown("#### 🌰 Frutos secos y semillas")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        frutos_secos_semillas = st.multiselect(
            "¿Cuáles de estos frutos secos y semillas consumes? (Puedes seleccionar varios)",
            ["Almendras", "Nueces", "Nuez de la India", "Pistaches", "Cacahuates naturales (sin sal)", 
             "Semillas de chía", "Semillas de linaza", "Semillas de girasol", "Semillas de calabaza (pepitas)", "Ninguno"],
            key="frutos_secos_semillas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los frutos secos y semillas que consumes. Marca 'Ninguno' si no consumes ninguno de estos."
        )
        
        st.markdown("#### 🧈 Mantequillas y pastas vegetales")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        mantequillas_vegetales = st.multiselect(
            "¿Cuáles de estas mantequillas y pastas vegetales consumes? (Puedes seleccionar varios)",
            ["Mantequilla de maní natural", "Mantequilla de almendra", "Tahini (pasta de ajonjolí)", 
             "Mantequilla de nuez de la India", "Ninguno"],
            key="mantequillas_vegetales",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las mantequillas vegetales que consumes. Marca 'Ninguno' si no consumes ninguna de estas."
        )

        # Resumen del paso actual
        total_seleccionados = (len(st.session_state.get('grasas_naturales', [])) + 
                              len(st.session_state.get('frutos_secos_semillas', [])) + 
                              len(st.session_state.get('mantequillas_vegetales', [])))
        if total_seleccionados > 0:
            st.success(f"✅ **¡Excelente!** Has seleccionado {total_seleccionados} fuentes de grasa saludable. Estas son clave para un plan equilibrado.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # GRUPO 4: CARBOHIDRATOS COMPLEJOS Y CEREALES
    elif current_step == 4:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(156, 39, 176, 0.3);
            border: 3px solid #9C27B0;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🍞 PASO 4: CARBOHIDRATOS COMPLEJOS Y CEREALES
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 4 de 12 - Selecciona los carbohidratos que consumes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso4"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso4');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍞 PASO 4: CARBOHIDRATOS COMPLEJOS Y CEREALES
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(33, text="Paso 4 de 12: Carbohidratos complejos y cereales")
        
        # Actualizar indicador visual
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="background: #F4C430; color: #1E1E1E; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">4</div>
            <h4 style="color: #F4C430; margin-top: 0.5rem;">PASO ACTUAL</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        En este paso evaluaremos los **carbohidratos complejos y cereales** que consumes. 
        Estos alimentos proporcionan energía sostenida y fibra importante para tu digestión.
        
        **💡 Instrucción:** Marca TODOS los alimentos que consumas con facilidad, incluso ocasionalmente.
        """)
        
        st.markdown("#### 🌾 Cereales y granos integrales")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        cereales_integrales = st.multiselect(
            "¿Cuáles de estos cereales y granos integrales consumes? (Puedes seleccionar varios)",
            ["Avena tradicional", "Avena instantánea sin azúcar", "Arroz integral", "Arroz blanco", 
             "Arroz jazmín", "Arroz basmati", "Trigo bulgur", "Cuscús", "Quinoa", "Amaranto", 
             "Trigo inflado natural", "Cereal de maíz sin azúcar", "Cereal integral bajo en azúcar", "Ninguno"],
            key="cereales_integrales",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los cereales y granos que consumes. Marca 'Ninguno' si no consumes ninguno de estos."
        )
        
        st.markdown("#### 🍝 Pastas")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        pastas = st.multiselect(
            "¿Cuáles de estas pastas consumes? (Puedes seleccionar varios)",
            ["Pasta integral", "Pasta de trigo regular", "Pasta de arroz", "Pasta de quinoa", "Pasta de legumbres (lentejas, garbanzos)", "Fideos de arroz", "Fideos chinos", "Spaguetti", "Macarrones", "Lasaña", "Ninguno"],
            key="pastas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todas las pastas que consumes. Marca 'Ninguno' si no consumes ninguna de estas."
        )
        
        st.markdown("#### 🌽 Tortillas y panes")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        tortillas_panes = st.multiselect(
            "¿Cuáles de estas tortillas y panes consumes? (Puedes seleccionar varios)",
            ["Tortilla de maíz", "Tortilla de nopal", "Tortilla integral", "Tortilla de harina", 
             "Tortilla de avena", "Pan integral", "Pan multigrano", "Pan de centeno", 
             "Pan de caja sin azúcar añadida", "Pan pita integral", "Pan tipo Ezekiel (germinado)", "Ninguno"],
            key="tortillas_panes",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los tipos de tortillas y panes que consumes. Marca 'Ninguno' si no consumes ninguno."
        )
        
        st.markdown("#### 🥔 Raíces y tubérculos (forma base)")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        raices_tuberculos = st.multiselect(
            "¿Cuáles de estas raíces y tubérculos consumes? (Puedes seleccionar varios)",
            ["Papa", "Camote", "Yuca", "Plátano macho", "Jícama", "Zanahoria", "Betabel", "Ninguno"],
            key="raices_tuberculos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los tubérculos y raíces que consumes en su forma base. Marca 'Ninguno' si no consumes ninguno de estos."
        )
        
        st.markdown("#### 🫘 Leguminosas")
        st.info("💡 **Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.")
        leguminosas = st.multiselect(
            "¿Cuáles de estas leguminosas consumes? (Puedes seleccionar varios)",
            ["Frijoles negros", "Frijoles bayos", "Frijoles pintos", "Lentejas", "Garbanzos", 
             "Habas cocidas", "Soya texturizada", "Edamames (vainas de soya)", "Hummus (puré de garbanzo)", "Ninguno"],
            key="leguminosas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las leguminosas que consumes. Marca 'Ninguno' si no consumes ninguna de estas."
        )

        # Resumen del paso actual
        total_seleccionados = (len(st.session_state.get('cereales_integrales', [])) + 
                              len(st.session_state.get('pastas', [])) + 
                              len(st.session_state.get('tortillas_panes', [])) + 
                              len(st.session_state.get('raices_tuberculos', [])) + 
                              len(st.session_state.get('leguminosas', [])))
        if total_seleccionados > 0:
            st.success(f"✅ **¡Excelente!** Has seleccionado {total_seleccionados} fuentes de carbohidratos. Estos proporcionarán energía para tu plan.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # GRUPO 5: VEGETALES
    elif current_step == 5:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
            border: 3px solid #4CAF50;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🥬 PASO 5: VEGETALES
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 5 de 12 - Selecciona los vegetales que consumes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso5"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso5');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥬 PASO 5: VEGETALES
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(42, text="Paso 5 de 12: Vegetales")
        
        # Actualizar indicador visual
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="background: #F4C430; color: #1E1E1E; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">5</div>
            <h4 style="color: #F4C430; margin-top: 0.5rem;">PASO ACTUAL</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        En este paso evaluaremos los **vegetales** que consumes o toleras fácilmente. 
        Los vegetales aportan vitaminas, minerales, fibra y antioxidantes esenciales para tu salud.
        
        **💡 Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.
        """)
        
        st.info("💡 **Ayuda:** Incluye vegetales que consumas crudos, cocidos, al vapor, salteados o en cualquier preparación. Entre más vegetales selecciones, más variado será tu plan.")
        
        vegetales_lista = st.multiselect(
            "¿Cuáles de estos vegetales consumes o toleras fácilmente? (Puedes seleccionar varios)",
            ["Espinaca", "Acelga", "Kale", "Lechuga (romana, italiana, orejona, iceberg)", 
             "Col morada", "Col verde", "Repollo", "Brócoli", "Coliflor", "Ejote", "Chayote", 
             "Calabacita", "Nopal", "Betabel", "Zanahoria", "Jitomate saladet", "Jitomate bola", 
             "Tomate verde", "Cebolla blanca", "Cebolla morada", "Pimiento morrón (rojo, verde, amarillo, naranja)", 
             "Pepino", "Apio", "Rábano", "Ajo", "Berenjena", "Champiñones", "Guisantes (chícharos)", 
             "Verdolaga", "Habas tiernas", "Germen de alfalfa", "Germen de soya", "Flor de calabaza", "Ninguno"],
            key="vegetales_lista",
            placeholder="🔽 Haz clic aquí para ver y seleccionar todos los vegetales que consumes",
            help="Selecciona todos los vegetales que consumes o toleras. Marca 'Ninguno' si no consumes ninguno de estos vegetales."
        )

        # Resumen del paso actual con categorización
        vegetales_count = len(st.session_state.get('vegetales_lista', []))
        if vegetales_count >= 15:
            st.success(f"✅ **¡Excelente diversidad!** Has seleccionado {vegetales_count} vegetales. Esto permitirá crear un plan muy variado y nutritivo.")
        elif vegetales_count >= 8:
            st.success(f"✅ **¡Buena variedad!** Has seleccionado {vegetales_count} vegetales. Tu plan tendrá buena diversidad nutricional.")
        elif vegetales_count >= 3:
            st.info(f"ℹ️ **Variedad básica:** Has seleccionado {vegetales_count} vegetales. Considera probar otros vegetales para enriquecer tu plan.")
        elif vegetales_count > 0:
            st.warning(f"⚠️ **Poca variedad:** Solo has seleccionado {vegetales_count} vegetales. Te recomendamos incluir más opciones.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # GRUPO 6: FRUTAS
    elif current_step == 6:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #E91E63 0%, #C2185B 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(233, 30, 99, 0.3);
            border: 3px solid #E91E63;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🍎 PASO 6: FRUTAS
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 6 de 12 - Selecciona las frutas que consumes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso6"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso6');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍎 PASO 6: FRUTAS
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(50, text="Paso 6 de 12: Frutas - ¡Completando grupos principales!")
        
        # Actualizar indicador visual
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="background: #F4C430; color: #1E1E1E; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 1.2rem;">6</div>
            <h4 style="color: #F4C430; margin-top: 0.5rem;">¡ÚLTIMO GRUPO PRINCIPAL!</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        En este último paso de los grupos principales evaluaremos las **frutas** que disfrutas o toleras bien. 
        Las frutas aportan vitaminas, antioxidantes, fibra y azúcares naturales para energía.
        
        **💡 Instrucción:** Preferentemente elige al menos uno de esta lista. Se pueden seleccionar más de uno. Si no consumes ninguno, selecciona 'Ninguno'.
        """)
        
        st.info("💡 **Ayuda:** Incluye frutas que consumas solas, en licuados, ensaladas, postres naturales o cualquier preparación. La variedad de frutas enriquecerá tu plan nutricional.")
        
        frutas_lista = st.multiselect(
            "¿Cuáles de estas frutas disfrutas o toleras bien? (Puedes seleccionar varios)",
            ["Manzana (roja, verde, gala, fuji)", "Naranja", "Mandarina", "Mango (petacón, ataulfo)", 
             "Papaya", "Sandía", "Melón", "Piña", "Plátano (tabasco, dominico, macho)", "Uvas", 
             "Fresas", "Arándanos", "Zarzamoras", "Frambuesas", "Higo", "Kiwi", "Pera", "Durazno", 
             "Ciruela", "Granada", "Cereza", "Chabacano", "Lima", "Limón", "Guayaba", "Tuna", 
             "Níspero", "Mamey", "Pitahaya (dragon fruit)", "Tamarindo", "Coco (carne, rallado)", 
             "Caqui (persimón)", "Maracuyá", "Manzana en puré sin azúcar", "Fruta en almíbar light", "Ninguno"],
            key='frutas_lista',
            placeholder="🔽 Haz clic aquí para ver y seleccionar todas las frutas que disfrutas",
            help="Selecciona todas las frutas que disfrutas. Marca 'Ninguno' si no consumes ninguna de estas frutas."
        )

        # Resumen del paso actual con categorización
        frutas_count = len(st.session_state.get('frutas_lista', []))
        if frutas_count >= 12:
            st.success(f"🎉 **¡Fantástica variedad!** Has seleccionado {frutas_count} frutas. Tu plan tendrá una excelente diversidad de sabores y nutrientes.")
        elif frutas_count >= 6:
            st.success(f"✅ **¡Buena selección!** Has seleccionado {frutas_count} frutas. Esto permitirá variedad en tu plan alimentario.")
        elif frutas_count >= 3:
            st.info(f"ℹ️ **Selección básica:** Has seleccionado {frutas_count} frutas. Considera incluir más opciones para mayor variedad.")
        elif frutas_count > 0:
            st.warning(f"⚠️ **Poca variedad:** Solo has seleccionado {frutas_count} frutas. Te sugerimos probar más opciones.")
        
        # Mensaje de finalización de grupos principales
        st.markdown("""
        ---
        ### 🎊 ¡Felicitaciones!
        Has completado la evaluación de los **6 grupos alimentarios principales**. 
        A continuación encontrarás secciones adicionales para complementar tu perfil nutricional.
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # APARTADO EXTRA 1: ACEITES DE COCCIÓN (PASO 7)
    elif current_step == 7:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #795548 0%, #5D4037 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(121, 85, 72, 0.3);
            border: 3px solid #795548;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🍳 PASO 7: ACEITES DE COCCIÓN PREFERIDOS
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 7 de 12 - Información Adicional (Opcional)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso7"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso7');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #27AE60 0%, #2ECC71 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #27AE60;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍳 PASO 7: ACEITES DE COCCIÓN PREFERIDOS
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">Información Adicional - Opcional</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(58, text="Paso 7 de 12: Aceites de cocción (Opcional)")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        Queremos conocer los **aceites y grasas** que utilizas para cocinar, freír, hornear o saltear tus alimentos.
        Esto nos ayuda a adaptar las recetas a tus preferencias y métodos disponibles.
        
        **💡 Instrucción:** Selecciona TODAS las opciones que sueles usar en tu cocina. (Este paso es opcional)
        """)
        
        st.info("💡 **Ayuda:** Incluye cualquier grasa o aceite que uses para cocinar, desde aceites vegetales hasta mantequilla o manteca.")
        
        aceites_coccion = st.multiselect(
            "¿Cuáles de estas grasas/aceites usas para cocinar? (Puedes seleccionar varios)",
            ["🫒 Aceite de oliva extra virgen", "🥑 Aceite de aguacate", "🥥 Aceite de coco virgen", 
             "🧈 Mantequilla con sal", "🧈 Mantequilla sin sal", "🧈 Mantequilla clarificada (ghee)", 
             "🐷 Manteca de cerdo (casera o artesanal)", "🧴 Spray antiadherente sin calorías (aceite de oliva o aguacate)", 
             "❌ Prefiero cocinar sin aceite o con agua", "Ninguno"],
            key='aceites_coccion',
            placeholder="🔽 Haz clic aquí para seleccionar los aceites que usas para cocinar",
            help="Selecciona todos los aceites y grasas que usas en tu cocina. Marca 'Ninguno' si no usas ninguno de estos aceites."
        )

        # Resumen
        aceites_count = len(st.session_state.get('aceites_coccion', []))
        if aceites_count > 0:
            st.success(f"✅ **Perfecto!** Has seleccionado {aceites_count} opciones. Esto nos ayuda a personalizar las recetas según tus métodos de cocción.")
        else:
            st.info("ℹ️ **Nota:** Si no seleccionas ningún aceite, asumiremos métodos de cocción sin grasa añadida.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # APARTADO EXTRA 2: BEBIDAS (PASO 8)
    elif current_step == 8:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(0, 188, 212, 0.3);
            border: 3px solid #00BCD4;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🥤 PASO 8: BEBIDAS PARA HIDRATACIÓN
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 8 de 12 - Información Adicional (Opcional)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso8"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso8');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #27AE60 0%, #2ECC71 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #27AE60;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥤 PASO 8: BEBIDAS PARA HIDRATACIÓN
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">Información Adicional - Opcional</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(67, text="Paso 8 de 12: Bebidas para hidratación (Opcional)")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Qué necesitamos saber?
        Queremos conocer las **bebidas sin calorías** que consumes regularmente para mantenerte hidratado.
        Esto nos ayuda a incluir opciones de hidratación que realmente disfrutes en tu plan.
        
        **💡 Instrucción:** Marca TODAS las bebidas que acostumbres tomar para hidratarte. (Este paso es opcional)
        """)
        
        st.info("💡 **Ayuda:** Incluye cualquier bebida sin calorías o muy bajas en calorías que tomes durante el día.")
        
        bebidas_sin_calorias = st.multiselect(
            "¿Cuáles de estas bebidas sin calorías consumes regularmente? (Puedes seleccionar varios)",
            ["💧 Agua natural", "💦 Agua mineral", "⚡ Bebidas con electrolitos sin azúcar (Electrolit Zero, SueroX, LMNT, etc.)", 
             "🍋 Agua infusionada con frutas naturales (limón, pepino, menta, etc.)", 
             "🍵 Té de hierbas sin azúcar (manzanilla, menta, jengibre, etc.)", 
             "🍃 Té verde o té negro sin azúcar", "☕ Café negro sin azúcar", 
             "🥤 Refrescos sin calorías (Coca Cola Zero, Pepsi Light, etc.)", "Ninguno"],
            key='bebidas_sin_calorias',
            placeholder="🔽 Haz clic aquí para seleccionar las bebidas que consumes",
            help="Selecciona todas las bebidas sin calorías que acostumbres. Marca 'Ninguno' si no consumes ninguna de estas bebidas."
        )

        # Resumen
        bebidas_count = len(st.session_state.get('bebidas_sin_calorias', []))
        if bebidas_count > 0:
            st.success(f"✅ **Excelente!** Has seleccionado {bebidas_count} opciones de hidratación. Esto enriquece las recomendaciones de tu plan.")
        else:
            st.info("ℹ️ **Nota:** La hidratación es fundamental. Te recomendamos incluir al menos agua natural en tu rutina diaria.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # APARTADO EXTRA 3: ALERGIAS/INTOLERANCIAS (PASO 9)
    elif current_step == 9:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(244, 67, 54, 0.3);
            border: 3px solid #F44336;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🚨 PASO 9: ALERGIAS E INTOLERANCIAS
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 9 de 12 - Información Crítica para tu Seguridad
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso9"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso9');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); color: #FFFFFF; margin-bottom: 2rem; border: 3px solid #E74C3C;">
            <h2 style="color: #FFFFFF; text-align: center; margin-bottom: 1rem;">
                🚨 PASO 9: ALERGIAS E INTOLERANCIAS
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">Información Crítica para tu Seguridad</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(75, text="Paso 9 de 12: Alergias e intolerancias (Crítico)")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.markdown("""
        ### ⚠️ Información Crítica para tu Seguridad Alimentaria
        Esta sección es **fundamental** para crear un plan alimentario seguro y adecuado para ti.
        Por favor, sé muy específico y honesto con tus respuestas.
        """)
        
        st.markdown("### ❗ 1. ¿Tienes alguna alergia alimentaria?")
        st.error("🚨 **IMPORTANTE:** Las alergias alimentarias pueden ser graves. Marca todas las que tengas, aunque sean leves.")
        st.info("💡 **Instrucción:** Debes seleccionar al menos una opción. Si no tienes alergias, selecciona 'Ninguna'.")
        alergias_alimentarias = st.multiselect(
            "Selecciona TODAS las alergias alimentarias que tienes:",
            ["Lácteos", "Huevo", "Frutos secos", "Mariscos", "Pescado", "Gluten", "Soya", "Semillas", "Ninguna"],
            key='alergias_alimentarias',
            placeholder="🔽 Selecciona si tienes alguna alergia alimentaria o marca 'Ninguna'",
            help="Incluye cualquier alergia, desde leve hasta severa. Si no tienes alergias, selecciona 'Ninguna'."
        )
        
        otra_alergia = st.text_input(
            "¿Otra alergia no mencionada? Especifica aquí:",
            value=st.session_state.get('otra_alergia', ''),
            placeholder="Ej: alergia al apio, maní, sulfitos, etc.",
            help="Especifica cualquier otra alergia alimentaria que tengas"
        )
        
        st.markdown("---")
        st.markdown("### ⚠️ 2. ¿Tienes alguna intolerancia o malestar digestivo?")
        st.warning("💡 **Ayuda:** Las intolerancias causan malestar pero no son tan graves como las alergias. Incluye cualquier alimento que te cause gases, hinchazón, dolor abdominal, etc.")
        st.info("💡 **Instrucción:** Debes seleccionar al menos una opción. Si no tienes intolerancias, selecciona 'Ninguna'.")
        intolerancias_digestivas = st.multiselect(
            "Selecciona las intolerancias o malestares digestivos que experimentas:",
            ["Lácteos con lactosa", "Leguminosas", "FODMAPs", "Gluten", "Crucíferas", "Endulzantes artificiales", "Ninguna"],
            key='intolerancias_digestivas',
            placeholder="🔽 Selecciona si tienes intolerancias digestivas o marca 'Ninguna'",
            help="Incluye alimentos que te causen malestar digestivo. Si no tienes intolerancias, selecciona 'Ninguna'."
        )
        
        otra_intolerancia = st.text_input(
            "¿Otra intolerancia no mencionada? Especifica aquí:",
            value=st.session_state.get('otra_intolerancia', ''),
            placeholder="Ej: intolerancia a la fructosa, sorbitol, etc.",
            help="Especifica cualquier otra intolerancia o malestar digestivo"
        )
        
        st.markdown("---")
        st.markdown("### ➕ 3. ¿Hay algún alimento o bebida especial que desees incluir?")
        st.info("💡 **Ayuda:** Menciona alimentos regionales, marcas específicas, preparaciones especiales o cualquier cosa importante que no aparezca en las listas anteriores.")
        alimento_adicional = st.text_area(
            "Escribe aquí alimentos o bebidas adicionales:",
            value=st.session_state.get('alimento_adicional', ''),
            placeholder="Ej: agua de jamaica casera, proteína en polvo marca X, alimentos regionales como quelites, etc.",
            help="Incluye cualquier alimento importante que no esté en las listas anteriores"
        )
        
        st.markdown("---")
        st.markdown("### 👨‍🍳 4. ¿Cuáles son tus métodos de cocción más accesibles?")
        st.info("💡 **Ayuda:** Selecciona los métodos de cocción que más usas o que tienes disponibles en tu cocina. Esto nos ayuda a sugerir recetas que puedas preparar fácilmente.")
        
        metodos_coccion_accesibles = st.multiselect(
            "Selecciona los métodos de cocción que más usas o prefieres:",
            ["🔥 A la plancha", "🔥 A la parrilla", "💧 Hervido", "♨️ Al vapor", "🔥 Horneado / al horno", 
             "💨 Air fryer (freidora de aire)", "⚡ Microondas", "🥄 Salteado (con poco aceite)"],
            key='metodos_coccion_accesibles',
            placeholder="🔽 Selecciona los métodos de cocción que usas",
            help="Incluye todos los métodos que uses regularmente o que tengas disponibles"
        )
        
        otro_metodo_coccion = st.text_input(
            "¿Otro método de cocción? Especifica aquí:",
            value=st.session_state.get('otro_metodo_coccion', ''),
            placeholder="Ej: cocina de leña, olla de presión, wok, etc.",
            help="Especifica cualquier otro método de cocción que uses"
        )

        # Guardar en session state (solo text inputs)
        st.session_state.otra_alergia = otra_alergia
        st.session_state.otra_intolerancia = otra_intolerancia
        st.session_state.alimento_adicional = alimento_adicional
        st.session_state.otro_metodo_coccion = otro_metodo_coccion
        
        # Resumen de restricciones
        alergias_count = len(st.session_state.get('alergias_alimentarias', []))
        intolerancias_count = len(st.session_state.get('intolerancias_digestivas', []))
        total_restricciones = alergias_count + intolerancias_count
        if otra_alergia:
            total_restricciones += 1
        if otra_intolerancia:
            total_restricciones += 1
            
        if total_restricciones > 0:
            st.warning(f"⚠️ **Restricciones identificadas:** {total_restricciones} restricciones alimentarias. Tu plan será cuidadosamente adaptado para evitar estos alimentos.")
        else:
            st.success("✅ **Sin restricciones:** No has reportado alergias o intolerancias. Esto nos da mayor flexibilidad para tu plan alimentario.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # APARTADO EXTRA 4: ANTOJOS (PASO 10)
    elif current_step == 10:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #673AB7 0%, #512DA8 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(103, 58, 183, 0.3);
            border: 3px solid #673AB7;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                😋 PASO 10: EVALUACIÓN DE ANTOJOS
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 10 de 12 - Información para Estrategias
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso10"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso10');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
                // Focus on the first multiselect dropdown in this step
                setTimeout(function() {
                    const firstMultiselect = window.parent.document.querySelector('[data-testid="stMultiSelect"] input');
                    if (firstMultiselect) {
                        firstMultiselect.focus();
                        firstMultiselect.click();
                    }
                }, 200);
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%); color: #FFFFFF; margin-bottom: 2rem; border: 3px solid #9B59B6;">
            <h2 style="color: #FFFFFF; text-align: center; margin-bottom: 1rem;">
                😋 PASO 10: EVALUACIÓN DE ANTOJOS
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">¡Último Paso! - Información para Estrategias</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(83, text="Paso 10 de 12: Antojos alimentarios")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🧠 ¿Por qué evaluamos tus antojos?
        Conocer tus **antojos frecuentes** nos ayuda a:
        - Crear estrategias para manejarlos de forma saludable
        - Incluir alternativas satisfactorias en tu plan
        - Desarrollar un plan realista y sostenible a largo plazo
        
        **💡 Instrucción:** Debes seleccionar al menos una opción en cualquiera de las categorías de antojos. 
        Si no tienes antojos frecuentes, selecciona 'Ninguno' en al menos una categoría.
        """)
        
        st.markdown("---")
        st.markdown("### 🍫 Antojos de alimentos dulces / postres")
        st.info("💡 **Ayuda:** Incluye cualquier dulce, postre o alimento azucarado que se te antoje frecuentemente. Si no tienes antojos dulces, selecciona 'Ninguno'.")
        antojos_dulces = st.multiselect(
            "¿Cuáles de estos alimentos dulces se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Chocolate con leche", "Chocolate amargo", "Pan dulce (conchas, donas, cuernitos)", 
             "Pastel (tres leches, chocolate, etc.)", "Galletas (Marías, Emperador, Chokis, etc.)", 
             "Helado / Nieve", "Flan / Gelatina", "Dulces tradicionales (cajeta, obleas, jamoncillo, glorias)", 
             "Cereal azucarado", "Leche condensada", "Churros", "Ninguno"],
            key='antojos_dulces',
            placeholder="🔽 Selecciona los alimentos dulces que se te antojan o marca 'Ninguno'",
            help="Incluye todos los dulces que frecuentemente deseas. Si no tienes antojos dulces, selecciona 'Ninguno'."
        )
        
        st.markdown("---")
        st.markdown("### 🧂 Antojos de alimentos salados / snacks")
        st.info("💡 **Ayuda:** Incluye botanas, frituras o alimentos salados que se te antojen. Si no tienes antojos salados, selecciona 'Ninguno'.")
        antojos_salados = st.multiselect(
            "¿Cuáles de estos alimentos salados se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Papas fritas (Sabritas, Ruffles, etc.)", "Cacahuates enchilados", "Frituras (Doritos, Cheetos, Takis, etc.)", 
             "Totopos con salsa", "Galletas saladas", "Cacahuates japoneses", "Chicharrón (de cerdo o harina)", 
             "Nachos con queso", "Queso derretido o gratinado", "Ninguno"],
            key='antojos_salados',
            placeholder="🔽 Selecciona los alimentos salados que se te antojan o marca 'Ninguno'",
            help="Incluye todas las botanas y snacks salados que frecuentemente deseas. Si no tienes antojos salados, selecciona 'Ninguno'."
        )
        
        st.markdown("---")
        st.markdown("### 🌮 Antojos de comidas rápidas / callejeras")
        st.info("💡 **Ayuda:** Incluye comida rápida, platillos callejeros o preparaciones que se te antojen. Si no tienes antojos de comida rápida, selecciona 'Ninguno'.")
        antojos_comida_rapida = st.multiselect(
            "¿Cuáles de estas comidas rápidas se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Tacos (pastor, asada, birria, etc.)", "Tortas (cubana, ahogada, etc.)", "Hamburguesas", "Hot dogs", 
             "Pizza", "Quesadillas fritas", "Tamales", "Pambazos", "Sopes / gorditas", "Elotes / esquites", 
             "Burritos", "Enchiladas", "Empanadas", "Ninguno"],
            key='antojos_comida_rapida',
            placeholder="🔽 Selecciona las comidas rápidas que se te antojan o marca 'Ninguno'",
            help="Incluye toda la comida rápida o callejera que frecuentemente deseas. Si no tienes antojos de comida rápida, selecciona 'Ninguno'."
        )
        
        st.markdown("---")
        st.markdown("### 🍹 Antojos de bebidas y postres líquidos")
        st.info("💡 **Ayuda:** Incluye bebidas azucaradas, alcohólicas o postres líquidos que se te antojen. Si no tienes antojos de bebidas, selecciona 'Ninguno'.")
        antojos_bebidas = st.multiselect(
            "¿Cuáles de estas bebidas se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Refrescos regulares (Coca-Cola, Fanta, etc.)", "Jugos industrializados (Boing, Jumex, etc.)", 
             "Malteadas / Frappés", "Agua de sabor con azúcar (jamaica, horchata, tamarindo)", 
             "Café con azúcar y leche", "Champurrado / atole", "Licuado de plátano con azúcar", 
             "Bebidas alcohólicas (cerveza, tequila, vino, etc.)", "Ninguno"],
            key='antojos_bebidas',
            placeholder="🔽 Selecciona las bebidas que se te antojan o marca 'Ninguno'",
            help="Incluye todas las bebidas con calorías que frecuentemente deseas. Si no tienes antojos de bebidas, selecciona 'Ninguno'."
        )
        
        st.markdown("---")
        st.markdown("### 🔥 Antojos de alimentos con condimentos estimulantes")
        st.info("💡 **Ayuda:** Incluye alimentos picantes, con chile o condimentos intensos que se te antojen. Si no tienes antojos picantes, selecciona 'Ninguno'.")
        antojos_picantes = st.multiselect(
            "¿Cuáles de estos alimentos picantes se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Chiles en escabeche", "Salsas picantes", "Salsa Valentina, Tajín o Chamoy", 
             "Pepinos con chile y limón", "Mangos verdes con chile", "Gomitas enchiladas", 
             "Fruta con Miguelito o chile en polvo", "Ninguno"],
            key='antojos_picantes',
            placeholder="🔽 Selecciona los alimentos picantes que se te antojan o marca 'Ninguno'",
            help="Incluye todos los alimentos con chile o condimentos estimulantes que deseas. Si no tienes antojos picantes, selecciona 'Ninguno'."
        )
        
        st.markdown("---")
        st.markdown("### ❓ Otros antojos no mencionados")
        st.info("💡 **Ayuda:** Especifica cualquier otro antojo que no aparezca en las listas anteriores.")
        otros_antojos = st.text_area(
            "¿Qué otros alimentos o preparaciones se te antojan mucho?",
            value=st.session_state.get('otros_antojos', ''),
            placeholder="Ej: palomitas con mantequilla, raspados, gelatinas comerciales, etc.",
            help="Describe cualquier otro antojo que no esté en las listas anteriores"
        )

        # Guardar en session state (solo text input)
        st.session_state.otros_antojos = otros_antojos
        
        # Análisis de antojos
        antojos_dulces_count = len(st.session_state.get('antojos_dulces', []))
        antojos_salados_count = len(st.session_state.get('antojos_salados', []))
        antojos_comida_rapida_count = len(st.session_state.get('antojos_comida_rapida', []))
        antojos_bebidas_count = len(st.session_state.get('antojos_bebidas', []))
        antojos_picantes_count = len(st.session_state.get('antojos_picantes', []))
        
        total_antojos = (antojos_dulces_count + antojos_salados_count + 
                        antojos_comida_rapida_count + antojos_bebidas_count + antojos_picantes_count)
        
        if total_antojos >= 15:
            st.warning(f"⚠️ **Muchos antojos identificados:** {total_antojos} tipos de antojos. Será importante desarrollar estrategias específicas de manejo.")
        elif total_antojos >= 8:
            st.info(f"ℹ️ **Antojos moderados:** {total_antojos} tipos de antojos. Incluiremos alternativas saludables en tu plan.")
        elif total_antojos >= 3:
            st.success(f"✅ **Pocos antojos:** {total_antojos} tipos de antojos. Esto facilitará mantener un plan alimentario saludable.")
        elif total_antojos > 0:
            st.success(f"✅ **Muy pocos antojos:** Solo {total_antojos} tipos. Tu autocontrol alimentario parece ser muy bueno.")
        else:
            st.success("🎉 **Sin antojos frecuentes:** Excelente autocontrol alimentario. Esto será una gran ventaja para tu plan.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # PASO 11: FRECUENCIA DE COMIDAS
    elif current_step == 11:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3);
            border: 3px solid #FF9800;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                🍽️ PASO 11: FRECUENCIA DE COMIDAS PREFERIDA
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                Estás en el paso 11 de 12 - Adaptación a tu Estilo de Vida
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso11"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso11');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(92, text="Paso 11 de 12: Frecuencia de comidas preferida")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ¿Cuál es tu frecuencia de comidas ideal?
        Queremos conocer la **frecuencia de comidas** que mejor se adapta a tu agenda diaria y estilo de vida.
        Esto nos ayudará a estructurar tu plan alimentario de manera que sea práctico y sostenible para ti.
        
        **💡 Instrucción:** Selecciona la opción que mejor describa tu rutina alimentaria preferida o más realista para tu día a día.
        """)
        
        st.info("💡 **Ayuda:** Piensa en tu horario de trabajo, actividades y preferencias personales para elegir la frecuencia más conveniente.")
        
        frecuencia_comidas = st.radio(
            "¿Cuál es la frecuencia de comidas que mejor se adapta a tu agenda diaria?",
            [
                "Desayuno, comida y cena (3 comidas principales)",
                "Desayuno, comida, cena y una colación",
                "Desayuno, comida, cena y dos colaciones", 
                "Solo dos comidas principales al día",
                "Otro (especificar)"
            ],
            key='frecuencia_comidas',
            help="Selecciona la estructura de comidas que mejor se ajuste a tu rutina diaria"
        )
        
        # Campo adicional si selecciona "Otro"
        otra_frecuencia = ""
        if frecuencia_comidas == "Otro (especificar)":
            otra_frecuencia = st.text_input(
                "Especifica tu frecuencia de comidas preferida:",
                value=st.session_state.get('otra_frecuencia', ''),
                placeholder="Ej: Ayuno intermitente 16:8, una comida al día, 5 comidas pequeñas, etc.",
                help="Describe tu rutina alimentaria ideal con el mayor detalle posible"
            )
            st.session_state.otra_frecuencia = otra_frecuencia
        
        # Resumen de la selección
        if frecuencia_comidas:
            if frecuencia_comidas == "Otro (especificar)" and otra_frecuencia:
                st.success(f"✅ **Frecuencia seleccionada:** {otra_frecuencia}")
            elif frecuencia_comidas != "Otro (especificar)":
                st.success(f"✅ **Frecuencia seleccionada:** {frecuencia_comidas}")
            
            # Información adicional según la selección
            if "3 comidas principales" in frecuencia_comidas:
                st.info("🍽️ **Estructura clásica:** Ideal para horarios regulares y control de porciones.")
            elif "una colación" in frecuencia_comidas:
                st.info("🥪 **Con una colación:** Excelente para mantener energía estable durante el día.")
            elif "dos colaciones" in frecuencia_comidas:
                st.info("🍎 **Con dos colaciones:** Perfecta para personas con horarios largos o alta actividad física.")
            elif "dos comidas principales" in frecuencia_comidas:
                st.info("⏰ **Ayuno intermitente:** Ideal para quienes prefieren ventanas de alimentación más concentradas.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("Siguiente ➡️"):
                advance_to_next_step()

    # PASO 12: SUGERENCIAS DE MENÚS
    elif current_step == 12:
        # Add prominent visual step indicator
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
            border: 3px solid #4CAF50;
            animation: slideIn 0.5s ease-out;
        ">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: bold; color: white;">
                📝 PASO 12: SUGERENCIAS DE MENÚS
            </h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; color: white;">
                ¡Último Paso! Estás en el paso 12 de 12 - Personalización Final
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add unique HTML marker for this step
        st.markdown("""
        <div id="paso12"></div>
        <script>
        // Auto-scroll to this step's marker and focus on first input for better UX
        setTimeout(function() {
            const stepElement = window.parent.document.getElementById('paso12');
            if (stepElement) {
                stepElement.scrollIntoView({behavior: 'smooth'});
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(100, text="Paso 12 de 12: Sugerencias de menús - ¡Último paso!")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 💭 Sugerencias de Menús y Preferencias Adicionales
        Para finalizar tu evaluación, nos gustaría conocer si tienes **sugerencias específicas de menús** que te gustaría que adaptemos a tu plan nutricional, o si prefieres que nuestro equipo de nutrición se encargue de crear las propuestas basándose en toda la información que has proporcionado.
        
        **💡 Instrucción:** Puedes escribir menús específicos, platos favoritos, recetas que te gustan, o simplemente indicar que confías en nuestro criterio profesional.
        """)
        
        st.info("💡 **Ayuda:** Puedes mencionar platos específicos, combinaciones que te gustan, recetas familiares, o cualquier idea que tengas. También puedes dejar que nuestro equipo decida completamente.")
        
        sugerencias_menus = st.text_area(
            "¿Tienes alguna sugerencia de menús que quisieras que adaptemos, o prefieres que el equipo decida por ti?",
            value=st.session_state.get('sugerencias_menus', ''),
            placeholder="""Ejemplos:
- Me gustan los desayunos con avena y frutas
- Prefiero pollo a la plancha con verduras para la cena
- Me encantan las ensaladas coloridas para el almuerzo
- Que el equipo decida completamente basándose en mi evaluación
- Quiero incluir comida mexicana tradicional saludable
- Prefiero menús sencillos y fáciles de preparar""",
            height=120,
            help="Escribe todas las ideas, preferencias o sugerencias que tengas, o indica si prefieres que decidamos nosotros"
        )
        
        # Guardar en session state
        st.session_state.sugerencias_menus = sugerencias_menus
        
        # Opciones predefinidas rápidas
        st.markdown("### 🎯 Opciones Rápidas (Opcional)")
        st.markdown("Si no sabes qué escribir, puedes seleccionar una de estas opciones:")
        
        opcion_rapida = st.selectbox(
            "Selecciona una opción si no tienes sugerencias específicas:",
            [
                "Seleccionar...",
                "Que el equipo decida completamente por mí",
                "Prefiero comida mexicana saludable",
                "Quiero menús sencillos y fáciles de preparar", 
                "Me gusta variar mucho los sabores",
                "Prefiero preparaciones al vapor y a la plancha",
                "Quiero incluir más recetas internacionales saludables"
            ],
            key='opcion_rapida_menu',
            help="Estas son opciones generales que puedes usar si no tienes ideas específicas"
        )
        
        # Auto-llenar si selecciona una opción rápida
        if opcion_rapida and opcion_rapida != "Seleccionar..." and not sugerencias_menus:
            st.session_state.sugerencias_menus = opcion_rapida
            st.rerun()
        
        # Mostrar resumen de la entrada
        if sugerencias_menus:
            palabra_count = len(sugerencias_menus.split())
            if palabra_count > 0:
                st.success(f"✅ **Sugerencias recibidas:** {palabra_count} palabras. Excelente, esto nos ayudará mucho a personalizar tu plan.")
            
            # Análisis rápido del contenido
            if "equipo decida" in sugerencias_menus.lower() or "decidan por mí" in sugerencias_menus.lower():
                st.info("👨‍🍳 **Perfecto:** Nuestro equipo de nutrición creará menús completamente personalizados basándose en toda tu evaluación.")
            elif len(sugerencias_menus) > 50:
                st.info("📝 **Excelente:** Has proporcionado sugerencias detalladas que nos ayudarán a crear un plan muy específico para ti.")
            else:
                st.info("💡 **Recibido:** Tus preferencias han sido registradas y las consideraremos en tu plan personalizado.")
        else:
            st.info("ℹ️ **Nota:** Si no escribes nada, nuestro equipo creará menús basándose en todos los alimentos que seleccionaste en los pasos anteriores.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de navegación - En el último paso solo mostrar anterior y finalizar
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior"):
                go_to_previous_step()
        with col3:
            if st.button("🎉 Finalizar Evaluación"):
                st.success("🎊 ¡Felicitaciones! Has completado toda la evaluación de patrones alimentarios.")
                st.balloons()
                # Marcar este paso como completado
                st.session_state.step_completed[12] = True

    # RESULTADO FINAL: Análisis completo del nuevo cuestionario
    with st.expander("📈 **RESULTADO FINAL: Tu Perfil Alimentario Completo**", expanded=False):
        progress.progress(100, text="Análisis completo: Generando tu perfil alimentario personalizado")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.markdown("### 🎯 Tu Perfil Alimentario Personalizado")
        
        # Crear resumen del perfil por grupos actuales
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Información Personal")
            st.write(f"• **Nombre:** {st.session_state.get('nombre', 'No especificado')}")
            st.write(f"• **Edad:** {st.session_state.get('edad', 'No especificado')} años")
            st.write(f"• **Sexo:** {st.session_state.get('sexo', 'No especificado')}")
            st.write(f"• **Fecha evaluación:** {st.session_state.get('fecha_llenado', 'No especificado')}")
            
            st.markdown("#### 🥩 Grupo 1: Proteínas Grasas")
            total_proteinas_grasas = len(st.session_state.get('huevos_embutidos', [])) + len(st.session_state.get('carnes_res_grasas', [])) + len(st.session_state.get('carnes_cerdo_grasas', [])) + len(st.session_state.get('carnes_pollo_grasas', [])) + len(st.session_state.get('organos_grasos', [])) + len(st.session_state.get('quesos_grasos', [])) + len(st.session_state.get('lacteos_enteros', [])) + len(st.session_state.get('pescados_grasos', [])) + len(st.session_state.get('mariscos_grasos', []))
            st.write(f"• **Total alimentos seleccionados:** {total_proteinas_grasas}")
            if st.session_state.get('huevos_embutidos'):
                st.write(f"• **Huevos/embutidos:** {len(st.session_state.get('huevos_embutidos', []))}")
            if st.session_state.get('carnes_res_grasas'):
                st.write(f"• **Carnes de res grasas:** {len(st.session_state.get('carnes_res_grasas', []))}")
            if st.session_state.get('carnes_cerdo_grasas'):
                st.write(f"• **Carnes de cerdo grasas:** {len(st.session_state.get('carnes_cerdo_grasas', []))}")
            if st.session_state.get('carnes_pollo_grasas'):
                st.write(f"• **Carnes de pollo/pavo grasas:** {len(st.session_state.get('carnes_pollo_grasas', []))}")
            
            st.markdown("#### 🍗 Grupo 2: Proteínas Magras")
            total_proteinas_magras = len(st.session_state.get('carnes_res_magras', [])) + len(st.session_state.get('carnes_cerdo_magras', [])) + len(st.session_state.get('carnes_pollo_magras', [])) + len(st.session_state.get('organos_magros', [])) + len(st.session_state.get('pescados_magros', [])) + len(st.session_state.get('mariscos_magros', [])) + len(st.session_state.get('quesos_magros', [])) + len(st.session_state.get('lacteos_light', [])) + len(st.session_state.get('huevos_embutidos_light', []))
            st.write(f"• **Total alimentos seleccionados:** {total_proteinas_magras}")
            if st.session_state.get('carnes_res_magras'):
                st.write(f"• **Carnes de res magras:** {len(st.session_state.get('carnes_res_magras', []))}")
            if st.session_state.get('pescados_magros'):
                st.write(f"• **Pescados magros:** {len(st.session_state.get('pescados_magros', []))}")
        
        with col2:
            st.markdown("#### 🥑 Grupo 3: Grasas Saludables")
            total_grasas = len(st.session_state.get('grasas_naturales', [])) + len(st.session_state.get('frutos_secos_semillas', [])) + len(st.session_state.get('mantequillas_vegetales', []))
            st.write(f"• **Total alimentos seleccionados:** {total_grasas}")
            if st.session_state.get('grasas_naturales'):
                st.write(f"• **Grasas naturales:** {len(st.session_state.get('grasas_naturales', []))}")
            if st.session_state.get('frutos_secos_semillas'):
                st.write(f"• **Frutos secos/semillas:** {len(st.session_state.get('frutos_secos_semillas', []))}")
            
            st.markdown("#### 🍞 Grupo 4: Carbohidratos")
            total_carbohidratos = len(st.session_state.get('cereales_integrales', [])) + len(st.session_state.get('pastas', [])) + len(st.session_state.get('tortillas_panes', [])) + len(st.session_state.get('raices_tuberculos', [])) + len(st.session_state.get('leguminosas', []))
            st.write(f"• **Total alimentos seleccionados:** {total_carbohidratos}")
            if st.session_state.get('cereales_integrales'):
                st.write(f"• **Cereales:** {len(st.session_state.get('cereales_integrales', []))}")
            if st.session_state.get('tortillas_panes'):
                st.write(f"• **Tortillas/panes:** {len(st.session_state.get('tortillas_panes', []))}")
            
            st.markdown("#### 🥬 Grupos 5 y 6: Vegetales y Frutas")
            st.write(f"• **Vegetales:** {len(st.session_state.get('vegetales_lista', []))} seleccionados")
            st.write(f"• **Frutas:** {len(st.session_state.get('frutas_lista', []))} seleccionadas")
        
        # Sección de información adicional
        st.markdown("### 🍳 Información Adicional")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🧈 Aceites de Cocción")
            if st.session_state.get('aceites_coccion'):
                st.write(f"• **Aceites preferidos:** {len(st.session_state.get('aceites_coccion', []))} seleccionados")
                aceites_top = st.session_state.get('aceites_coccion', [])[:3]
                for aceite in aceites_top:
                    st.write(f"  - {aceite}")
            
            st.markdown("#### 🥤 Bebidas Sin Calorías")
            if st.session_state.get('bebidas_sin_calorias'):
                st.write(f"• **Bebidas preferidas:** {len(st.session_state.get('bebidas_sin_calorias', []))} seleccionadas")
                bebidas_top = st.session_state.get('bebidas_sin_calorias', [])[:3]
                for bebida in bebidas_top:
                    st.write(f"  - {bebida}")
        
        with col2:
            st.markdown("#### 👨‍🍳 Métodos de Cocción")
            if st.session_state.get('metodos_coccion_accesibles'):
                st.write(f"• **Métodos preferidos:** {len(st.session_state.get('metodos_coccion_accesibles', []))} seleccionados")
                metodos_top = st.session_state.get('metodos_coccion_accesibles', [])[:3]
                for metodo in metodos_top:
                    st.write(f"  - {metodo}")
            
            if st.session_state.get('otro_metodo_coccion'):
                st.write(f"• **Otro método:** {st.session_state.get('otro_metodo_coccion', 'No especificado')}")

        # Restricciones importantes
        if st.session_state.get('alergias_alimentarias') or st.session_state.get('intolerancias_digestivas'):
            st.markdown("### ⚠️ Restricciones Importantes")
            if st.session_state.get('alergias_alimentarias'):
                st.warning(f"**Alergias alimentarias:** {', '.join(st.session_state.get('alergias_alimentarias', []))}")
                if st.session_state.get('otra_alergia'):
                    st.write(f"• **Otra alergia:** {st.session_state.get('otra_alergia')}")
            
            if st.session_state.get('intolerancias_digestivas'):
                st.info(f"**Intolerancias digestivas:** {', '.join(st.session_state.get('intolerancias_digestivas', []))}")
                if st.session_state.get('otra_intolerancia'):
                    st.write(f"• **Otra intolerancia:** {st.session_state.get('otra_intolerancia')}")

        # Antojos alimentarios
        st.markdown("### 😋 Patrones de Antojos Alimentarios")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.get('antojos_dulces'):
                st.write(f"• **Antojos dulces:** {len(st.session_state.get('antojos_dulces', []))} tipos")
            if st.session_state.get('antojos_salados'):
                st.write(f"• **Antojos salados:** {len(st.session_state.get('antojos_salados', []))} tipos")
            if st.session_state.get('antojos_comida_rapida'):
                st.write(f"• **Comida rápida:** {len(st.session_state.get('antojos_comida_rapida', []))} tipos")
        
        with col2:
            if st.session_state.get('antojos_bebidas'):
                st.write(f"• **Bebidas con calorías:** {len(st.session_state.get('antojos_bebidas', []))} tipos")
            if st.session_state.get('antojos_picantes'):
                st.write(f"• **Condimentos picantes:** {len(st.session_state.get('antojos_picantes', []))} tipos")
            if st.session_state.get('otros_antojos'):
                st.write(f"• **Otros antojos especificados:** Sí")

        # Información adicional especificada
        if st.session_state.get('alimento_adicional'):
            st.markdown("### ➕ Alimentos Adicionales Especificados")
            st.info(f"**Alimentos mencionados:** {st.session_state.get('alimento_adicional', 'No especificado')}")

        # Información de frecuencia de comidas
        if st.session_state.get('frecuencia_comidas'):
            st.markdown("### 🍽️ Frecuencia de Comidas Preferida")
            frecuencia = st.session_state.get('frecuencia_comidas', 'No especificado')
            if frecuencia == "Otro (especificar)" and st.session_state.get('otra_frecuencia'):
                st.info(f"**Frecuencia personalizada:** {st.session_state.get('otra_frecuencia')}")
            else:
                st.info(f"**Frecuencia seleccionada:** {frecuencia}")

        # Sugerencias de menús
        if st.session_state.get('sugerencias_menus'):
            st.markdown("### 📝 Sugerencias de Menús")
            sugerencias = st.session_state.get('sugerencias_menus', '')
            palabra_count = len(sugerencias.split()) if sugerencias else 0
            st.info(f"**Sugerencias del cliente:** {sugerencias[:200]}{'...' if len(sugerencias) > 200 else ''}")
            if palabra_count > 0:
                st.success(f"**Detalle:** {palabra_count} palabras de sugerencias específicas proporcionadas")

        # Recomendaciones personalizadas basadas en datos reales
        st.markdown("### 💡 Recomendaciones Personalizadas Iniciales")
        
        # Análisis básico basado en las respuestas actuales
        recomendaciones = []
        
        # Verificar diversidad de alimentos por grupo
        total_grupos_completos = 0
        if len(st.session_state.get('huevos_embutidos', [])) + len(st.session_state.get('carnes_res_grasas', [])) > 0:
            total_grupos_completos += 1
        if len(st.session_state.get('carnes_res_magras', [])) + len(st.session_state.get('pescados_magros', [])) > 0:
            total_grupos_completos += 1
        if len(st.session_state.get('grasas_naturales', [])) + len(st.session_state.get('frutos_secos_semillas', [])) > 0:
            total_grupos_completos += 1
        if len(st.session_state.get('cereales_integrales', [])) + len(st.session_state.get('pastas', [])) + len(st.session_state.get('tortillas_panes', [])) > 0:
            total_grupos_completos += 1
        if len(st.session_state.get('vegetales_lista', [])) > 5:
            total_grupos_completos += 1
        if len(st.session_state.get('frutas_lista', [])) > 5:
            total_grupos_completos += 1
        
        if total_grupos_completos >= 5:
            recomendaciones.append("✅ **Diversidad nutricional excelente:** Tienes una buena variedad de alimentos en la mayoría de grupos alimentarios.")
        elif total_grupos_completos >= 3:
            recomendaciones.append("🔄 **Diversidad nutricional moderada:** Considera ampliar la variedad en algunos grupos alimentarios.")
        else:
            recomendaciones.append("📈 **Oportunidad de mejora:** Ampliar la variedad de alimentos puede enriquecer tu plan nutricional.")
        
        # Verificar métodos de cocción
        if len(st.session_state.get('metodos_coccion_accesibles', [])) >= 4:
            recomendaciones.append("👨‍🍳 **Versatilidad culinaria:** Tienes múltiples métodos de cocción disponibles, ideal para variedad en preparaciones.")
        elif len(st.session_state.get('metodos_coccion_accesibles', [])) >= 2:
            recomendaciones.append("🔧 **Métodos básicos:** Con tus métodos de cocción actuales puedes crear preparaciones nutritivas y variadas.")
        
        # Verificar restricciones
        if st.session_state.get('alergias_alimentarias') or st.session_state.get('intolerancias_digestivas'):
            recomendaciones.append("⚠️ **Plan especializado:** Tus restricciones alimentarias requerirán un plan personalizado cuidadoso.")
        
        # Verificar antojos
        total_antojos = len(st.session_state.get('antojos_dulces', [])) + len(st.session_state.get('antojos_salados', [])) + len(st.session_state.get('antojos_comida_rapida', []))
        if total_antojos > 10:
            recomendaciones.append("🧠 **Manejo de antojos:** Se recomienda desarrollar estrategias específicas para controlar los antojos identificados.")
        elif total_antojos > 5:
            recomendaciones.append("⚖️ **Equilibrio:** Incluir alternativas saludables para satisfacer antojos ocasionales.")
        
        if not recomendaciones:
            recomendaciones.append("📋 **Perfil base establecido:** Se requiere más información para recomendaciones específicas.")
        
        for i, rec in enumerate(recomendaciones, 1):
            st.write(f"{i}. {rec}")

        st.success(f"""
        ### ✅ Análisis de patrones alimentarios completado exitosamente
        
        **Tu perfil nutricional personalizado está listo** y incluye información detallada sobre:
        - 6 grupos alimentarios principales evaluados
        - Métodos de cocción disponibles y preferidos  
        - Restricciones, alergias e intolerancias específicas
        - Patrones de antojos alimentarios identificados
        - Aceites de cocción y bebidas sin calorías preferidas
        
        **Este análisis integral permitirá crear un plan nutricional completamente adaptado** 
        a tus gustos, tolerancias y necesidades específicas.
        
        La información será enviada a nuestro equipo de nutrición para desarrollar tu plan personalizado.
        """)

        st.markdown('</div>', unsafe_allow_html=True)

# Construir resumen completo para email
def crear_resumen_email():
    resumen = f"""
=====================================
CUESTIONARIO DE SELECCIÓN ALIMENTARIA PERSONALIZADA - MUPAI
=====================================
Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Sistema: MUPAI v2.0 - Muscle Up Performance Assessment Intelligence

=====================================
DATOS DEL CLIENTE:
=====================================
- Nombre completo: {st.session_state.get('nombre', 'No especificado')}
- Edad: {st.session_state.get('edad', 'No especificado')} años
- Sexo: {st.session_state.get('sexo', 'No especificado')}
- Teléfono: {st.session_state.get('telefono', 'No especificado')}
- Email: {st.session_state.get('email_cliente', 'No especificado')}
- Fecha evaluación: {st.session_state.get('fecha_llenado', 'No especificado')}

=====================================
🥩 GRUPO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO
=====================================
🍳 Huevos y embutidos:
- {', '.join(st.session_state.get('huevos_embutidos', [])) if st.session_state.get('huevos_embutidos') else 'No especificado'}

🐄 Carnes de res grasas:
- {', '.join(st.session_state.get('carnes_res_grasas', [])) if st.session_state.get('carnes_res_grasas') else 'No especificado'}

🐷 Carnes de cerdo grasas:
- {', '.join(st.session_state.get('carnes_cerdo_grasas', [])) if st.session_state.get('carnes_cerdo_grasas') else 'No especificado'}

🐔 Carnes de pollo/pavo grasas:
- {', '.join(st.session_state.get('carnes_pollo_grasas', [])) if st.session_state.get('carnes_pollo_grasas') else 'No especificado'}

🫀 Órganos y vísceras grasas:
- {', '.join(st.session_state.get('organos_grasos', [])) if st.session_state.get('organos_grasos') else 'No especificado'}

🐟 Pescados grasos:
- {', '.join(st.session_state.get('pescados_grasos', [])) if st.session_state.get('pescados_grasos') else 'No especificado'}

🦐 Mariscos/comida marina grasos:
- {', '.join(st.session_state.get('mariscos_grasos', [])) if st.session_state.get('mariscos_grasos') else 'No especificado'}

🧀 Quesos altos en grasa:
- {', '.join(st.session_state.get('quesos_grasos', [])) if st.session_state.get('quesos_grasos') else 'No especificado'}

🥛 Lácteos enteros:
- {', '.join(st.session_state.get('lacteos_enteros', [])) if st.session_state.get('lacteos_enteros') else 'No especificado'}

🐟 Pescados grasos:
- {', '.join(st.session_state.get('pescados_grasos', [])) if st.session_state.get('pescados_grasos') else 'No especificado'}

=====================================
🍗 GRUPO 2: PROTEÍNA ANIMAL MAGRA
=====================================
🐄 Carnes de res magras:
- {', '.join(st.session_state.get('carnes_res_magras', [])) if st.session_state.get('carnes_res_magras') else 'No especificado'}

🐷 Carnes de cerdo magras:
- {', '.join(st.session_state.get('carnes_cerdo_magras', [])) if st.session_state.get('carnes_cerdo_magras') else 'No especificado'}

🐔 Carnes de pollo/pavo magras:
- {', '.join(st.session_state.get('carnes_pollo_magras', [])) if st.session_state.get('carnes_pollo_magras') else 'No especificado'}

🫀 Órganos y vísceras magros:
- {', '.join(st.session_state.get('organos_magros', [])) if st.session_state.get('organos_magros') else 'No especificado'}

🐟 Pescados magros:
- {', '.join(st.session_state.get('pescados_magros', [])) if st.session_state.get('pescados_magros') else 'No especificado'}

🦐 Mariscos/comida marina magros:
- {', '.join(st.session_state.get('mariscos_magros', [])) if st.session_state.get('mariscos_magros') else 'No especificado'}

🧀 Quesos magros:
- {', '.join(st.session_state.get('quesos_magros', [])) if st.session_state.get('quesos_magros') else 'No especificado'}

🥛 Lácteos light o reducidos:
- {', '.join(st.session_state.get('lacteos_light', [])) if st.session_state.get('lacteos_light') else 'No especificado'}

🥚 Huevos y embutidos light:
- {', '.join(st.session_state.get('huevos_embutidos_light', [])) if st.session_state.get('huevos_embutidos_light') else 'No especificado'}

=====================================
🥑 GRUPO 3: FUENTES DE GRASA SALUDABLE
=====================================
🥑 Grasas naturales de alimentos:
- {', '.join(st.session_state.get('grasas_naturales', [])) if st.session_state.get('grasas_naturales') else 'No especificado'}

🌰 Frutos secos y semillas:
- {', '.join(st.session_state.get('frutos_secos_semillas', [])) if st.session_state.get('frutos_secos_semillas') else 'No especificado'}

🧈 Mantequillas y pastas vegetales:
- {', '.join(st.session_state.get('mantequillas_vegetales', [])) if st.session_state.get('mantequillas_vegetales') else 'No especificado'}

=====================================
🍞 GRUPO 4: CARBOHIDRATOS COMPLEJOS Y CEREALES
=====================================
🌾 Cereales y granos integrales:
- {', '.join(st.session_state.get('cereales_integrales', [])) if st.session_state.get('cereales_integrales') else 'No especificado'}

🍝 Pastas:
- {', '.join(st.session_state.get('pastas', [])) if st.session_state.get('pastas') else 'No especificado'}

🌽 Tortillas y panes:
- {', '.join(st.session_state.get('tortillas_panes', [])) if st.session_state.get('tortillas_panes') else 'No especificado'}

🥔 Raíces y tubérculos (forma base):
- {', '.join(st.session_state.get('raices_tuberculos', [])) if st.session_state.get('raices_tuberculos') else 'No especificado'}

🫘 Leguminosas:
- {', '.join(st.session_state.get('leguminosas', [])) if st.session_state.get('leguminosas') else 'No especificado'}

=====================================
🥬 GRUPO 5: VEGETALES
=====================================
- {', '.join(st.session_state.get('vegetales_lista', [])) if st.session_state.get('vegetales_lista') else 'No especificado'}

=====================================
🍎 GRUPO 6: FRUTAS
=====================================
- {', '.join(st.session_state.get('frutas_lista', [])) if st.session_state.get('frutas_lista') else 'No especificado'}

=====================================
🍳 APARTADO EXTRA: GRASA/ACEITE DE COCCIÓN FAVORITA
=====================================
- {', '.join(st.session_state.get('aceites_coccion', [])) if st.session_state.get('aceites_coccion') else 'No especificado'}

=====================================
🥤 BEBIDAS SIN CALORÍAS PARA HIDRATACIÓN
=====================================
- {', '.join(st.session_state.get('bebidas_sin_calorias', [])) if st.session_state.get('bebidas_sin_calorias') else 'No especificado'}

=====================================
🚨 SECCIÓN FINAL: ALERGIAS, INTOLERANCIAS Y PREFERENCIAS
=====================================
❗ 1. Alergias alimentarias:
- {', '.join(st.session_state.get('alergias_alimentarias', [])) if st.session_state.get('alergias_alimentarias') else 'No especificado'}
- Otra alergia especificada: {st.session_state.get('otra_alergia', 'No especificado')}

⚠️ 2. Intolerancias o malestar digestivo:
- {', '.join(st.session_state.get('intolerancias_digestivas', [])) if st.session_state.get('intolerancias_digestivas') else 'No especificado'}
- Otra intolerancia especificada: {st.session_state.get('otra_intolerancia', 'No especificado')}

➕ 3. Alimentos o bebidas adicionales deseados:
- {st.session_state.get('alimento_adicional', 'No especificado')}

➕ 4. Métodos de cocción más accesibles para el día a día:
- {', '.join(st.session_state.get('metodos_coccion_accesibles', [])) if st.session_state.get('metodos_coccion_accesibles') else 'No especificado'}
- Otro método especificado: {st.session_state.get('otro_metodo_coccion', 'No especificado')}

=====================================
😋 SECCIÓN DE ANTOJOS ALIMENTARIOS
=====================================
🍫 Alimentos dulces / postres:
- {', '.join(st.session_state.get('antojos_dulces', [])) if st.session_state.get('antojos_dulces') else 'No especificado'}

🧂 Alimentos salados / snacks:
- {', '.join(st.session_state.get('antojos_salados', [])) if st.session_state.get('antojos_salados') else 'No especificado'}

🌮 Comidas rápidas / callejeras:
- {', '.join(st.session_state.get('antojos_comida_rapida', [])) if st.session_state.get('antojos_comida_rapida') else 'No especificado'}

🍹 Bebidas y postres líquidos:
- {', '.join(st.session_state.get('antojos_bebidas', [])) if st.session_state.get('antojos_bebidas') else 'No especificado'}

🔥 Alimentos con condimentos estimulantes:
- {', '.join(st.session_state.get('antojos_picantes', [])) if st.session_state.get('antojos_picantes') else 'No especificado'}

❓ Otros antojos especificados:
- {st.session_state.get('otros_antojos', 'No especificado')}

=====================================
🍽️ FRECUENCIA DE COMIDAS PREFERIDA
=====================================
- Frecuencia seleccionada: {st.session_state.get('frecuencia_comidas', 'No especificado')}
- Especificación adicional: {st.session_state.get('otra_frecuencia', 'No especificado')}

=====================================
📝 SUGERENCIAS DE MENÚS Y PREFERENCIAS
=====================================
- Sugerencias del cliente: {st.session_state.get('sugerencias_menus', 'No especificado')}
- Opción rápida seleccionada: {st.session_state.get('opcion_rapida_menu', 'No especificado')}

=====================================
RESUMEN DE ANÁLISIS IDENTIFICADO:
=====================================
Este cuestionario completo de patrones alimentarios proporciona una base integral 
para el desarrollo de recomendaciones nutricionales altamente personalizadas basadas en:

1. 6 grupos alimentarios principales evaluados
2. Métodos de cocción disponibles y preferidos
3. Restricciones específicas (alergias e intolerancias)  
4. Patrones de preferencias detallados
5. Análisis de antojos y alimentación emocional
6. Frecuencia de comidas preferida del cliente
7. Sugerencias específicas de menús y preferencias adicionales
8. Contexto personal, familiar y social completo

RECOMENDACIONES PARA SEGUIMIENTO:
- Desarrollar plan nutricional personalizado basado en estos patrones
- Considerar restricciones y alergias como prioridad absoluta
- Aprovechar métodos de cocción preferidos y disponibles
- Integrar estrategias para manejo de antojos identificados
- Estructurar la frecuencia de comidas según la preferencia del cliente
- Incorporar sugerencias específicas de menús proporcionadas por el cliente
- Adaptar recomendaciones al contexto personal y familiar específico

=====================================
© 2025 MUPAI - Muscle up GYM
Alimentary Pattern Assessment Intelligence
=====================================
"""
    return resumen

# RESUMEN FINAL Y ENVÍO DE EMAIL
st.markdown("---")
st.markdown('<div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E;">', unsafe_allow_html=True)
st.markdown("## 🎯 **Resumen Final de tu Evaluación de Patrones Alimentarios**")
st.markdown(f"*Fecha: {st.session_state.get('fecha_llenado', 'No especificado')} | Cliente: {st.session_state.get('nombre', 'No especificado')}*")

# Mostrar métricas finales basadas en los datos reales del formulario
col1, col2, col3 = st.columns(3)
with col1:
    total_alimentos_grupo1 = len(st.session_state.get('huevos_embutidos', [])) + len(st.session_state.get('carnes_res_grasas', [])) + len(st.session_state.get('quesos_grasos', []))
    total_alimentos_grupo2 = len(st.session_state.get('carnes_res_magras', [])) + len(st.session_state.get('pescados_magros', [])) + len(st.session_state.get('quesos_magros', []))
    st.markdown(f"""
    ### 🥩 Proteínas
    - **Grupo 1 (grasas):** {total_alimentos_grupo1} alimentos
    - **Grupo 2 (magras):** {total_alimentos_grupo2} alimentos
    - **Restricciones:** {'Sí' if st.session_state.get('alergias_alimentarias') or st.session_state.get('intolerancias_digestivas') else 'No'}
    """)

with col2:
    total_grasas = len(st.session_state.get('grasas_naturales', [])) + len(st.session_state.get('frutos_secos_semillas', []))
    total_carbohidratos = len(st.session_state.get('cereales_integrales', [])) + len(st.session_state.get('pastas', [])) + len(st.session_state.get('tortillas_panes', []))
    st.markdown(f"""
    ### 🥑 Macronutrientes  
    - **Grasas saludables:** {total_grasas} alimentos
    - **Carbohidratos:** {total_carbohidratos} alimentos
    - **Vegetales:** {len(st.session_state.get('vegetales_lista', []))} seleccionados
    """)

with col3:
    total_antojos = len(st.session_state.get('antojos_dulces', [])) + len(st.session_state.get('antojos_salados', []))
    st.markdown(f"""
    ### 😋 Patrones y Hábitos
    - **Frutas:** {len(st.session_state.get('frutas_lista', []))} seleccionadas
    - **Métodos cocción:** {len(st.session_state.get('metodos_coccion_accesibles', []))} disponibles
    - **Antojos:** {total_antojos} tipos identificados
    """)

st.success(f"""
### ✅ Evaluación de patrones alimentarios completada exitosamente

Tu perfil alimentario ha sido analizado considerando todos los grupos alimentarios evaluados: 
proteínas (grasas y magras), grasas saludables, carbohidratos complejos, vegetales, frutas, 
métodos de cocción, restricciones alimentarias y patrones de antojos.

**Este análisis proporciona la base para desarrollar recomendaciones nutricionales personalizadas** 
que se ajusten a tus gustos, tolerancias y necesidades específicas.

Se recomienda consulta con nutricionista especializado para desarrollar plan específico basado en estos patrones.
""")

st.markdown('</div>', unsafe_allow_html=True)

# Función para verificar datos completos
def datos_completos_para_email():
    obligatorios = {
        "Nombre": st.session_state.get('nombre'),
        "Email": st.session_state.get('email_cliente'), 
        "Teléfono": st.session_state.get('telefono'),
        "Edad": st.session_state.get('edad')
    }
    faltantes = [campo for campo, valor in obligatorios.items() if not valor]
    return faltantes

def verificar_grupos_obligatorios_completos():
    """Verifica que los grupos obligatorios (1-6) estén completados"""
    grupos_incompletos = []
    
    # Grupo 1: Proteínas grasas
    if not validate_step_1():
        grupos_incompletos.append("Proteínas con más contenido graso")
    
    # Grupo 2: Proteínas magras  
    if not validate_step_2():
        grupos_incompletos.append("Proteínas magras")
        
    # Grupo 3: Grasas saludables
    if not validate_step_3():
        grupos_incompletos.append("Fuentes de grasa saludable")
        
    # Grupo 4: Carbohidratos
    if not validate_step_4():
        grupos_incompletos.append("Carbohidratos complejos")
        
    # Grupo 5: Vegetales
    if not validate_step_5():
        grupos_incompletos.append("Vegetales")
        
    # Grupo 6: Frutas
    if not validate_step_6():
        grupos_incompletos.append("Frutas")
        
    return grupos_incompletos

# Botón para enviar email
if not st.session_state.get("correo_enviado", False):
    if st.button("📧 Terminar cuestionario y enviar resumen por email", key="enviar_email"):
        faltantes = datos_completos_para_email()
        grupos_incompletos = verificar_grupos_obligatorios_completos()
        
        if faltantes:
            st.error(f"❌ No se puede enviar el email. Faltan datos personales: {', '.join(faltantes)}")
        elif grupos_incompletos:
            st.error(f"""
            ❌ **No se puede enviar el email. Grupos incompletos:**
            
            Los siguientes grupos alimentarios requieren al menos una selección (puedes marcar 'Ninguno' si no consumes ninguno):
            
            {chr(10).join([f'• {grupo}' for grupo in grupos_incompletos])}
            
            Por favor, completa estos grupos antes de enviar el resumen.
            """)
        else:
            with st.spinner("📧 Enviando resumen de patrones alimentarios por email..."):
                resumen_completo = crear_resumen_email()
                ok = enviar_email_resumen(
                    resumen_completo, 
                    st.session_state.get('nombre', ''), 
                    st.session_state.get('email_cliente', ''), 
                    st.session_state.get('fecha_llenado', ''), 
                    st.session_state.get('edad', ''), 
                    st.session_state.get('telefono', '')
                )
                if ok:
                    st.session_state["correo_enviado"] = True
                    st.success("✅ Email enviado exitosamente a administración")
                else:
                    st.error("❌ Error al enviar email. Contacta a soporte técnico.")
else:
    st.info("✅ El resumen ya fue enviado por email. Si requieres reenviarlo, usa el botón de 'Reenviar Email'.")

# Opción para reenviar manualmente
if st.button("📧 Reenviar Email", key="reenviar_email"):
    faltantes = datos_completos_para_email()
    grupos_incompletos = verificar_grupos_obligatorios_completos()
    
    if faltantes:
        st.error(f"❌ No se puede reenviar el email. Faltan datos personales: {', '.join(faltantes)}")
    elif grupos_incompletos:
        st.error(f"""
        ❌ **No se puede reenviar el email. Grupos incompletos:**
        
        Los siguientes grupos alimentarios requieren al menos una selección:
        
        {chr(10).join([f'• {grupo}' for grupo in grupos_incompletos])}
        """)
    else:
        with st.spinner("📧 Reenviando resumen por email..."):
            resumen_completo = crear_resumen_email()
            ok = enviar_email_resumen(
                resumen_completo, 
                st.session_state.get('nombre', ''), 
                st.session_state.get('email_cliente', ''), 
                st.session_state.get('fecha_llenado', ''), 
                st.session_state.get('edad', ''), 
                st.session_state.get('telefono', '')
            )
            if ok:
                st.session_state["correo_enviado"] = True
                st.success("✅ Email reenviado exitosamente a administración")
            else:
                st.error("❌ Error al reenviar email. Contacta a soporte técnico.")

# Limpieza de sesión y botón de nueva evaluación
if st.button("🔄 Nueva Evaluación", key="nueva"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Footer moderno
st.markdown("""
<div class="footer-mupai">
    <h4>MUPAI / Muscle up GYM Alimentary Pattern Assessment Intelligence</h4>
    <span>Digital Nutrition Science</span>
    <br>
    <span>© 2025 MUPAI - Muscle up GYM / MUPAI</span>
    <br>
    <a href="https://muscleupgym.fitness" target="_blank">muscleupgym.fitness</a>
</div>
""", unsafe_allow_html=True)
