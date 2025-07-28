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

    # BLOQUE 1: Preferencias alimentarias básicas
    with st.expander("🥗 **Paso 1: Preferencias Alimentarias Básicas**", expanded=True):
        progress.progress(16)
        progress_text.text("Paso 1 de 6: Evaluación de preferencias alimentarias")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🍽️ Preferencias de sabores y texturas")
        
        col1, col2 = st.columns(2)
        with col1:
            sabores_preferidos = st.multiselect(
                "Sabores que más disfrutas:",
                ["Dulce", "Salado", "Ácido", "Amargo", "Umami", "Picante", "Especiado", "Ahumado", "Suave/Neutro"],
                help="Selecciona todos los sabores que te agraden"
            )
            
            texturas_preferidas = st.multiselect(
                "Texturas que prefieres:",
                ["Crujiente", "Suave", "Cremosa", "Fibrosa", "Gelatinosa", "Líquida", "Densa", "Aireada"],
                help="Elige las texturas que más disfrutas en los alimentos"
            )
        
        with col2:
            temperaturas_preferidas = st.multiselect(
                "Temperaturas de comida preferidas:",
                ["Muy caliente", "Caliente", "Tibia", "Temperatura ambiente", "Fría", "Muy fría/Helada"],
                help="¿A qué temperatura prefieres consumir tus alimentos?"
            )
            
            comidas_favoritas = st.text_area(
                "Menciona 5 de tus comidas favoritas:",
                placeholder="Ej: Pizza, ensalada césar, sushi, tacos, helado de vainilla...",
                help="Describe brevemente tus platillos favoritos"
            )

        st.markdown("### 🚫 Alimentos que evitas o no te gustan")
        alimentos_evitados = st.text_area(
            "¿Hay alimentos que evitas por gusto personal?",
            placeholder="Ej: brócoli, pescado, comida muy picante, lácteos...",
            help="Lista alimentos que no consumes por preferencia personal"
        )
        
        # Guardar en session state
        st.session_state.sabores_preferidos = sabores_preferidos
        st.session_state.texturas_preferidas = texturas_preferidas
        st.session_state.temperaturas_preferidas = temperaturas_preferidas
        st.session_state.comidas_favoritas = comidas_favoritas
        st.session_state.alimentos_evitados = alimentos_evitados
        
        st.markdown('</div>', unsafe_allow_html=True)

    # BLOQUE 2: Restricciones dietéticas y médicas
    with st.expander("🚫 **Paso 2: Restricciones Dietéticas y Alergias**", expanded=True):
        progress.progress(32)
        progress_text.text("Paso 2 de 6: Evaluación de restricciones y alergias")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Alergias e intolerancias alimentarias")
        
        tiene_alergias = st.radio(
            "¿Tienes alergias o intolerancias alimentarias?",
            ["No", "Sí, tengo alergias", "Sí, tengo intolerancias", "Sí, tengo ambas"],
            help="Las alergias causan reacciones inmunes; las intolerancias causan malestar digestivo"
        )
        
        alergias_especificas = ""
        if tiene_alergias != "No":
            alergias_especificas = st.text_area(
                "Describe específicamente tus alergias e intolerancias:",
                placeholder="Ej: Alergia a frutos secos, intolerancia a lactosa, celiaquía...",
                help="Sé específico para crear un plan seguro"
            )
        
        st.markdown("### 🥗 Patrones dietéticos especiales")
        patron_dietetico = st.selectbox(
            "¿Sigues algún patrón dietético específico?",
            ["Ninguno en particular", "Vegetariano", "Vegano", "Pescetariano", "Flexitariano", 
             "Cetogénico", "Paleo", "Mediterráneo", "Bajo en carbohidratos", "Ayuno intermitente",
             "Sin gluten", "Bajo en FODMAP", "Otro"],
            help="Selecciona el patrón que mejor describe tu alimentación actual"
        )
        
        patron_otro = ""
        if patron_dietetico == "Otro":
            patron_otro = st.text_input(
                "Especifica tu patrón dietético:",
                placeholder="Describe tu patrón alimentario...",
                help="Detalla tu enfoque dietético específico"
            )
        
        motivacion_patron = ""
        if patron_dietetico != "Ninguno en particular":
            motivacion_patron = st.selectbox(
                "¿Cuál es tu motivación principal para seguir este patrón?",
                ["Salud general", "Pérdida de peso", "Ganancia muscular", "Rendimiento deportivo",
                 "Razones éticas/morales", "Razones ambientales", "Tradición cultural/familiar",
                 "Recomendación médica", "Otra"],
                help="Entender la motivación ayuda a personalizar mejor las recomendaciones"
            )
        
        # Guardar en session state
        st.session_state.tiene_alergias = tiene_alergias
        st.session_state.alergias_especificas = alergias_especificas
        st.session_state.patron_dietetico = patron_dietetico
        st.session_state.patron_otro = patron_otro
        st.session_state.motivacion_patron = motivacion_patron
        
        st.markdown('</div>', unsafe_allow_html=True)

    # BLOQUE 3: Patrones de comida y horarios
    with st.expander("⏰ **Paso 3: Patrones de Comida y Horarios**", expanded=True):
        progress.progress(48)
        progress_text.text("Paso 3 de 6: Evaluación de patrones temporales")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🕐 Frecuencia y horarios de comida")
        
        col1, col2 = st.columns(2)
        with col1:
            comidas_por_dia = st.selectbox(
                "¿Cuántas comidas haces al día normalmente?",
                ["1-2 comidas", "3 comidas", "4-5 comidas", "6 o más comidas", "Variable/Irregular"],
                help="Incluye comidas principales y snacks"
            )
            
            horario_desayuno = st.time_input(
                "Hora habitual de desayuno:",
                value=datetime.strptime("07:00", "%H:%M").time(),
                help="¿A qué hora sueles desayunar?"
            )
            
            horario_almuerzo = st.time_input(
                "Hora habitual de almuerzo:",
                value=datetime.strptime("13:00", "%H:%M").time(),
                help="¿A qué hora sueles almorzar?"
            )
        
        with col2:
            horario_cena = st.time_input(
                "Hora habitual de cena:",
                value=datetime.strptime("19:00", "%H:%M").time(),
                help="¿A qué hora sueles cenar?"
            )
            
            snacks_frecuencia = st.selectbox(
                "¿Con qué frecuencia consumes snacks entre comidas?",
                ["Nunca", "Rara vez", "Ocasionalmente", "Frecuentemente", "Siempre"],
                help="Considera refrigerios, botanas, colaciones"
            )
            
            horarios_irregulares = st.checkbox(
                "Mis horarios de comida son muy irregulares debido al trabajo/estudio",
                help="Marca si tus horarios cambian constantemente"
            )

        st.markdown("### 🍽️ Comportamientos alimentarios")
        
        col1, col2 = st.columns(2)
        with col1:
            come_viendo_tv = st.checkbox("Suelo comer viendo TV/pantallas")
            come_rapido = st.checkbox("Como muy rápido habitualmente")
            saltea_comidas = st.checkbox("Frecuentemente me salteo comidas")
            come_tarde_noche = st.checkbox("Como frecuentemente tarde en la noche")
        
        with col2:
            come_estresado = st.checkbox("Como más cuando estoy estresado/ansioso")
            come_aburrido = st.checkbox("Como por aburrimiento")
            planifica_comidas = st.checkbox("Planifico mis comidas con anticipación")
            come_social = st.checkbox("La mayoría de mis comidas son en contextos sociales")

        # Guardar en session state
        st.session_state.comidas_por_dia = comidas_por_dia
        st.session_state.horario_desayuno = horario_desayuno
        st.session_state.horario_almuerzo = horario_almuerzo
        st.session_state.horario_cena = horario_cena
        st.session_state.snacks_frecuencia = snacks_frecuencia
        st.session_state.horarios_irregulares = horarios_irregulares
        st.session_state.comportamientos_alimentarios = {
            "come_viendo_tv": come_viendo_tv,
            "come_rapido": come_rapido,
            "saltea_comidas": saltea_comidas,
            "come_tarde_noche": come_tarde_noche,
            "come_estresado": come_estresado,
            "come_aburrido": come_aburrido,
            "planifica_comidas": planifica_comidas,
            "come_social": come_social
        }
        
        st.markdown('</div>', unsafe_allow_html=True)

    # BLOQUE 4: Habilidades culinarias y preparación
    with st.expander("👨‍🍳 **Paso 4: Habilidades Culinarias y Preparación**", expanded=True):
        progress.progress(64)
        progress_text.text("Paso 4 de 6: Evaluación de habilidades culinarias")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🔪 Nivel de habilidades culinarias")
        
        nivel_cocina = st.selectbox(
            "¿Cómo calificarías tu nivel de cocina?",
            ["Principiante (apenas cocino)", "Básico (platos simples)", "Intermedio (variedad de platos)", 
             "Avanzado (técnicas complejas)", "Experto (como chef profesional)"],
            help="Sé honesto sobre tus habilidades actuales"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            tiempo_cocinar_dia = st.selectbox(
                "¿Cuánto tiempo puedes dedicar a cocinar por día?",
                ["Menos de 15 minutos", "15-30 minutos", "30-60 minutos", "1-2 horas", "Más de 2 horas"],
                help="Considera tiempo de preparación y cocción"
            )
            
            frecuencia_cocina_casa = st.selectbox(
                "¿Con qué frecuencia cocinas en casa?",
                ["Nunca", "Rara vez", "Ocasionalmente", "Frecuentemente", "Siempre/Casi siempre"],
                help="Comidas preparadas en tu cocina vs comer fuera/delivery"
            )
        
        with col2:
            electrodomesticos = st.multiselect(
                "¿Qué electrodomésticos tienes disponibles?",
                ["Estufa/Cocina", "Horno", "Microondas", "Licuadora", "Procesador de alimentos", 
                 "Freidora de aire", "Plancha/Grill", "Olla de presión", "Slow cooker", "Otro"],
                help="Selecciona todos los que uses para cocinar"
            )
            
            compra_ingredientes = st.selectbox(
                "¿Cómo obtienes principalmente tus ingredientes?",
                ["Supermercado tradicional", "Mercado local/tianguis", "Tiendas especializadas", 
                 "Compras online", "Combinación de varios", "Alguien más compra para mí"],
                help="¿Dónde y cómo haces las compras de comida?"
            )

        st.markdown("### 🥘 Métodos de preparación preferidos")
        metodos_preparacion = st.multiselect(
            "¿Qué métodos de cocción prefieres o usas más?",
            ["Hervido", "Al vapor", "Salteado", "Frito", "Al horno", "A la plancha", 
             "A la parrilla", "Crudo", "Microondas", "Guisado", "Al wok"],
            help="Selecciona todos los métodos que uses regularmente"
        )
        
        comida_preparada_frecuencia = st.selectbox(
            "¿Con qué frecuencia consumes comida preparada/procesada?",
            ["Nunca", "Rara vez", "Ocasionalmente", "Frecuentemente", "Siempre/Casi siempre"],
            help="Incluye comidas congeladas, enlatadas, delivery, restaurantes"
        )

        # Guardar en session state
        st.session_state.nivel_cocina = nivel_cocina
        st.session_state.tiempo_cocinar_dia = tiempo_cocinar_dia
        st.session_state.frecuencia_cocina_casa = frecuencia_cocina_casa
        st.session_state.electrodomesticos = electrodomesticos
        st.session_state.compra_ingredientes = compra_ingredientes
        st.session_state.metodos_preparacion = metodos_preparacion
        st.session_state.comida_preparada_frecuencia = comida_preparada_frecuencia
        
        st.markdown('</div>', unsafe_allow_html=True)

    # BLOQUE 5: Contexto cultural y social
    with st.expander("🏛️ **Paso 5: Contexto Cultural y Social**", expanded=True):
        progress.progress(80)
        progress_text.text("Paso 5 de 6: Evaluación de contexto cultural")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🌍 Tradiciones culturales y familiares")
        
        col1, col2 = st.columns(2)  
        with col1:
            origen_cultural = st.text_input(
                "¿Cuál es tu origen cultural/región?",
                placeholder="Ej: Mexicano del norte, Italiano, Asiático...",
                help="Esto nos ayuda a entender tus tradiciones alimentarias"
            )
            
            comida_tradicional = st.text_area(
                "¿Hay comidas tradicionales importantes en tu familia/cultura?",
                placeholder="Ej: Tamales en navidad, pasta los domingos, té de la tarde...",
                help="Menciona platillos o rituales alimentarios importantes"
            )
        
        with col2:
            come_en_familia = st.selectbox(
                "¿Con qué frecuencia comes en familia/acompañado?",
                ["Nunca", "Rara vez", "Ocasionalmente", "Frecuentemente", "Siempre"],
                help="Considera comidas con familia, pareja, amigos"
            )
            
            eventos_sociales_comida = st.selectbox(
                "¿Participas frecuentemente en eventos sociales que involucran comida?",
                ["Nunca", "Rara vez", "Ocasionalmente", "Frecuentemente", "Siempre"],
                help="Fiestas, reuniones, celebraciones, comidas de trabajo"
            )

        st.markdown("### 🎯 Objetivos y motivaciones")
        objetivo_principal = st.selectbox(
            "¿Cuál es tu objetivo principal con respecto a la alimentación?",
            ["Mantener peso y salud actuales", "Perder peso", "Ganar peso/músculo", 
             "Mejorar energía y bienestar", "Controlar condición médica", "Rendimiento deportivo",
             "Mejorar digestión", "Reducir inflamación", "Longevidad y antienvejecimiento"],
            help="Selecciona tu prioridad número uno"
        )
        
        motivaciones_adicionales = st.multiselect(
            "¿Qué otras motivaciones tienes? (selecciona todas las que apliquen)",
            ["Ahorrar dinero", "Ahorrar tiempo", "Ser más sostenible/ecológico", 
             "Aprender a cocinar mejor", "Variar mi dieta", "Comer más saludable",
             "Disfrutar más la comida", "Controlar antojos", "Mejorar imagen corporal"],
            help="Múltiples motivaciones nos ayudan a crear un plan más completo"
        )

        # Guardar en session state
        st.session_state.origen_cultural = origen_cultural
        st.session_state.comida_tradicional = comida_tradicional
        st.session_state.come_en_familia = come_en_familia
        st.session_state.eventos_sociales_comida = eventos_sociales_comida
        st.session_state.objetivo_principal = objetivo_principal
        st.session_state.motivaciones_adicionales = motivaciones_adicionales
        
        st.markdown('</div>', unsafe_allow_html=True)

    # BLOQUE 6: Información adicional y suplementos
    with st.expander("💊 **Paso 6: Suplementos e Información Adicional**", expanded=True):
        progress.progress(100)
        progress_text.text("Paso 6 de 6: Información complementaria")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 💊 Suplementos y bebidas")
        
        col1, col2 = st.columns(2)
        with col1:
            toma_suplementos = st.radio(
                "¿Tomas suplementos nutricionales?",
                ["No", "Sí, ocasionalmente", "Sí, regularmente"],
                help="Incluye vitaminas, minerales, proteínas, etc."
            )
            
            suplementos_especificos = ""
            if toma_suplementos != "No":
                suplementos_especificos = st.text_area(
                    "¿Qué suplementos tomas?",
                    placeholder="Ej: Vitamina D, Omega 3, Proteína en polvo, Multivitamínico...",
                    help="Lista todos los suplementos que consumes"
                )
        
        with col2:
            consumo_agua_diario = st.selectbox(
                "¿Cuánta agua consumes aproximadamente por día?",
                ["Menos de 1 litro", "1-1.5 litros", "1.5-2 litros", "2-2.5 litros", "Más de 2.5 litros"],
                help="Incluye agua pura, no otras bebidas"
            )
            
            bebidas_frecuentes = st.multiselect(
                "¿Qué bebidas consumes regularmente?",
                ["Agua", "Café", "Té", "Refrescos/Sodas", "Jugos naturales", "Jugos procesados",
                 "Bebidas energéticas", "Alcohol", "Bebidas deportivas", "Leches vegetales", "Lácteos"],
                help="Selecciona todas las bebidas que tomes habitualmente"
            )

        st.markdown("### 📝 Información adicional")
        
        actividad_fisica = st.selectbox(
            "¿Cuál es tu nivel de actividad física?",
            ["Sedentario (sin ejercicio)", "Ligeramente activo (ejercicio ligero 1-3 días/semana)",
             "Moderadamente activo (ejercicio moderado 3-5 días/semana)", 
             "Muy activo (ejercicio intenso 6-7 días/semana)",
             "Extremadamente activo (ejercicio muy intenso, trabajo físico)"],
            help="Esto afecta tus necesidades nutricionales"
        )
        
        problemas_digestivos = st.text_area(
            "¿Tienes algún problema digestivo recurrente?",
            placeholder="Ej: Acidez, gases, estreñimiento, diarrea, hinchazón...",
            help="Opcional - ayuda a personalizar recomendaciones"
        )
        
        comentarios_adicionales = st.text_area(
            "¿Hay algo más que consideres importante mencionar sobre tus hábitos alimentarios?",
            placeholder="Cualquier información adicional que creas relevante...",
            help="Opcional - espacio libre para comentarios"
        )

        # Guardar en session state
        st.session_state.toma_suplementos = toma_suplementos
        st.session_state.suplementos_especificos = suplementos_especificos
        st.session_state.consumo_agua_diario = consumo_agua_diario
        st.session_state.bebidas_frecuentes = bebidas_frecuentes
        st.session_state.actividad_fisica = actividad_fisica
        st.session_state.problemas_digestivos = problemas_digestivos
        st.session_state.comentarios_adicionales = comentarios_adicionales
        
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
EVALUACIÓN PATRONES ALIMENTARIOS MUPAI
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
PREFERENCIAS ALIMENTARIAS:
=====================================
- Sabores preferidos: {', '.join(st.session_state.get('sabores_preferidos', [])) if st.session_state.get('sabores_preferidos') else 'No especificado'}
- Texturas preferidas: {', '.join(st.session_state.get('texturas_preferidas', [])) if st.session_state.get('texturas_preferidas') else 'No especificado'}
- Temperaturas preferidas: {', '.join(st.session_state.get('temperaturas_preferidas', [])) if st.session_state.get('temperaturas_preferidas') else 'No especificado'}
- Comidas favoritas: {st.session_state.get('comidas_favoritas', 'No especificado')}
- Alimentos evitados: {st.session_state.get('alimentos_evitados', 'No especificado')}

=====================================
RESTRICCIONES Y PATRONES DIETÉTICOS:
=====================================
- Alergias/Intolerancias: {st.session_state.get('tiene_alergias', 'No especificado')}
- Detalles de alergias: {st.session_state.get('alergias_especificas', 'No especificado')}
- Patrón dietético: {st.session_state.get('patron_dietetico', 'No especificado')}
- Motivación del patrón: {st.session_state.get('motivacion_patron', 'No especificado')}

=====================================
PATRONES TEMPORALES:
=====================================
- Comidas por día: {st.session_state.get('comidas_por_dia', 'No especificado')}
- Horario desayuno: {st.session_state.get('horario_desayuno', 'No especificado')}
- Horario almuerzo: {st.session_state.get('horario_almuerzo', 'No especificado')}
- Horario cena: {st.session_state.get('horario_cena', 'No especificado')}
- Frecuencia de snacks: {st.session_state.get('snacks_frecuencia', 'No especificado')}
- Horarios irregulares: {'Sí' if st.session_state.get('horarios_irregulares') else 'No'}

=====================================
HABILIDADES CULINARIAS:
=====================================
- Nivel de cocina: {st.session_state.get('nivel_cocina', 'No especificado')}
- Tiempo disponible para cocinar: {st.session_state.get('tiempo_cocinar_dia', 'No especificado')}
- Frecuencia cocina en casa: {st.session_state.get('frecuencia_cocina_casa', 'No especificado')}
- Electrodomésticos disponibles: {', '.join(st.session_state.get('electrodomesticos', [])) if st.session_state.get('electrodomesticos') else 'No especificado'}
- Métodos de preparación preferidos: {', '.join(st.session_state.get('metodos_preparacion', [])) if st.session_state.get('metodos_preparacion') else 'No especificado'}

=====================================
CONTEXTO CULTURAL Y SOCIAL:
=====================================
- Origen cultural: {st.session_state.get('origen_cultural', 'No especificado')}
- Comida tradicional familiar: {st.session_state.get('comida_tradicional', 'No especificado')}
- Frecuencia come en familia: {st.session_state.get('come_en_familia', 'No especificado')}
- Eventos sociales con comida: {st.session_state.get('eventos_sociales_comida', 'No especificado')}

=====================================
OBJETIVOS Y MOTIVACIONES:
=====================================
- Objetivo principal: {st.session_state.get('objetivo_principal', 'No especificado')}
- Motivaciones adicionales: {', '.join(st.session_state.get('motivaciones_adicionales', [])) if st.session_state.get('motivaciones_adicionales') else 'No especificado'}

=====================================
INFORMACIÓN ADICIONAL:
=====================================
- Suplementos: {st.session_state.get('toma_suplementos', 'No especificado')}
- Suplementos específicos: {st.session_state.get('suplementos_especificos', 'No especificado')}
- Consumo de agua diario: {st.session_state.get('consumo_agua_diario', 'No especificado')}
- Bebidas frecuentes: {', '.join(st.session_state.get('bebidas_frecuentes', [])) if st.session_state.get('bebidas_frecuentes') else 'No especificado'}
- Actividad física: {st.session_state.get('actividad_fisica', 'No especificado')}
- Problemas digestivos: {st.session_state.get('problemas_digestivos', 'No especificado')}
- Comentarios adicionales: {st.session_state.get('comentarios_adicionales', 'No especificado')}

=====================================
RESUMEN DE PATRONES IDENTIFICADOS:
=====================================
Este análisis proporciona una base sólida para el desarrollo de recomendaciones 
nutricionales personalizadas basadas en preferencias individuales, restricciones, 
habilidades culinarias y contexto sociocultural del cliente.

Recomendamos seguimiento personalizado con nutricionista especializado para 
desarrollar plan nutricional específico basado en estos patrones identificados.

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
