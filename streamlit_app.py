import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re

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
    "authenticated": False  # Nueva variable para controlar el login
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
    nombre = st.text_input("Nombre completo*", placeholder="Ej: Juan Pérez García", help="Tu nombre legal completo")
    telefono = st.text_input("Teléfono*", placeholder="Ej: 8661234567", help="10 dígitos sin espacios")
    email_cliente = st.text_input("Email*", placeholder="correo@ejemplo.com", help="Email válido para recibir resultados")

with col2:
    edad = st.number_input("Edad (años)*", min_value=15, max_value=80, value=25, help="Tu edad actual")
    sexo = st.selectbox("Sexo biológico*", ["Hombre", "Mujer"], help="Necesario para análisis nutricionales precisos")
    fecha_llenado = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 Fecha de evaluación: {fecha_llenado}")

acepto_terminos = st.checkbox("He leído y acepto la política de privacidad y el descargo de responsabilidad")

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
                        <span style="font-size:1.3rem;">📝</span> <b>Paso 1:</b> Datos personales<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Recopilamos tu información básica para personalizar la evaluación nutricional.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🥗</span> <b>Paso 2:</b> Preferencias alimentarias<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Identificamos tus gustos, aversiones y preferencias de sabores y texturas.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🚫</span> <b>Paso 3:</b> Restricciones y alergias<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Evaluamos restricciones dietéticas, alergias e intolerancias alimentarias.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">⏰</span> <b>Paso 4:</b> Patrones de comida y horarios<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Analizamos frecuencia de comidas, horarios y hábitos de alimentación.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">👨‍🍳</span> <b>Paso 5:</b> Habilidades culinarias y preparación<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Evaluamos nivel de cocina, tiempo disponible y métodos de preparación preferidos.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">🏛️</span> <b>Paso 6:</b> Contexto cultural y social<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Consideramos tradiciones culturales, contexto social y situaciones especiales.
                        </span>
                    </li>
                    <li style="margin-bottom:1.1em;">
                        <span style="font-size:1.3rem;">📈</span> <b>Resultado final:</b> Plan alimentario personalizado<br>
                        <span style="color:#F5F5F5;font-size:1rem;">
                            Recibes recomendaciones nutricionales adaptadas a tus preferencias y necesidades.
                        </span>
                    </li>
                </ul>
                <div style="margin-top:1.2em; font-size:1rem; color:#F4C430;">
                    <b>Finalidad:</b> Esta evaluación integra principios de nutrición personalizada para ofrecerte recomendaciones alimentarias que se ajusten a tu estilo de vida. <br>
                    <b>Tiempo estimado:</b> Menos de 10 minutos.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# VALIDACIÓN DATOS PERSONALES PARA CONTINUAR
datos_personales_completos = all([nombre, telefono, email_cliente]) and acepto_terminos

if datos_personales_completos and st.session_state.datos_completos:
    # Progress bar general
    progress = st.progress(0)
    progress_text = st.empty()

    # CUESTIONARIO DE SELECCIÓN ALIMENTARIA PERSONALIZADA
    st.markdown("""
    <div class="content-card" style="background: linear-gradient(135deg, #F4C430 0%, #DAA520 100%); color: #1E1E1E; margin-bottom: 2rem;">
        <h2 style="color: #1E1E1E; text-align: center; margin-bottom: 1.5rem;">
            🧾 CUESTIONARIO DE SELECCIÓN ALIMENTARIA PERSONALIZADA
        </h2>
        <div style="text-align: left; font-size: 1.1rem; line-height: 1.6;">
            <p><strong>Instrucciones:</strong></p>
            <p>Marca (✓) todos los alimentos y bebidas que consumes con facilidad o disfrutas. Esto permitirá diseñar un plan de alimentación ajustado a tus gustos, tolerancias y necesidades personales.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # GRUPO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO
    with st.expander("🥩 **GRUPO 1: PROTEÍNA ANIMAL CON MÁS CONTENIDO GRASO**", expanded=True):
        progress.progress(17)
        progress_text.text("Grupo 1 de 6: Proteína animal con más contenido graso")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (elige todas las que puedas consumir con facilidad)")
        
        st.markdown("#### 🍳 Huevos y embutidos")
        huevos_embutidos = st.multiselect(
            "Selecciona los huevos y embutidos que consumes:",
            ["Huevo entero", "Chorizo", "Salchicha (Viena, alemana, parrillera)", "Longaniza", "Tocino", "Jamón serrano"],
            help="Marca todos los que consumes con facilidad"
        )
        
        st.markdown("#### 🥩 Carnes y cortes grasos")
        carnes_grasas = st.multiselect(
            "Selecciona las carnes y cortes grasos que consumes:",
            ["Costilla de res", "Costilla de cerdo", "Ribeye", "T-bone", "New York", "Arrachera marinada", 
             "Molida 80/20 (regular)", "Molida 85/15", "Cecina con grasa"],
            help="Marca todos los que consumes con facilidad"
        )
        
        st.markdown("#### 🧀 Quesos altos en grasa")
        quesos_grasos = st.multiselect(
            "Selecciona los quesos altos en grasa que consumes:",
            ["Queso manchego", "Queso doble crema", "Queso oaxaca", "Queso gouda", "Queso crema", "Queso cheddar"],
            help="Marca todos los que consumes con facilidad"
        )
        
        st.markdown("#### 🥛 Lácteos enteros")
        lacteos_enteros = st.multiselect(
            "Selecciona los lácteos enteros que consumes:",
            ["Leche entera", "Yogur entero azucarado", "Yogur tipo griego entero", "Yogur de frutas azucarado", 
             "Yogur bebible regular", "Crema", "Queso para untar (tipo Philadelphia original)"],
            help="Marca todos los que consumes con facilidad"
        )
        
        st.markdown("#### 🐟 Pescados grasos")
        pescados_grasos = st.multiselect(
            "Selecciona los pescados grasos que consumes:",
            ["Atún en aceite", "Salmón", "Sardinas", "Macarela", "Trucha"],
            help="Marca todos los que consumes con facilidad"
        )

        # Guardar en session state
        st.session_state.huevos_embutidos = huevos_embutidos
        st.session_state.carnes_grasas = carnes_grasas
        st.session_state.quesos_grasos = quesos_grasos
        st.session_state.lacteos_enteros = lacteos_enteros
        st.session_state.pescados_grasos = pescados_grasos
        
        st.markdown('</div>', unsafe_allow_html=True)

    # GRUPO 2: PROTEÍNA ANIMAL MAGRA
    with st.expander("🍗 **GRUPO 2: PROTEÍNA ANIMAL MAGRA**", expanded=True):
        progress.progress(33)
        progress_text.text("Grupo 2 de 6: Proteína animal magra")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (elige todas las que te sean fáciles de consumir)")
        
        st.markdown("#### 🍗 Carnes y cortes magros")
        carnes_magras = st.multiselect(
            "Selecciona las carnes y cortes magros que consumes:",
            ["Pechuga de pollo sin piel", "Filete de res magro (aguayón, bola, sirloin sin grasa visible)", 
             "Lomo de cerdo", "Bistec de res sin grasa visible", "Cecina magra", "Molida 90/10", 
             "Molida 95/5", "Molida 97/3", "Carne para deshebrar sin grasa (falda limpia)"],
            help="Marca todos los que te sean fáciles de consumir"
        )
        
        st.markdown("#### 🐟 Pescados blancos y bajos en grasa")
        pescados_blancos = st.multiselect(
            "Selecciona los pescados blancos y bajos en grasa que consumes:",
            ["Tilapia", "Basa", "Huachinango", "Merluza", "Robalo", "Atún en agua"],
            help="Marca todos los que te sean fáciles de consumir"
        )
        
        st.markdown("#### 🧀 Quesos bajos en grasa o magros")
        quesos_magros = st.multiselect(
            "Selecciona los quesos bajos en grasa que consumes:",
            ["Queso panela", "Queso cottage", "Queso ricotta light", "Queso oaxaca reducido en grasa", 
             "Queso mozzarella light", "Queso fresco bajo en grasa"],
            help="Marca todos los que te sean fáciles de consumir"
        )
        
        st.markdown("#### 🥛 Lácteos light o reducidos")
        lacteos_light = st.multiselect(
            "Selecciona los lácteos light o reducidos que consumes:",
            ["Leche descremada", "Leche deslactosada light", "Leche de almendra sin azúcar", 
             "Leche de coco sin azúcar", "Leche de soya sin azúcar", "Yogur griego natural sin azúcar", 
             "Yogur griego light", "Yogur bebible bajo en grasa", "Yogur sin azúcar añadida", 
             "Yogur de frutas bajo en grasa y sin azúcar añadida", "Queso crema light"],
            help="Marca todos los que te sean fáciles de consumir"
        )
        
        st.markdown("#### 🥚 Otros")
        otros_proteinas_magras = st.multiselect(
            "Selecciona otros productos que consumes:",
            ["Clara de huevo", "Jamón de pechuga de pavo", "Jamón de pierna bajo en grasa", 
             "Salchicha de pechuga de pavo (light)"],
            help="Marca todos los que te sean fáciles de consumir"
        )

        # Guardar en session state
        st.session_state.carnes_magras = carnes_magras
        st.session_state.pescados_blancos = pescados_blancos
        st.session_state.quesos_magros = quesos_magros
        st.session_state.lacteos_light = lacteos_light
        st.session_state.otros_proteinas_magras = otros_proteinas_magras
        
        st.markdown('</div>', unsafe_allow_html=True)

    # GRUPO 3: FUENTES DE GRASA SALUDABLE
    with st.expander("🥑 **GRUPO 3: FUENTES DE GRASA SALUDABLE**", expanded=True):
        progress.progress(50)
        progress_text.text("Grupo 3 de 6: Fuentes de grasa saludable")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (elige todas las que puedas o suelas consumir)")
        
        st.markdown("#### 🥑 Grasas naturales de alimentos")
        grasas_naturales = st.multiselect(
            "Selecciona las grasas naturales que consumes:",
            ["Aguacate", "Yema de huevo", "Aceitunas (negras, verdes)", "Coco rallado natural", 
             "Coco fresco", "Leche de coco sin azúcar"],
            help="Marca todas las que puedas o suelas consumir"
        )
        
        st.markdown("#### 🌰 Frutos secos y semillas")
        frutos_secos_semillas = st.multiselect(
            "Selecciona los frutos secos y semillas que consumes:",
            ["Almendras", "Nueces", "Nuez de la India", "Pistaches", "Cacahuates naturales (sin sal)", 
             "Semillas de chía", "Semillas de linaza", "Semillas de girasol", "Semillas de calabaza (pepitas)"],
            help="Marca todas las que puedas o suelas consumir"
        )
        
        st.markdown("#### 🧈 Mantequillas y pastas vegetales")
        mantequillas_vegetales = st.multiselect(
            "Selecciona las mantequillas y pastas vegetales que consumes:",
            ["Mantequilla de maní natural", "Mantequilla de almendra", "Tahini (pasta de ajonjolí)", 
             "Mantequilla de nuez de la India"],
            help="Marca todas las que puedas o suelas consumir"
        )

        # Guardar en session state
        st.session_state.grasas_naturales = grasas_naturales
        st.session_state.frutos_secos_semillas = frutos_secos_semillas
        st.session_state.mantequillas_vegetales = mantequillas_vegetales
        
        st.markdown('</div>', unsafe_allow_html=True)

    # GRUPO 4: CARBOHIDRATOS COMPLEJOS Y CEREALES
    with st.expander("🍞 **GRUPO 4: CARBOHIDRATOS COMPLEJOS Y CEREALES**", expanded=True):
        progress.progress(67)
        progress_text.text("Grupo 4 de 6: Carbohidratos complejos y cereales")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (elige todos los que consumas con facilidad)")
        
        st.markdown("#### 🌾 Cereales y granos integrales")
        cereales_integrales = st.multiselect(
            "Selecciona los cereales y granos integrales que consumes:",
            ["Avena tradicional", "Avena instantánea sin azúcar", "Arroz integral", "Arroz blanco", 
             "Arroz jazmín", "Arroz basmati", "Trigo bulgur", "Cuscús", "Quinoa", "Amaranto", 
             "Trigo inflado natural", "Cereal de maíz sin azúcar", "Cereal integral bajo en azúcar"],
            help="Marca todos los que consumas con facilidad"
        )
        
        st.markdown("#### 🌽 Tortillas y panes")
        tortillas_panes = st.multiselect(
            "Selecciona las tortillas y panes que consumes:",
            ["Tortilla de maíz", "Tortilla de nopal", "Tortilla integral", "Tortilla de harina", 
             "Tortilla de avena", "Pan integral", "Pan multigrano", "Pan de centeno", 
             "Pan de caja sin azúcar añadida", "Pan pita integral", "Pan tipo Ezekiel (germinado)"],
            help="Marca todos los que consumas con facilidad"
        )
        
        st.markdown("#### 🥔 Raíces, tubérculos y derivados")
        raices_tuberculos = st.multiselect(
            "Selecciona las raíces, tubérculos y derivados que consumes:",
            ["Papa cocida o al horno", "Camote cocido o al horno", "Yuca", "Plátano macho", 
             "Puré de papa", "Papas horneadas", "Papas en air fryer"],
            help="Marca todos los que consumas con facilidad"
        )
        
        st.markdown("#### 🫘 Leguminosas")
        leguminosas = st.multiselect(
            "Selecciona las leguminosas que consumes:",
            ["Frijoles negros", "Frijoles bayos", "Frijoles pintos", "Lentejas", "Garbanzos", 
             "Habas cocidas", "Soya texturizada", "Edamames (vainas de soya)", "Hummus (puré de garbanzo)"],
            help="Marca todos los que consumas con facilidad"
        )

        # Guardar en session state
        st.session_state.cereales_integrales = cereales_integrales
        st.session_state.tortillas_panes = tortillas_panes
        st.session_state.raices_tuberculos = raices_tuberculos
        st.session_state.leguminosas = leguminosas
        
        st.markdown('</div>', unsafe_allow_html=True)

    # GRUPO 5: VEGETALES
    with st.expander("🥬 **GRUPO 5: VEGETALES**", expanded=True):
        progress.progress(83)
        progress_text.text("Grupo 5 de 6: Vegetales")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (elige todos los que consumes o toleras fácilmente)")
        
        vegetales_lista = st.multiselect(
            "Selecciona todos los vegetales que consumes o toleras fácilmente:",
            ["Espinaca", "Acelga", "Kale", "Lechuga (romana, italiana, orejona, iceberg)", 
             "Col morada", "Col verde", "Repollo", "Brócoli", "Coliflor", "Ejote", "Chayote", 
             "Calabacita", "Nopal", "Betabel", "Zanahoria", "Jitomate saladet", "Jitomate bola", 
             "Tomate verde", "Cebolla blanca", "Cebolla morada", "Pimiento morrón (rojo, verde, amarillo, naranja)", 
             "Pepino", "Apio", "Rábano", "Ajo", "Berenjena", "Champiñones", "Guisantes (chícharos)", 
             "Verdolaga", "Habas tiernas", "Germen de alfalfa", "Germen de soya", "Flor de calabaza"],
            help="Marca todos los que consumes o toleras fácilmente"
        )

        # Guardar en session state
        st.session_state.vegetales_lista = vegetales_lista
        
        st.markdown('</div>', unsafe_allow_html=True)

    # GRUPO 6: FRUTAS
    with st.expander("🍎 **GRUPO 6: FRUTAS**", expanded=True):
        progress.progress(100)
        progress_text.text("Grupo 6 de 6: Frutas")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (elige todas las que disfrutes o toleres bien)")
        
        frutas_lista = st.multiselect(
            "Selecciona todas las frutas que disfrutas o toleras bien:",
            ["Manzana (roja, verde, gala, fuji)", "Naranja", "Mandarina", "Mango (petacón, ataulfo)", 
             "Papaya", "Sandía", "Melón", "Piña", "Plátano (tabasco, dominico, macho)", "Uvas", 
             "Fresas", "Arándanos", "Zarzamoras", "Frambuesas", "Higo", "Kiwi", "Pera", "Durazno", 
             "Ciruela", "Granada", "Cereza", "Chabacano", "Lima", "Limón", "Guayaba", "Tuna", 
             "Níspero", "Mamey", "Pitahaya (dragon fruit)", "Tamarindo", "Coco (carne, rallado)", 
             "Caqui (persimón)", "Maracuyá", "Manzana en puré sin azúcar", "Fruta en almíbar light"],
            help="Marca todas las que disfrutes o toleres bien"
        )

        # Guardar en session state
        st.session_state.frutas_lista = frutas_lista
        
        st.markdown('</div>', unsafe_allow_html=True)

    # APARTADO EXTRA: GRASA/ACEITE DE COCCIÓN FAVORITA
    with st.expander("🍳 **APARTADO EXTRA: GRASA/ACEITE DE COCCIÓN FAVORITA**", expanded=True):
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (elige todas las opciones que suelas usar para cocinar, freír, hornear o saltear tus alimentos)")
        
        aceites_coccion = st.multiselect(
            "Selecciona las grasas/aceites de cocción que usas:",
            ["🫒 Aceite de oliva extra virgen", "🥑 Aceite de aguacate", "🥥 Aceite de coco virgen", 
             "🧈 Mantequilla con sal", "🧈 Mantequilla sin sal", "🧈 Mantequilla clarificada (ghee)", 
             "🐷 Manteca de cerdo (casera o artesanal)", "🧴 Spray antiadherente sin calorías (aceite de oliva o aguacate)", 
             "❌ Prefiero cocinar sin aceite o con agua"],
            help="Marca todas las opciones que suelas usar"
        )

        # Guardar en session state
        st.session_state.aceites_coccion = aceites_coccion
        
        st.markdown('</div>', unsafe_allow_html=True)

    # BEBIDAS SIN CALORÍAS
    with st.expander("🥤 **¿Qué bebidas sin calorías sueles consumir regularmente para hidratarte?**", expanded=True):
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### (Marca todas las que acostumbres)")
        
        bebidas_sin_calorias = st.multiselect(
            "Selecciona las bebidas sin calorías que consumes:",
            ["💧 Agua natural", "💦 Agua mineral", "⚡ Bebidas con electrolitos sin azúcar (Electrolit Zero, SueroX, LMNT, etc.)", 
             "🍋 Agua infusionada con frutas naturales (limón, pepino, menta, etc.)", 
             "🍵 Té de hierbas sin azúcar (manzanilla, menta, jengibre, etc.)", 
             "🍃 Té verde o té negro sin azúcar", "☕ Café negro sin azúcar", 
             "🥤 Refrescos sin calorías (Coca Cola Zero, Pepsi Light, etc.)"],
            help="Marca todas las que acostumbres"
        )

        # Guardar en session state
        st.session_state.bebidas_sin_calorias = bebidas_sin_calorias
        
        st.markdown('</div>', unsafe_allow_html=True)

    # SECCIÓN FINAL: ALERGIAS, INTOLERANCIAS Y PREFERENCIAS
    with st.expander("🚨 **SECCIÓN FINAL: ALERGIAS, INTOLERANCIAS Y PREFERENCIAS**", expanded=True):
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.markdown("### ❗ 1. ¿Tienes alguna alergia alimentaria? (Marca todas las que apliquen)")
        alergias_alimentarias = st.multiselect(
            "Selecciona las alergias alimentarias que tienes:",
            ["Lácteos", "Huevo", "Frutos secos", "Mariscos", "Pescado", "Gluten", "Soya", "Semillas"],
            help="Marca todas las que apliquen"
        )
        
        otra_alergia = st.text_input(
            "Otra (especificar):",
            placeholder="Especifica otra alergia alimentaria",
            help="Si tienes otra alergia, especifícala aquí"
        )
        
        st.markdown("---")
        st.markdown("### ⚠️ 2. ¿Tienes alguna intolerancia o malestar digestivo?")
        intolerancias_digestivas = st.multiselect(
            "Selecciona las intolerancias que tienes:",
            ["Lácteos con lactosa", "Leguminosas", "FODMAPs", "Gluten", "Crucíferas", "Endulzantes artificiales"],
            help="Marca todas las que apliquen"
        )
        
        otra_intolerancia = st.text_input(
            "Otra (especificar):",
            placeholder="Especifica otra intolerancia",
            help="Si tienes otra intolerancia, especifícala aquí"
        )
        
        st.markdown("---")
        st.markdown("### ➕ 3. ¿Hay algún alimento o bebida que desees incluir, aunque no aparezca en las listas anteriores?")
        alimento_adicional = st.text_area(
            "Escribe aquí:",
            placeholder="Especifica alimentos o bebidas adicionales que consumes",
            help="Menciona cualquier alimento importante que no esté en las listas"
        )
        
        st.markdown("---")
        st.markdown("### ➕4. ¿Métodos de cocción más accesibles para tu día a día?")
        st.markdown("**Selecciona los métodos de cocción que más usas o prefieres para preparar tus alimentos:**")
        
        metodos_coccion_accesibles = st.multiselect(
            "Métodos de cocción preferidos:",
            ["☐ A la plancha", "☐ A la parrilla", "☐ Hervido", "☐ Al vapor", "☐ Horneado / al horno", 
             "☐ Air fryer (freidora de aire)", "☐ Microondas", "☐ Salteado (con poco aceite)"],
            help="Selecciona todos los métodos que uses regularmente"
        )
        
        otro_metodo_coccion = st.text_input(
            "☐ Otro:",
            placeholder="Especifica otro método de cocción",
            help="Si usas otro método, especifícalo aquí"
        )

        # Guardar en session state
        st.session_state.alergias_alimentarias = alergias_alimentarias
        st.session_state.otra_alergia = otra_alergia
        st.session_state.intolerancias_digestivas = intolerancias_digestivas
        st.session_state.otra_intolerancia = otra_intolerancia
        st.session_state.alimento_adicional = alimento_adicional
        st.session_state.metodos_coccion_accesibles = metodos_coccion_accesibles
        st.session_state.otro_metodo_coccion = otro_metodo_coccion
        
        st.markdown('</div>', unsafe_allow_html=True)

    # SECCIÓN DE ANTOJOS ALIMENTARIOS
    with st.expander("😋 **SECCIÓN DE ANTOJOS ALIMENTARIOS**", expanded=True):
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### Instrucciones: Marca los alimentos que frecuentemente se te antojan o deseas con intensidad, aunque no necesariamente los consumas con regularidad. Puedes marcar tantos como necesites.")
        
        st.markdown("---")
        st.markdown("### 🍫 Alimentos dulces / postres")
        antojos_dulces = st.multiselect(
            "Selecciona los alimentos dulces que se te antojan:",
            ["Chocolate con leche", "Chocolate amargo", "Pan dulce (conchas, donas, cuernitos)", 
             "Pastel (tres leches, chocolate, etc.)", "Galletas (Marías, Emperador, Chokis, etc.)", 
             "Helado / Nieve", "Flan / Gelatina", "Dulces tradicionales (cajeta, obleas, jamoncillo, glorias)", 
             "Cereal azucarado", "Leche condensada", "Churros"],
            help="Marca todos los que frecuentemente se te antojen"
        )
        
        st.markdown("---")
        st.markdown("### 🧂 Alimentos salados / snacks")
        antojos_salados = st.multiselect(
            "Selecciona los alimentos salados que se te antojan:",
            ["Papas fritas (Sabritas, Ruffles, etc.)", "Cacahuates enchilados", "Frituras (Doritos, Cheetos, Takis, etc.)", 
             "Totopos con salsa", "Galletas saladas", "Cacahuates japoneses", "Chicharrón (de cerdo o harina)", 
             "Nachos con queso", "Queso derretido o gratinado"],
            help="Marca todos los que frecuentemente se te antojen"
        )
        
        st.markdown("---")
        st.markdown("### 🌮 Comidas rápidas / callejeras")
        antojos_comida_rapida = st.multiselect(
            "Selecciona las comidas rápidas que se te antojan:",
            ["Tacos (pastor, asada, birria, etc.)", "Tortas (cubana, ahogada, etc.)", "Hamburguesas", "Hot dogs", 
             "Pizza", "Quesadillas fritas", "Tamales", "Pambazos", "Sopes / gorditas", "Elotes / esquites", 
             "Burritos", "Enchiladas", "Empanadas"],
            help="Marca todos los que frecuentemente se te antojen"
        )
        
        st.markdown("---")
        st.markdown("### 🍹 Bebidas y postres líquidos")
        antojos_bebidas = st.multiselect(
            "Selecciona las bebidas que se te antojan:",
            ["Refrescos regulares (Coca-Cola, Fanta, etc.)", "Jugos industrializados (Boing, Jumex, etc.)", 
             "Malteadas / Frappés", "Agua de sabor con azúcar (jamaica, horchata, tamarindo)", 
             "Café con azúcar y leche", "Champurrado / atole", "Licuado de plátano con azúcar", 
             "Bebidas alcohólicas (cerveza, tequila, vino, etc.)"],
            help="Marca todos los que frecuentemente se te antojen"
        )
        
        st.markdown("---")
        st.markdown("### 🔥 Alimentos con condimentos estimulantes")
        antojos_picantes = st.multiselect(
            "Selecciona los alimentos con condimentos que se te antojan:",
            ["Chiles en escabeche", "Salsas picantes", "Salsa Valentina, Tajín o Chamoy", 
             "Pepinos con chile y limón", "Mangos verdes con chile", "Gomitas enchiladas", 
             "Fruta con Miguelito o chile en polvo"],
            help="Marca todos los que frecuentemente se te antojen"
        )
        
        st.markdown("---")
        st.markdown("### ❓ Pregunta final:")
        st.markdown("**¿Qué otros alimentos o preparaciones se te antojan mucho y no aparecen en esta lista?**")
        otros_antojos = st.text_area(
            "👉 Escríbelos aquí:",
            placeholder="Especifica otros alimentos que se te antojen frecuentemente",
            help="Menciona cualquier antojo que no esté en las listas anteriores"
        )

        # Guardar en session state
        st.session_state.antojos_dulces = antojos_dulces
        st.session_state.antojos_salados = antojos_salados
        st.session_state.antojos_comida_rapida = antojos_comida_rapida
        st.session_state.antojos_bebidas = antojos_bebidas
        st.session_state.antojos_picantes = antojos_picantes
        st.session_state.otros_antojos = otros_antojos
        
        st.markdown('</div>', unsafe_allow_html=True)

    # RESULTADO FINAL: Análisis completo del nuevo cuestionario
    with st.expander("📈 **RESULTADO FINAL: Tu Perfil Alimentario Completo**", expanded=True):
        progress.progress(100)
        progress_text.text("Análisis completo: Generando tu perfil alimentario personalizado")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.markdown("### 🎯 Tu Perfil Alimentario Personalizado")
        
        # Crear resumen del perfil por grupos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Grupo 1: Información Básica")
            st.write(f"• **Comidas por día:** {st.session_state.get('comidas_por_dia_actual', 'No especificado')}")
            st.write(f"• **Objetivo principal:** {st.session_state.get('peso_objetivo', 'No especificado')}")
            st.write(f"• **Nivel de energía:** {st.session_state.get('energia_nivel', 'No especificado')}")
            st.write(f"• **Ejercicio:** {st.session_state.get('ejercicio_frecuencia', 'No especificado')}")
            
            st.markdown("#### 🥩 Grupo 2: Proteínas")
            if st.session_state.get('proteinas_animales'):
                proteinas_lista = st.session_state.get('proteinas_animales', [])
                st.write(f"• **Proteínas animales:** {', '.join(proteinas_lista[:3])}{'...' if len(proteinas_lista) > 3 else ''}")
            if st.session_state.get('proteinas_vegetales'):
                proteinas_veg_lista = st.session_state.get('proteinas_vegetales', [])
                st.write(f"• **Proteínas vegetales:** {', '.join(proteinas_veg_lista[:3])}{'...' if len(proteinas_veg_lista) > 3 else ''}")
            
            st.markdown("#### 🥑 Grupo 3: Grasas Saludables")
            if st.session_state.get('grasas_vegetales'):
                grasas_veg_lista = st.session_state.get('grasas_vegetales', [])
                st.write(f"• **Grasas vegetales:** {', '.join(grasas_veg_lista[:3])}{'...' if len(grasas_veg_lista) > 3 else ''}")
            if st.session_state.get('grasas_animales'):
                grasas_an_lista = st.session_state.get('grasas_animales', [])
                st.write(f"• **Grasas animales:** {', '.join(grasas_an_lista[:3])}{'...' if len(grasas_an_lista) > 3 else ''}")
        
        with col2:
            st.markdown("#### 🍞 Grupo 4: Carbohidratos")
            if st.session_state.get('cereales_granos'):
                cereales_lista = st.session_state.get('cereales_granos', [])
                st.write(f"• **Cereales:** {', '.join(cereales_lista[:3])}{'...' if len(cereales_lista) > 3 else ''}")
            st.write(f"• **Frutas:** {st.session_state.get('frutas_consumo', 'No especificado')}")
            st.write(f"• **Vegetales:** {st.session_state.get('vegetales_consumo', 'No especificado')}")
            
            st.markdown("#### 🥤 Grupo 5: Hidratación")
            st.write(f"• **Agua diaria:** {st.session_state.get('agua_pura_consumo', 'No especificado')}")
            st.write(f"• **Cafeína:** {st.session_state.get('frecuencia_cafeina', 'No especificado')}")
            st.write(f"• **Alcohol:** {st.session_state.get('consumo_alcohol', 'No especificado')}")
            
            st.markdown("#### 💊 Grupo 6: Suplementos")
            st.write(f"• **Usa suplementos:** {st.session_state.get('usa_suplementos', 'No especificado')}")
            st.write(f"• **Productos especiales:** {st.session_state.get('frecuencia_productos_especiales', 'No especificado')}")

        # Sección de métodos de cocción
        st.markdown("#### 👨‍🍳 Métodos de Cocción")
        if st.session_state.get('metodos_disponibles'):
            metodos_lista = st.session_state.get('metodos_disponibles', [])
            st.write(f"• **Disponibles:** {', '.join(metodos_lista[:5])}{'...' if len(metodos_lista) > 5 else ''}")
        if st.session_state.get('metodos_practicos'):
            metodos_prac_lista = st.session_state.get('metodos_practicos', [])
            st.write(f"• **Más prácticos:** {', '.join(metodos_prac_lista[:3])}{'...' if len(metodos_prac_lista) > 3 else ''}")

        # Restricciones importantes
        if (st.session_state.get('tiene_alergias') and st.session_state.get('tiene_alergias') != "No tengo alergias") or (st.session_state.get('tiene_intolerancias') and st.session_state.get('tiene_intolerancias') != "No tengo intolerancias"):
            st.markdown("#### ⚠️ Restricciones Importantes")
            if st.session_state.get('tiene_alergias') and st.session_state.get('tiene_alergias') != "No tengo alergias":
                st.warning(f"**Alergias:** {st.session_state.get('tiene_alergias')}")
                if st.session_state.get('alergias_especificas'):
                    alergias_lista = st.session_state.get('alergias_especificas', [])
                    st.write(f"• **Específicas:** {', '.join(alergias_lista)}")
            
            if st.session_state.get('tiene_intolerancias') and st.session_state.get('tiene_intolerancias') != "No tengo intolerancias":
                st.info(f"**Intolerancias:** {st.session_state.get('tiene_intolerancias')}")
                if st.session_state.get('intolerancias_especificas'):
                    intol_lista = st.session_state.get('intolerancias_especificas', [])
                    st.write(f"• **Específicas:** {', '.join(intol_lista)}")

        # Preferencias y antojos
        st.markdown("### 😋 Patrones de Preferencias y Antojos")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.get('sabores_favoritos'):
                sabores_lista = st.session_state.get('sabores_favoritos', [])
                st.write(f"• **Sabores favoritos:** {', '.join(sabores_lista)}")
            if st.session_state.get('comidas_comfort'):
                comidas_text = st.session_state.get('comidas_comfort', '')
                st.write(f"• **Comidas favoritas:** {comidas_text[:100]}{'...' if len(comidas_text) > 100 else ''}")
            st.write(f"• **Curiosidad alimentaria:** {st.session_state.get('curiosidad_alimentaria', 'No especificado')}")
        
        with col2:
            st.write(f"• **Frecuencia antojos:** {st.session_state.get('frecuencia_antojos', 'No especificado')}")
            if st.session_state.get('tipos_antojos') and "No tengo antojos específicos" not in st.session_state.get('tipos_antojos', []):
                antojos_lista = st.session_state.get('tipos_antojos', [])
                st.write(f"• **Tipos de antojos:** {', '.join(antojos_lista[:3])}{'...' if len(antojos_lista) > 3 else ''}")
            st.write(f"• **Control antojos:** {st.session_state.get('control_antojos', 'No especificado')}")

        # Contexto personal
        st.markdown("### 🏠 Contexto Personal")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"• **Situación familiar:** {st.session_state.get('situacion_familiar', 'No especificado')}")
            st.write(f"• **Quién cocina:** {st.session_state.get('quien_cocina', 'No especificado')}")
            st.write(f"• **Presupuesto:** {st.session_state.get('presupuesto_comida', 'No especificado')}")
        
        with col2:
            st.write(f"• **Horarios trabajo:** {st.session_state.get('trabajo_horarios', 'No especificado')}")
            st.write(f"• **Eventos sociales:** {st.session_state.get('eventos_sociales', 'No especificado')}")
            st.write(f"• **Objetivo específico:** {st.session_state.get('objetivo_principal_detallado', 'No especificado')}")

        # Recomendaciones personalizadas
        st.markdown("### 💡 Recomendaciones Personalizadas Iniciales")
        
        # Análisis básico basado en las respuestas
        recomendaciones = []
        
        if st.session_state.get('agua_pura_consumo') in ["Menos de 1 litro", "1-1.5 litros"]:
            recomendaciones.append("💧 **Hidratación:** Incrementar el consumo de agua pura gradualmente hasta alcanzar 2-2.5 litros diarios.")
        
        if st.session_state.get('vegetales_consumo') in ["No como vegetales", "1 porción"]:
            recomendaciones.append("🥬 **Vegetales:** Incorporar más vegetales variados, comenzando con los que más te gusten.")
        
        if (st.session_state.get('frecuencia_antojos') in ["Diariamente", "Varias veces al día"]) and (st.session_state.get('control_antojos') in ["Muy difícil, casi siempre cedo", "Imposible, siempre cedo a los antojos"]):
            recomendaciones.append("🧠 **Antojos:** Desarrollar estrategias específicas para manejar antojos, incluyendo alternativas saludables.")
        
        if st.session_state.get('ejercicio_frecuencia') == "No hago ejercicio":
            recomendaciones.append("🏃 **Actividad:** Incorporar actividad física gradual que complemente el plan nutricional.")
        
        if st.session_state.get('metodos_disponibles') and len(st.session_state.get('metodos_disponibles', [])) >= 5:
            recomendaciones.append("👨‍🍳 **Cocina:** Aprovechar la variedad de métodos de cocción disponibles para crear más opciones saludables.")
        
        if not recomendaciones:
            recomendaciones.append("✅ **Perfil balanceado:** Tu perfil muestra buenos hábitos base. Enfocaremos en optimización y personalización.")
        
        for i, rec in enumerate(recomendaciones, 1):
            st.write(f"{i}. {rec}")

        st.success(f"""
        ### ✅ Análisis de patrones alimentarios completado exitosamente
        
        **Tu perfil nutricional personalizado está listo** y incluye información detallada sobre:
        - 6 grupos alimentarios principales
        - Métodos de cocción disponibles y preferidos  
        - Restricciones, alergias e intolerancias
        - Patrones de preferencias y antojos
        - Contexto personal y familiar
        
        **Este análisis integral permitirá crear un plan nutricional completamente adaptado** 
        a tu estilo de vida, preferencias y necesidades específicas.
        
        La información será enviada a nuestro equipo de nutrición para desarrollar tu plan personalizado.
        """)

        st.markdown('</div>', unsafe_allow_html=True)

    # RESULTADO FINAL: Análisis de patrones alimentarios
    with st.expander("📈 **RESULTADO FINAL: Tu Perfil Alimentario Personalizado**", expanded=True):
        progress.progress(100)
        progress_text.text("Análisis completo: Generando tu perfil alimentario personalizado")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.markdown("### 🎯 Tu Perfil Alimentario Personalizado")
        
        # Crear resumen del perfil
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Perfil Personal")
            st.write(f"• **Nombre:** {nombre}")
            st.write(f"• **Edad:** {edad} años")
            st.write(f"• **Sexo:** {sexo}")
            st.write(f"• **Origen cultural:** {origen_cultural if origen_cultural else 'No especificado'}")
            
            st.markdown("#### 🥗 Preferencias Principales")
            if sabores_preferidos:
                st.write(f"• **Sabores favoritos:** {', '.join(sabores_preferidos)}")
            if texturas_preferidas:
                st.write(f"• **Texturas preferidas:** {', '.join(texturas_preferidas)}")
            if patron_dietetico != "Ninguno en particular":
                st.write(f"• **Patrón dietético:** {patron_dietetico}")
                if motivacion_patron:
                    st.write(f"• **Motivación:** {motivacion_patron}")
        
        with col2:
            st.markdown("#### ⏰ Patrones Temporales")
            st.write(f"• **Comidas por día:** {comidas_por_dia}")
            st.write(f"• **Desayuno:** {horario_desayuno}")
            st.write(f"• **Almuerzo:** {horario_almuerzo}")
            st.write(f"• **Cena:** {horario_cena}")
            st.write(f"• **Frecuencia de snacks:** {snacks_frecuencia}")
            
            st.markdown("#### 👨‍🍳 Habilidades Culinarias")
            st.write(f"• **Nivel de cocina:** {nivel_cocina}")
            st.write(f"• **Tiempo disponible:** {tiempo_cocinar_dia}")
            st.write(f"• **Frecuencia cocina casa:** {frecuencia_cocina_casa}")

        # Análisis de restricciones
        if tiene_alergias != "No":
            st.markdown("#### ⚠️ Restricciones Importantes")
            st.warning(f"**Alergias/Intolerancias:** {tiene_alergias}")
            if alergias_especificas:
                st.write(f"• **Detalles:** {alergias_especificas}")

        # Recomendaciones personalizadas basadas en las respuestas
        st.markdown("### 💡 Recomendaciones Personalizadas")
        
        # Análisis del nivel de cocina para recomendaciones
        if nivel_cocina.startswith("Principiante"):
            recomendacion_cocina = "Enfócate en recetas simples de 3-5 ingredientes. Considera meal prep básico los fines de semana."
        elif nivel_cocina.startswith("Básico"):
            recomendacion_cocina = "Puedes explorar técnicas nuevas gradualmente. Ideal para batch cooking y preparaciones versátiles."
        elif nivel_cocina.startswith("Intermedio"):
            recomendacion_cocina = "Tienes base sólida para experimentar con sabores internacionales y técnicas más avanzadas."
        else:
            recomendacion_cocina = "Tu nivel avanzado te permite crear platos complejos. Considera explorar cocina molecular o técnicas especializadas."

        # Análisis del tiempo disponible
        if tiempo_cocinar_dia == "Menos de 15 minutos":
            recomendacion_tiempo = "Prioriza meal prep, alimentos pre-cortados y técnicas de cocción rápida como salteados."
        elif tiempo_cocinar_dia == "15-30 minutos":
            recomendacion_tiempo = "Tiempo ideal para platos balanceados. Una olla/sartén puede ser tu mejor estrategia."
        else:
            recomendacion_tiempo = "Tienes flexibilidad para explorar técnicas que requieren más tiempo como guisos, horneados o fermentaciones."

        # Mostrar recomendaciones
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
            **💻 Recomendación por nivel de cocina:**
            {recomendacion_cocina}
            """)
        with col2:
            st.info(f"""
            **⏱️ Recomendación por tiempo disponible:**
            {recomendacion_tiempo}
            """)

        # Objetivos y próximos pasos
        st.markdown("### 🎯 Próximos Pasos Recomendados")
        
        objetivos_texto = ""
        if objetivo_principal == "Perder peso":
            objetivos_texto = "Enfoque en preparaciones bajas en calorías pero satisfactorias, control de porciones y planificación de comidas."
        elif objetivo_principal == "Ganar peso/músculo":
            objetivos_texto = "Prioriza alimentos densos en nutrientes, aumenta frecuencia de comidas y incluye snacks nutritivos."
        elif objetivo_principal == "Mejorar energía y bienestar":
            objetivos_texto = "Enfócate en alimentos integrales, hidratación adecuada y horarios regulares de comida."
        else:
            objetivos_texto = "Plan balanceado enfocado en variedad nutricional y sostenibilidad a largo plazo."

        st.success(f"""
        ### ✅ Análisis completado exitosamente
        
        **Tu objetivo principal:** {objetivo_principal}
        
        **Estrategia recomendada:** {objetivos_texto}
        
        **Nivel de personalización:** Alto - basado en {len([x for x in [sabores_preferidos, texturas_preferidas, patron_dietetico, nivel_cocina] if x])} factores clave analizados.
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
st.markdown(f"*Fecha: {fecha_llenado} | Cliente: {nombre}*")

# Mostrar métricas finales
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    ### 🥗 Preferencias
    - **Sabores principales:** {len(st.session_state.get('sabores_preferidos', []))} identificados
    - **Patrón dietético:** {st.session_state.get('patron_dietetico', 'Estándar')}
    - **Restricciones:** {'Sí' if st.session_state.get('tiene_alergias', 'No') != 'No' else 'No'}
    """)

with col2:
    st.markdown(f"""
    ### ⏰ Patrones Temporales  
    - **Comidas/día:** {st.session_state.get('comidas_por_dia', 'No especificado')}
    - **Horarios:** {'Regulares' if not st.session_state.get('horarios_irregulares') else 'Irregulares'}
    - **Snacks:** {st.session_state.get('snacks_frecuencia', 'No especificado')}
    """)

with col3:
    st.markdown(f"""
    ### 👨‍🍳 Habilidades
    - **Nivel cocina:** {st.session_state.get('nivel_cocina', 'No especificado')}
    - **Tiempo disponible:** {st.session_state.get('tiempo_cocinar_dia', 'No especificado')}
    - **Objetivo:** {st.session_state.get('objetivo_principal', 'No especificado')}
    """)

st.success(f"""
### ✅ Evaluación de patrones alimentarios completada exitosamente

Tu perfil alimentario ha sido analizado considerando todos los factores evaluados: preferencias, 
restricciones, habilidades culinarias, patrones temporales y contexto cultural. 

**Este análisis proporciona la base para desarrollar recomendaciones nutricionales personalizadas** 
que se ajusten a tu estilo de vida y preferencias individuales.

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
