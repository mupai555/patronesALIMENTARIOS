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
        st.session_state.get('carnes_grasas', []) + 
        st.session_state.get('quesos_grasos', []) + 
        st.session_state.get('lacteos_enteros', []) + 
        st.session_state.get('pescados_grasos', [])
    )
    return len(selections) > 0

def validate_step_2():
    """Valida que se haya seleccionado al menos una opción en proteínas magras"""
    selections = (
        st.session_state.get('carnes_magras', []) + 
        st.session_state.get('pescados_blancos', []) + 
        st.session_state.get('quesos_magros', []) + 
        st.session_state.get('lacteos_light', []) + 
        st.session_state.get('otros_proteinas_magras', [])
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
    """Valida alergias/intolerancias - opcional"""
    return True  # Este paso es opcional

def validate_step_10():
    """Valida antojos - opcional"""
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
        10: validate_step_10
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
        if current_step < 10:
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
    color: #fff !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    font-size: 1.04rem !important;
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
        10: False  # Antojos
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
    
    st.markdown(f"""
    <div class="content-card" style="background: #2A2A2A; border-left: 5px solid #F4C430;">
        <h3 style="color: #F4C430; text-align: center; margin-bottom: 1rem;">🗺️ Progreso del Cuestionario</h3>
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 1 else '#27AE60' if step_completed.get(1, False) else '#666'}; color: {'#1E1E1E' if current_step == 1 or step_completed.get(1, False) else '#FFF'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">1</div>
                <small>Proteínas Grasas</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 2 else '#27AE60' if step_completed.get(2, False) else '#666' if max_unlocked >= 2 else '#333'}; color: {'#1E1E1E' if current_step == 2 or step_completed.get(2, False) else '#FFF' if max_unlocked >= 2 else '#888'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">2</div>
                <small>Proteínas Magras</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 3 else '#27AE60' if step_completed.get(3, False) else '#666' if max_unlocked >= 3 else '#333'}; color: {'#1E1E1E' if current_step == 3 or step_completed.get(3, False) else '#FFF' if max_unlocked >= 3 else '#888'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">3</div>
                <small>Grasas Saludables</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 4 else '#27AE60' if step_completed.get(4, False) else '#666' if max_unlocked >= 4 else '#333'}; color: {'#1E1E1E' if current_step == 4 or step_completed.get(4, False) else '#FFF' if max_unlocked >= 4 else '#888'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">4</div>
                <small>Carbohidratos</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 5 else '#27AE60' if step_completed.get(5, False) else '#666' if max_unlocked >= 5 else '#333'}; color: {'#1E1E1E' if current_step == 5 or step_completed.get(5, False) else '#FFF' if max_unlocked >= 5 else '#888'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">5</div>
                <small>Vegetales</small>
            </div>
            <div style="text-align: center; flex: 1; min-width: 120px;">
                <div style="background: {'#F4C430' if current_step == 6 else '#27AE60' if step_completed.get(6, False) else '#666' if max_unlocked >= 6 else '#333'}; color: {'#1E1E1E' if current_step == 6 or step_completed.get(6, False) else '#FFF' if max_unlocked >= 6 else '#888'}; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold;">6</div>
                <small>Frutas</small>
            </div>
        </div>
        <div style="text-align: center; margin-top: 1rem; color: #CCCCCC;">
            <small>Paso {current_step} de 10 - {'✅ Completado' if step_completed.get(current_step, False) else '⏳ En progreso'}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar solo el paso actual
    current_step = st.session_state.get('current_step', 1)

    # GRUPO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO
    if current_step == 1:
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥩 PASO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(10, text="Paso 1 de 10: Proteínas con más contenido graso")
        
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
        st.info("💡 **Ayuda:** Incluye cualquier forma de huevo y embutidos que consumas, sin importar la frecuencia.")
        huevos_embutidos = st.multiselect(
            "¿Cuáles de estos huevos y embutidos consumes? (Puedes seleccionar varios)",
            ["Huevo entero", "Chorizo", "Salchicha (Viena, alemana, parrillera)", "Longaniza", "Tocino", "Jamón serrano"],
            key="huevos_embutidos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los que consumes. Es mejor incluir más opciones para personalizar mejor tu plan."
        )
        
        st.markdown("#### 🥩 Carnes y cortes grasos")
        st.info("💡 **Ayuda:** Incluye cualquier tipo de carne roja con mayor contenido graso que consumas.")
        carnes_grasas = st.multiselect(
            "¿Cuáles de estas carnes y cortes grasos consumes? (Puedes seleccionar varios)",
            ["Costilla de res", "Costilla de cerdo", "Ribeye", "T-bone", "New York", "Arrachera marinada", 
             "Molida 80/20 (regular)", "Molida 85/15", "Cecina con grasa"],
            key="carnes_grasas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los cortes que consumes, aunque sea ocasionalmente."
        )
        
        st.markdown("#### 🧀 Quesos altos en grasa")
        st.info("💡 **Ayuda:** Incluye cualquier tipo de queso con mayor contenido graso que disfrutes.")
        quesos_grasos = st.multiselect(
            "¿Cuáles de estos quesos altos en grasa consumes? (Puedes seleccionar varios)",
            ["Queso manchego", "Queso doble crema", "Queso oaxaca", "Queso gouda", "Queso crema", "Queso cheddar"],
            key="quesos_grasos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los quesos que consumes en cualquier preparación."
        )
        
        st.markdown("#### 🥛 Lácteos enteros")
        st.info("💡 **Ayuda:** Incluye cualquier producto lácteo entero (no light o descremado) que consumas.")
        lacteos_enteros = st.multiselect(
            "¿Cuáles de estos lácteos enteros consumes? (Puedes seleccionar varios)",
            ["Leche entera", "Yogur entero azucarado", "Yogur tipo griego entero", "Yogur de frutas azucarado", 
             "Yogur bebible regular", "Crema", "Queso para untar (tipo Philadelphia original)"],
            key="lacteos_enteros",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los lácteos enteros que uses en tu alimentación diaria."
        )
        
        st.markdown("#### 🐟 Pescados grasos")
        st.info("💡 **Ayuda:** Incluye pescados con mayor contenido de grasas omega-3 que consumas.")
        pescados_grasos = st.multiselect(
            "¿Cuáles de estos pescados grasos consumes? (Puedes seleccionar varios)",
            ["Atún en aceite", "Salmón", "Sardinas", "Macarela", "Trucha"],
            key="pescados_grasos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los pescados grasos que consumes, frescos o enlatados."
        )

        # Resumen del paso actual
        total_seleccionados = (len(st.session_state.get('huevos_embutidos', [])) + 
                              len(st.session_state.get('carnes_grasas', [])) + 
                              len(st.session_state.get('quesos_grasos', [])) + 
                              len(st.session_state.get('lacteos_enteros', [])) + 
                              len(st.session_state.get('pescados_grasos', [])))
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍗 PASO 2: PROTEÍNA ANIMAL MAGRA
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(20, text="Paso 2 de 10: Proteínas animales magras")
        
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
        
        st.markdown("#### 🍗 Carnes y cortes magros")
        st.info("💡 **Ayuda:** Incluye carnes con bajo contenido graso, como pechuga de pollo, cortes magros de res y cerdo.")
        carnes_magras = st.multiselect(
            "¿Cuáles de estas carnes y cortes magros consumes? (Puedes seleccionar varios)",
            ["Pechuga de pollo sin piel", "Filete de res magro (aguayón, bola, sirloin sin grasa visible)", 
             "Lomo de cerdo", "Bistec de res sin grasa visible", "Cecina magra", "Molida 90/10", 
             "Molida 95/5", "Molida 97/3", "Carne para deshebrar sin grasa (falda limpia)"],
            key="carnes_magras",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las carnes magras que te resulten fáciles de consumir."
        )
        
        st.markdown("#### 🐟 Pescados blancos y bajos en grasa")
        st.info("💡 **Ayuda:** Incluye pescados con carne blanca o bajo contenido graso que consumas.")
        pescados_blancos = st.multiselect(
            "¿Cuáles de estos pescados blancos y bajos en grasa consumes? (Puedes seleccionar varios)",
            ["Tilapia", "Basa", "Huachinango", "Merluza", "Robalo", "Atún en agua"],
            key="pescados_blancos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los pescados blancos que consumes, frescos, congelados o enlatados."
        )
        
        st.markdown("#### 🧀 Quesos bajos en grasa o magros")
        st.info("💡 **Ayuda:** Incluye quesos con menor contenido graso o versiones light que consumas.")
        quesos_magros = st.multiselect(
            "¿Cuáles de estos quesos bajos en grasa consumes? (Puedes seleccionar varios)",
            ["Queso panela", "Queso cottage", "Queso ricotta light", "Queso oaxaca reducido en grasa", 
             "Queso mozzarella light", "Queso fresco bajo en grasa"],
            key="quesos_magros",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los quesos bajos en grasa que consumes."
        )
        
        st.markdown("#### 🥛 Lácteos light o reducidos")
        st.info("💡 **Ayuda:** Incluye productos lácteos descremados, light o sin azúcar que consumas.")
        lacteos_light = st.multiselect(
            "¿Cuáles de estos lácteos light o reducidos consumes? (Puedes seleccionar varios)",
            ["Leche descremada", "Leche deslactosada light", "Leche de almendra sin azúcar", 
             "Leche de coco sin azúcar", "Leche de soya sin azúcar", "Yogur griego natural sin azúcar", 
             "Yogur griego light", "Yogur bebible bajo en grasa", "Yogur sin azúcar añadida", 
             "Yogur de frutas bajo en grasa y sin azúcar añadida", "Queso crema light"],
            key="lacteos_light",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los lácteos light o reducidos que uses regularmente."
        )
        
        st.markdown("#### 🥚 Otros productos proteicos magros")
        st.info("💡 **Ayuda:** Incluye otros productos con alto contenido proteico y bajo en grasa.")
        otros_proteinas_magras = st.multiselect(
            "¿Cuáles de estos otros productos consumes? (Puedes seleccionar varios)",
            ["Clara de huevo", "Jamón de pechuga de pavo", "Jamón de pierna bajo en grasa", 
             "Salchicha de pechuga de pavo (light)"],
            key="otros_proteinas_magras",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los productos proteicos magros que consumes."
        )

        # Resumen del paso actual
        total_seleccionados = (len(st.session_state.get('carnes_magras', [])) + 
                              len(st.session_state.get('pescados_blancos', [])) + 
                              len(st.session_state.get('quesos_magros', [])) + 
                              len(st.session_state.get('lacteos_light', [])) + 
                              len(st.session_state.get('otros_proteinas_magras', [])))
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥑 PASO 3: FUENTES DE GRASA SALUDABLE
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(30, text="Paso 3 de 10: Fuentes de grasa saludable")
        
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
        
        **💡 Instrucción:** Marca TODOS los alimentos que puedas o suelas consumir, incluso ocasionalmente.
        """)
        
        st.markdown("#### 🥑 Grasas naturales de alimentos")
        st.info("💡 **Ayuda:** Incluye alimentos que naturalmente contienen grasas saludables.")
        grasas_naturales = st.multiselect(
            "¿Cuáles de estas grasas naturales consumes? (Puedes seleccionar varios)",
            ["Aguacate", "Yema de huevo", "Aceitunas (negras, verdes)", "Coco rallado natural", 
             "Coco fresco", "Leche de coco sin azúcar"],
            key="grasas_naturales",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las grasas naturales que consumes en cualquier preparación."
        )
        
        st.markdown("#### 🌰 Frutos secos y semillas")
        st.info("💡 **Ayuda:** Incluye cualquier tipo de fruto seco, semilla o nuez que consumas, natural o tostada.")
        frutos_secos_semillas = st.multiselect(
            "¿Cuáles de estos frutos secos y semillas consumes? (Puedes seleccionar varios)",
            ["Almendras", "Nueces", "Nuez de la India", "Pistaches", "Cacahuates naturales (sin sal)", 
             "Semillas de chía", "Semillas de linaza", "Semillas de girasol", "Semillas de calabaza (pepitas)"],
            key="frutos_secos_semillas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los frutos secos y semillas que consumes como snack o en preparaciones."
        )
        
        st.markdown("#### 🧈 Mantequillas y pastas vegetales")
        st.info("💡 **Ayuda:** Incluye mantequillas naturales hechas de frutos secos o semillas (sin azúcar añadida).")
        mantequillas_vegetales = st.multiselect(
            "¿Cuáles de estas mantequillas y pastas vegetales consumes? (Puedes seleccionar varios)",
            ["Mantequilla de maní natural", "Mantequilla de almendra", "Tahini (pasta de ajonjolí)", 
             "Mantequilla de nuez de la India"],
            key="mantequillas_vegetales",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las mantequillas vegetales naturales que consumes."
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍞 PASO 4: CARBOHIDRATOS COMPLEJOS Y CEREALES
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(40, text="Paso 4 de 10: Carbohidratos complejos y cereales")
        
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
        st.info("💡 **Ayuda:** Incluye cereales, avenas y granos que consumas en el desayuno o comidas principales.")
        cereales_integrales = st.multiselect(
            "¿Cuáles de estos cereales y granos integrales consumes? (Puedes seleccionar varios)",
            ["Avena tradicional", "Avena instantánea sin azúcar", "Arroz integral", "Arroz blanco", 
             "Arroz jazmín", "Arroz basmati", "Trigo bulgur", "Cuscús", "Quinoa", "Amaranto", 
             "Trigo inflado natural", "Cereal de maíz sin azúcar", "Cereal integral bajo en azúcar"],
            key="cereales_integrales",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los cereales y granos que consumes regularmente."
        )
        
        st.markdown("#### 🌽 Tortillas y panes")
        st.info("💡 **Ayuda:** Incluye cualquier tipo de tortilla, pan o producto horneado que consumas.")
        tortillas_panes = st.multiselect(
            "¿Cuáles de estas tortillas y panes consumes? (Puedes seleccionar varios)",
            ["Tortilla de maíz", "Tortilla de nopal", "Tortilla integral", "Tortilla de harina", 
             "Tortilla de avena", "Pan integral", "Pan multigrano", "Pan de centeno", 
             "Pan de caja sin azúcar añadida", "Pan pita integral", "Pan tipo Ezekiel (germinado)"],
            key="tortillas_panes",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todos los tipos de tortillas y panes que consumes."
        )
        
        st.markdown("#### 🥔 Raíces, tubérculos y derivados")
        st.info("💡 **Ayuda:** Incluye papas, camotes y otros tubérculos que consumas cocidos o preparados.")
        raices_tuberculos = st.multiselect(
            "¿Cuáles de estas raíces, tubérculos y derivados consumes? (Puedes seleccionar varios)",
            ["Papa cocida o al horno", "Camote cocido o al horno", "Yuca", "Plátano macho", 
             "Puré de papa", "Papas horneadas", "Papas en air fryer"],
            key="raices_tuberculos",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Incluye todos los tubérculos y raíces que consumes en diferentes preparaciones."
        )
        
        st.markdown("#### 🫘 Leguminosas")
        st.info("💡 **Ayuda:** Incluye frijoles, lentejas y otras legumbres que consumas, cocidas o en preparaciones.")
        leguminosas = st.multiselect(
            "¿Cuáles de estas leguminosas consumes? (Puedes seleccionar varios)",
            ["Frijoles negros", "Frijoles bayos", "Frijoles pintos", "Lentejas", "Garbanzos", 
             "Habas cocidas", "Soya texturizada", "Edamames (vainas de soya)", "Hummus (puré de garbanzo)"],
            key="leguminosas",
            placeholder="🔽 Haz clic aquí para ver y seleccionar opciones",
            help="Selecciona todas las leguminosas que consumes, frescas, secas o enlatadas."
        )

        # Resumen del paso actual
        total_seleccionados = (len(st.session_state.get('cereales_integrales', [])) + 
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥬 PASO 5: VEGETALES
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(50, text="Paso 5 de 10: Vegetales")
        
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
        
        **💡 Instrucción:** Marca TODOS los vegetales que consumes o toleras bien, sin importar cómo los prepares.
        """)
        
        st.info("💡 **Ayuda:** Incluye vegetales que consumas crudos, cocidos, al vapor, salteados o en cualquier preparación. Entre más vegetales selecciones, más variado será tu plan.")
        
        vegetales_lista = st.multiselect(
            "¿Cuáles de estos vegetales consumes o toleras fácilmente? (Puedes seleccionar varios)",
            ["Espinaca", "Acelga", "Kale", "Lechuga (romana, italiana, orejona, iceberg)", 
             "Col morada", "Col verde", "Repollo", "Brócoli", "Coliflor", "Ejote", "Chayote", 
             "Calabacita", "Nopal", "Betabel", "Zanahoria", "Jitomate saladet", "Jitomate bola", 
             "Tomate verde", "Cebolla blanca", "Cebolla morada", "Pimiento morrón (rojo, verde, amarillo, naranja)", 
             "Pepino", "Apio", "Rábano", "Ajo", "Berenjena", "Champiñones", "Guisantes (chícharos)", 
             "Verdolaga", "Habas tiernas", "Germen de alfalfa", "Germen de soya", "Flor de calabaza"],
            key="vegetales_lista",
            placeholder="🔽 Haz clic aquí para ver y seleccionar todos los vegetales que consumes",
            help="Selecciona todos los vegetales que consumes o toleras, en cualquier forma de preparación (crudo, cocido, salteado, etc.)"
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #DAA520;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍎 PASO 6: FRUTAS
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(60, text="Paso 6 de 10: Frutas - ¡Completando grupos principales!")
        
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
        
        **💡 Instrucción:** Marca TODAS las frutas que disfrutes o toleres, frescas, congeladas o en cualquier presentación natural.
        """)
        
        st.info("💡 **Ayuda:** Incluye frutas que consumas solas, en licuados, ensaladas, postres naturales o cualquier preparación. La variedad de frutas enriquecerá tu plan nutricional.")
        
        frutas_lista = st.multiselect(
            "¿Cuáles de estas frutas disfrutas o toleras bien? (Puedes seleccionar varios)",
            ["Manzana (roja, verde, gala, fuji)", "Naranja", "Mandarina", "Mango (petacón, ataulfo)", 
             "Papaya", "Sandía", "Melón", "Piña", "Plátano (tabasco, dominico, macho)", "Uvas", 
             "Fresas", "Arándanos", "Zarzamoras", "Frambuesas", "Higo", "Kiwi", "Pera", "Durazno", 
             "Ciruela", "Granada", "Cereza", "Chabacano", "Lima", "Limón", "Guayaba", "Tuna", 
             "Níspero", "Mamey", "Pitahaya (dragon fruit)", "Tamarindo", "Coco (carne, rallado)", 
             "Caqui (persimón)", "Maracuyá", "Manzana en puré sin azúcar", "Fruta en almíbar light"],
            key='frutas_lista',
            placeholder="🔽 Haz clic aquí para ver y seleccionar todas las frutas que disfrutas",
            help="Selecciona todas las frutas que disfrutas, en cualquier presentación natural (fresca, congelada, deshidratada sin azúcar, etc.)"
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #27AE60 0%, #2ECC71 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #27AE60;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🍳 PASO 7: ACEITES DE COCCIÓN PREFERIDOS
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">Información Adicional - Opcional</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(70, text="Paso 7 de 10: Aceites de cocción (Opcional)")
        
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
             "❌ Prefiero cocinar sin aceite o con agua"],
            key='aceites_coccion',
            placeholder="🔽 Haz clic aquí para seleccionar los aceites que usas para cocinar",
            help="Selecciona todos los aceites y grasas que usas habitualmente en tu cocina."
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #27AE60 0%, #2ECC71 100%); color: #1E1E1E; margin-bottom: 2rem; border: 3px solid #27AE60;">
            <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1rem;">
                🥤 PASO 8: BEBIDAS PARA HIDRATACIÓN
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">Información Adicional - Opcional</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(80, text="Paso 8 de 10: Bebidas para hidratación (Opcional)")
        
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
             "🥤 Refrescos sin calorías (Coca Cola Zero, Pepsi Light, etc.)"],
            key='bebidas_sin_calorias',
            placeholder="🔽 Haz clic aquí para seleccionar las bebidas que consumes",
            help="Selecciona todas las bebidas sin calorías que acostumbres para hidratarte."
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); color: #FFFFFF; margin-bottom: 2rem; border: 3px solid #E74C3C;">
            <h2 style="color: #FFFFFF; text-align: center; margin-bottom: 1rem;">
                🚨 PASO 9: ALERGIAS E INTOLERANCIAS
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">Información Crítica para tu Seguridad</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(90, text="Paso 9 de 10: Alergias e intolerancias (Crítico)")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.markdown("""
        ### ⚠️ Información Crítica para tu Seguridad Alimentaria
        Esta sección es **fundamental** para crear un plan alimentario seguro y adecuado para ti.
        Por favor, sé muy específico y honesto con tus respuestas.
        """)
        
        st.markdown("### ❗ 1. ¿Tienes alguna alergia alimentaria?")
        st.error("🚨 **IMPORTANTE:** Las alergias alimentarias pueden ser graves. Marca todas las que tengas, aunque sean leves.")
        alergias_alimentarias = st.multiselect(
            "Selecciona TODAS las alergias alimentarias que tienes:",
            ["Lácteos", "Huevo", "Frutos secos", "Mariscos", "Pescado", "Gluten", "Soya", "Semillas"],
            key='alergias_alimentarias',
            placeholder="🔽 Selecciona si tienes alguna alergia alimentaria",
            help="Incluye cualquier alergia, desde leve hasta severa. Esto es crítico para tu seguridad."
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
        intolerancias_digestivas = st.multiselect(
            "Selecciona las intolerancias o malestares digestivos que experimentas:",
            ["Lácteos con lactosa", "Leguminosas", "FODMAPs", "Gluten", "Crucíferas", "Endulzantes artificiales"],
            key='intolerancias_digestivas',
            placeholder="🔽 Selecciona si tienes intolerancias digestivas",
            help="Incluye alimentos que te causen malestar digestivo, gases, hinchazón, etc."
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
        st.markdown("""
        <div class="content-card" style="background: linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%); color: #FFFFFF; margin-bottom: 2rem; border: 3px solid #9B59B6;">
            <h2 style="color: #FFFFFF; text-align: center; margin-bottom: 1rem;">
                😋 PASO 10: EVALUACIÓN DE ANTOJOS
            </h2>
            <p style="text-align: center; margin: 0; font-weight: bold;">¡Último Paso! - Información para Estrategias</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Actualizar progreso
        progress.progress(100, text="Paso 10 de 10: Antojos alimentarios - ¡Último paso!")
        
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🧠 ¿Por qué evaluamos tus antojos?
        Conocer tus **antojos frecuentes** nos ayuda a:
        - Crear estrategias para manejarlos de forma saludable
        - Incluir alternativas satisfactorias en tu plan
        - Desarrollar un plan realista y sostenible a largo plazo
        
        **💡 Instrucción:** Marca los alimentos que frecuentemente se te antojan o deseas con intensidad, 
        aunque no necesariamente los consumas con regularidad. (Este paso es opcional)
        """)
        
        st.markdown("---")
        st.markdown("### 🍫 Antojos de alimentos dulces / postres")
        st.info("💡 **Ayuda:** Incluye cualquier dulce, postre o alimento azucarado que se te antoje frecuentemente.")
        antojos_dulces = st.multiselect(
            "¿Cuáles de estos alimentos dulces se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Chocolate con leche", "Chocolate amargo", "Pan dulce (conchas, donas, cuernitos)", 
             "Pastel (tres leches, chocolate, etc.)", "Galletas (Marías, Emperador, Chokis, etc.)", 
             "Helado / Nieve", "Flan / Gelatina", "Dulces tradicionales (cajeta, obleas, jamoncillo, glorias)", 
             "Cereal azucarado", "Leche condensada", "Churros"],
            key='antojos_dulces',
            placeholder="🔽 Selecciona los alimentos dulces que se te antojan",
            help="Incluye todos los dulces que frecuentemente deseas, aunque no los consumas seguido."
        )
        
        st.markdown("---")
        st.markdown("### 🧂 Antojos de alimentos salados / snacks")
        st.info("💡 **Ayuda:** Incluye botanas, frituras o alimentos salados que se te antojen.")
        antojos_salados = st.multiselect(
            "¿Cuáles de estos alimentos salados se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Papas fritas (Sabritas, Ruffles, etc.)", "Cacahuates enchilados", "Frituras (Doritos, Cheetos, Takis, etc.)", 
             "Totopos con salsa", "Galletas saladas", "Cacahuates japoneses", "Chicharrón (de cerdo o harina)", 
             "Nachos con queso", "Queso derretido o gratinado"],
            key='antojos_salados',
            placeholder="🔽 Selecciona los alimentos salados que se te antojan",
            help="Incluye todas las botanas y snacks salados que frecuentemente deseas."
        )
        
        st.markdown("---")
        st.markdown("### 🌮 Antojos de comidas rápidas / callejeras")
        st.info("💡 **Ayuda:** Incluye comida rápida, platillos callejeros o preparaciones que se te antojen.")
        antojos_comida_rapida = st.multiselect(
            "¿Cuáles de estas comidas rápidas se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Tacos (pastor, asada, birria, etc.)", "Tortas (cubana, ahogada, etc.)", "Hamburguesas", "Hot dogs", 
             "Pizza", "Quesadillas fritas", "Tamales", "Pambazos", "Sopes / gorditas", "Elotes / esquites", 
             "Burritos", "Enchiladas", "Empanadas"],
            key='antojos_comida_rapida',
            placeholder="🔽 Selecciona las comidas rápidas que se te antojan",
            help="Incluye toda la comida rápida o callejera que frecuentemente deseas."
        )
        
        st.markdown("---")
        st.markdown("### 🍹 Antojos de bebidas y postres líquidos")
        st.info("💡 **Ayuda:** Incluye bebidas azucaradas, alcohólicas o postres líquidos que se te antojen.")
        antojos_bebidas = st.multiselect(
            "¿Cuáles de estas bebidas se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Refrescos regulares (Coca-Cola, Fanta, etc.)", "Jugos industrializados (Boing, Jumex, etc.)", 
             "Malteadas / Frappés", "Agua de sabor con azúcar (jamaica, horchata, tamarindo)", 
             "Café con azúcar y leche", "Champurrado / atole", "Licuado de plátano con azúcar", 
             "Bebidas alcohólicas (cerveza, tequila, vino, etc.)"],
            key='antojos_bebidas',
            placeholder="🔽 Selecciona las bebidas que se te antojan",
            help="Incluye todas las bebidas con calorías que frecuentemente deseas."
        )
        
        st.markdown("---")
        st.markdown("### 🔥 Antojos de alimentos con condimentos estimulantes")
        st.info("💡 **Ayuda:** Incluye alimentos picantes, con chile o condimentos intensos que se te antojen.")
        antojos_picantes = st.multiselect(
            "¿Cuáles de estos alimentos picantes se te antojan frecuentemente? (Puedes seleccionar varios)",
            ["Chiles en escabeche", "Salsas picantes", "Salsa Valentina, Tajín o Chamoy", 
             "Pepinos con chile y limón", "Mangos verdes con chile", "Gomitas enchiladas", 
             "Fruta con Miguelito o chile en polvo"],
            key='antojos_picantes',
            placeholder="🔽 Selecciona los alimentos picantes que se te antojan",
            help="Incluye todos los alimentos con chile o condimentos estimulantes que deseas."
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
                st.session_state.step_completed[10] = True

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
            total_proteinas_grasas = len(st.session_state.get('huevos_embutidos', [])) + len(st.session_state.get('carnes_grasas', [])) + len(st.session_state.get('quesos_grasos', [])) + len(st.session_state.get('lacteos_enteros', [])) + len(st.session_state.get('pescados_grasos', []))
            st.write(f"• **Total alimentos seleccionados:** {total_proteinas_grasas}")
            if st.session_state.get('huevos_embutidos'):
                st.write(f"• **Huevos/embutidos:** {len(st.session_state.get('huevos_embutidos', []))}")
            if st.session_state.get('carnes_grasas'):
                st.write(f"• **Carnes grasas:** {len(st.session_state.get('carnes_grasas', []))}")
            
            st.markdown("#### 🍗 Grupo 2: Proteínas Magras")
            total_proteinas_magras = len(st.session_state.get('carnes_magras', [])) + len(st.session_state.get('pescados_blancos', [])) + len(st.session_state.get('quesos_magros', [])) + len(st.session_state.get('lacteos_light', [])) + len(st.session_state.get('otros_proteinas_magras', []))
            st.write(f"• **Total alimentos seleccionados:** {total_proteinas_magras}")
            if st.session_state.get('carnes_magras'):
                st.write(f"• **Carnes magras:** {len(st.session_state.get('carnes_magras', []))}")
            if st.session_state.get('pescados_blancos'):
                st.write(f"• **Pescados blancos:** {len(st.session_state.get('pescados_blancos', []))}")
        
        with col2:
            st.markdown("#### 🥑 Grupo 3: Grasas Saludables")
            total_grasas = len(st.session_state.get('grasas_naturales', [])) + len(st.session_state.get('frutos_secos_semillas', [])) + len(st.session_state.get('mantequillas_vegetales', []))
            st.write(f"• **Total alimentos seleccionados:** {total_grasas}")
            if st.session_state.get('grasas_naturales'):
                st.write(f"• **Grasas naturales:** {len(st.session_state.get('grasas_naturales', []))}")
            if st.session_state.get('frutos_secos_semillas'):
                st.write(f"• **Frutos secos/semillas:** {len(st.session_state.get('frutos_secos_semillas', []))}")
            
            st.markdown("#### 🍞 Grupo 4: Carbohidratos")
            total_carbohidratos = len(st.session_state.get('cereales_integrales', [])) + len(st.session_state.get('tortillas_panes', [])) + len(st.session_state.get('raices_tuberculos', [])) + len(st.session_state.get('leguminosas', []))
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

        # Recomendaciones personalizadas basadas en datos reales
        st.markdown("### 💡 Recomendaciones Personalizadas Iniciales")
        
        # Análisis básico basado en las respuestas actuales
        recomendaciones = []
        
        # Verificar diversidad de alimentos por grupo
        total_grupos_completos = 0
        if len(st.session_state.get('huevos_embutidos', [])) + len(st.session_state.get('carnes_grasas', [])) > 0:
            total_grupos_completos += 1
        if len(st.session_state.get('carnes_magras', [])) + len(st.session_state.get('pescados_blancos', [])) > 0:
            total_grupos_completos += 1
        if len(st.session_state.get('grasas_naturales', [])) + len(st.session_state.get('frutos_secos_semillas', [])) > 0:
            total_grupos_completos += 1
        if len(st.session_state.get('cereales_integrales', [])) + len(st.session_state.get('tortillas_panes', [])) > 0:
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

🥩 Carnes y cortes grasos:
- {', '.join(st.session_state.get('carnes_grasas', [])) if st.session_state.get('carnes_grasas') else 'No especificado'}

🧀 Quesos altos en grasa:
- {', '.join(st.session_state.get('quesos_grasos', [])) if st.session_state.get('quesos_grasos') else 'No especificado'}

🥛 Lácteos enteros:
- {', '.join(st.session_state.get('lacteos_enteros', [])) if st.session_state.get('lacteos_enteros') else 'No especificado'}

🐟 Pescados grasos:
- {', '.join(st.session_state.get('pescados_grasos', [])) if st.session_state.get('pescados_grasos') else 'No especificado'}

=====================================
🍗 GRUPO 2: PROTEÍNA ANIMAL MAGRA
=====================================
🍗 Carnes y cortes magros:
- {', '.join(st.session_state.get('carnes_magras', [])) if st.session_state.get('carnes_magras') else 'No especificado'}

🐟 Pescados blancos y bajos en grasa:
- {', '.join(st.session_state.get('pescados_blancos', [])) if st.session_state.get('pescados_blancos') else 'No especificado'}

🧀 Quesos bajos en grasa o magros:
- {', '.join(st.session_state.get('quesos_magros', [])) if st.session_state.get('quesos_magros') else 'No especificado'}

🥛 Lácteos light o reducidos:
- {', '.join(st.session_state.get('lacteos_light', [])) if st.session_state.get('lacteos_light') else 'No especificado'}

🥚 Otros:
- {', '.join(st.session_state.get('otros_proteinas_magras', [])) if st.session_state.get('otros_proteinas_magras') else 'No especificado'}

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

🌽 Tortillas y panes:
- {', '.join(st.session_state.get('tortillas_panes', [])) if st.session_state.get('tortillas_panes') else 'No especificado'}

🥔 Raíces, tubérculos y derivados:
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
RESUMEN DE ANÁLISIS IDENTIFICADO:
=====================================
Este cuestionario completo de patrones alimentarios proporciona una base integral 
para el desarrollo de recomendaciones nutricionales altamente personalizadas basadas en:

1. 6 grupos alimentarios principales evaluados
2. Métodos de cocción disponibles y preferidos
3. Restricciones específicas (alergias e intolerancias)  
4. Patrones de preferencias detallados
5. Análisis de antojos y alimentación emocional
6. Contexto personal, familiar y social completo

RECOMENDACIONES PARA SEGUIMIENTO:
- Desarrollar plan nutricional personalizado basado en estos patrones
- Considerar restricciones y alergias como prioridad absoluta
- Aprovechar métodos de cocción preferidos y disponibles
- Integrar estrategias para manejo de antojos identificados
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
    total_alimentos_grupo1 = len(st.session_state.get('huevos_embutidos', [])) + len(st.session_state.get('carnes_grasas', [])) + len(st.session_state.get('quesos_grasos', []))
    total_alimentos_grupo2 = len(st.session_state.get('carnes_magras', [])) + len(st.session_state.get('pescados_blancos', [])) + len(st.session_state.get('quesos_magros', []))
    st.markdown(f"""
    ### 🥩 Proteínas
    - **Grupo 1 (grasas):** {total_alimentos_grupo1} alimentos
    - **Grupo 2 (magras):** {total_alimentos_grupo2} alimentos
    - **Restricciones:** {'Sí' if st.session_state.get('alergias_alimentarias') or st.session_state.get('intolerancias_digestivas') else 'No'}
    """)

with col2:
    total_grasas = len(st.session_state.get('grasas_naturales', [])) + len(st.session_state.get('frutos_secos_semillas', []))
    total_carbohidratos = len(st.session_state.get('cereales_integrales', [])) + len(st.session_state.get('tortillas_panes', []))
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

# Botón para enviar email
if not st.session_state.get("correo_enviado", False):
    if st.button("📧 Enviar Resumen por Email", key="enviar_email"):
        faltantes = datos_completos_para_email()
        if faltantes:
            st.error(f"❌ No se puede enviar el email. Faltan: {', '.join(faltantes)}")
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
    if faltantes:
        st.error(f"❌ No se puede reenviar el email. Faltan: {', '.join(faltantes)}")
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
