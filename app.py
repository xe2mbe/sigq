import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

from database import FMREDatabase
from utils import (
    validate_all_fields, format_call_sign, format_name, format_qth,
    get_mexican_states, format_timestamp, get_signal_quality_text,
    get_zonas, get_sistemas, validate_call_sign, validate_operator_name, 
    validate_ciudad, validate_estado, validate_signal_report, get_estados_list
)
from exports import FMREExporter
from auth import AuthManager
from email_service import EmailService
import secrets
import string

# Definir funciones antes de usarlas
def show_motivational_dashboard():
    """Muestra el dashboard de rankings y reconocimientos"""
    st.header("🏆 Ranking")
    st.markdown("### ¡Competencia Sana entre Radioaficionados!")
    
    # Obtener estadísticas motivacionales
    motivational_stats = db.get_motivational_stats()
    
    # Pestañas para organizar las estadísticas
    tab1, tab2, tab3, tab4 = st.tabs(["🥇 Estaciones Top", "🌍 Zonas Activas", "📡 Sistemas Populares", "📊 Resumen General"])
    
    with tab1:
        st.subheader("🎯 Estaciones Más Reportadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Este Año**")
            if not motivational_stats['top_stations_year'].empty:
                for idx, row in motivational_stats['top_stations_year'].head(5).iterrows():
                    if idx == 0:
                        st.markdown(f"🥇 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 1:
                        st.markdown(f"🥈 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 2:
                        st.markdown(f"🥉 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    else:
                        st.markdown(f"🏅 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
            else:
                st.info("No hay datos suficientes para mostrar el ranking anual")
        
        with col2:
            st.markdown("#### 📆 **Este Mes**")
            if not motivational_stats['top_stations_month'].empty:
                for idx, row in motivational_stats['top_stations_month'].head(5).iterrows():
                    if idx == 0:
                        st.markdown(f"🥇 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 1:
                        st.markdown(f"🥈 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 2:
                        st.markdown(f"🥉 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    else:
                        st.markdown(f"🏅 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
            else:
                st.info("No hay datos suficientes para mostrar el ranking mensual")
    
    with tab2:
        st.subheader("🌍 Zonas Más Activas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Este Año**")
            if not motivational_stats['top_zones_year'].empty:
                for idx, row in motivational_stats['top_zones_year'].iterrows():
                    st.markdown(f"🏆 **Zona {row['zona']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de zonas para este año")
        
        with col2:
            st.markdown("#### 📆 **Este Mes**")
            if not motivational_stats['top_zones_month'].empty:
                for idx, row in motivational_stats['top_zones_month'].iterrows():
                    st.markdown(f"🏆 **Zona {row['zona']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de zonas para este mes")
    
    with tab3:
        st.subheader("📡 Sistemas Más Utilizados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Este Año**")
            if not motivational_stats['top_systems_year'].empty:
                for idx, row in motivational_stats['top_systems_year'].iterrows():
                    st.markdown(f"🔧 **{row['sistema']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de sistemas para este año")
        
        with col2:
            st.markdown("#### 📆 **Este Mes**")
            if not motivational_stats['top_systems_month'].empty:
                for idx, row in motivational_stats['top_systems_month'].iterrows():
                    st.markdown(f"🔧 **{row['sistema']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de sistemas para este mes")
    
    with tab4:
        st.subheader("📊 Resumen General de Actividad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Estadísticas del Año**")
            if not motivational_stats['general_year'].empty:
                year_stats = motivational_stats['general_year'].iloc[0]
                st.metric("📊 Total Reportes", year_stats['total_reports'])
                st.metric("👥 Estaciones Únicas", year_stats['unique_stations'])
                st.metric("📅 Días Activos", year_stats['active_days'])
            else:
                st.info("No hay estadísticas generales del año")
        
        with col2:
            st.markdown("#### 📆 **Estadísticas del Mes**")
            if not motivational_stats['general_month'].empty:
                month_stats = motivational_stats['general_month'].iloc[0]
                st.metric("📊 Total Reportes", month_stats['total_reports'])
                st.metric("👥 Estaciones Únicas", month_stats['unique_stations'])
                st.metric("📅 Días Activos", month_stats['active_days'])
            else:
                st.info("No hay estadísticas generales del mes")
    
    # Mensaje motivacional
    st.markdown("---")
    st.markdown("### 🎉 ¡Sigue Participando!")
    st.info("💪 **¡Cada reporte cuenta!** Mantente activo en las redes y ayuda a tu zona y sistema favorito a liderar las estadísticas. ¡La competencia sana nos hace crecer como comunidad radioaficionada! 📻✨")

def show_user_management():
    # Verificar si el usuario es admin
    if current_user['role'] != 'admin':
        st.error("❌ Acceso denegado. Solo los administradores pueden acceder a esta sección.")
        st.stop()
        
    st.header("👥 Gestión de Usuarios")
    
    # Inicializar servicio de email
    if 'email_service' not in st.session_state:
        st.session_state.email_service = EmailService()
    
    email_service = st.session_state.email_service
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Usuarios", "➕ Crear Usuario", "🔄 Recuperar Contraseña", "⚙️ Configuración Email"])
    
    with tab1:
        st.subheader("Lista de Usuarios")
        
        # Obtener usuarios
        users = db.get_all_users()
        
        if users is not None and len(users) > 0:
            for user in users:
                with st.expander(f"👤 {user['username']} ({user['role']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Nombre completo:** {user.get('full_name', 'No especificado')}")
                        st.write(f"**Email:** {user.get('email', 'No especificado')}")
                        st.write(f"**Rol:** {user['role']}")
                        st.write(f"**Creado:** {user.get('created_at', 'No disponible')}")
                    
                    with col2:
                        # Botón para editar usuario
                        if st.button(f"✏️ Editar", key=f"edit_{user['id']}"):
                            st.session_state[f"editing_user_{user['id']}"] = True
                        
                        # Botón para eliminar usuario (solo si no es admin)
                        if user['username'] != 'admin':
                            if st.button(f"🗑️ Eliminar", key=f"delete_{user['id']}"):
                                try:
                                    db.delete_user(user['id'])
                                    st.success(f"Usuario {user['username']} eliminado")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al eliminar usuario: {str(e)}")
                        else:
                            st.info("👑 Usuario administrador protegido")
                    
                    # Formulario de edición si está activado
                    if st.session_state.get(f"editing_user_{user['id']}", False):
                        st.markdown("---")
                        st.subheader("✏️ Editar Usuario")
                        
                        with st.form(f"edit_user_form_{user['id']}"):
                            edit_full_name = st.text_input("Nombre completo:", value=user.get('full_name', ''))
                            edit_email = st.text_input("Email:", value=user.get('email', ''))
                            edit_role = st.selectbox("Rol:", ["operator", "admin"], 
                                                   index=0 if user['role'] == 'operator' else 1)
                            
                            # Opción para cambiar contraseña
                            change_password = st.checkbox("Cambiar contraseña")
                            edit_password = ""
                            confirm_edit_password = ""
                            
                            if change_password:
                                edit_password = st.text_input("Nueva contraseña:", type="password", 
                                                            help="Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 carácter especial")
                                confirm_edit_password = st.text_input("Confirmar nueva contraseña:", type="password")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                submit_edit = st.form_submit_button("💾 Guardar Cambios")
                            
                            with col_cancel:
                                cancel_edit = st.form_submit_button("❌ Cancelar")
                            
                            if cancel_edit:
                                st.session_state[f"editing_user_{user['id']}"] = False
                                st.rerun()
                            
                            if submit_edit:
                                if edit_full_name and edit_email:
                                    # Validar contraseña si se va a cambiar
                                    password_valid = True
                                    if change_password:
                                        if edit_password != confirm_edit_password:
                                            st.error("❌ Las contraseñas no coinciden")
                                            password_valid = False
                                        else:
                                            from utils import validate_password
                                            is_valid, message = validate_password(edit_password)
                                            if not is_valid:
                                                st.error(f"❌ {message}")
                                                password_valid = False
                                    
                                    if password_valid:
                                        try:
                                            # Actualizar usuario
                                            update_data = {
                                                'full_name': edit_full_name,
                                                'email': edit_email,
                                                'role': edit_role
                                            }
                                            
                                            if change_password:
                                                import hashlib
                                                update_data['password'] = hashlib.sha256(edit_password.encode()).hexdigest()
                                            
                                            db.update_user(user['id'], **update_data)
                                            
                                            st.success("✅ Usuario actualizado exitosamente")
                                            st.info(f"**Usuario:** {user['username']}\n**Nombre:** {edit_full_name}\n**Email:** {edit_email}\n**Rol:** {edit_role}")
                                            
                                            st.session_state[f"editing_user_{user['id']}"] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error al actualizar usuario: {str(e)}")
                                else:
                                    st.error("❌ Todos los campos son obligatorios")
        else:
            st.info("No hay usuarios registrados")
    
    with tab2:
        st.subheader("➕ Crear Nuevo Usuario")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Nombre de usuario:")
            new_full_name = st.text_input("Nombre completo:")
            new_email = st.text_input("Email:")
            new_password = st.text_input("Contraseña:", type="password", help="Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 carácter especial")
            confirm_password = st.text_input("Confirmar contraseña:", type="password")
            new_role = st.selectbox("Rol:", ["operator", "admin"])
            
            submit_create = st.form_submit_button("✅ Crear Usuario")
            
            if submit_create:
                if new_username and new_full_name and new_email and new_password and confirm_password:
                    # Validar que las contraseñas coincidan
                    if new_password != confirm_password:
                        st.error("❌ Las contraseñas no coinciden")
                    else:
                        from utils import validate_password
                        is_valid, message = validate_password(new_password)
                        if not is_valid:
                            st.error(f"❌ {message}")
                        else:
                            try:
                                # Crear usuario
                                user_created = auth.create_user(new_username, new_password, new_role, new_full_name, new_email)
                                if user_created:
                                    st.success("✅ Usuario creado exitosamente")
                                    
                                    # Mostrar información del usuario creado
                                    st.info(f"""
                                    **Usuario creado:**
                                    - **Nombre de usuario:** {new_username}
                                    - **Nombre completo:** {new_full_name}
                                    - **Email:** {new_email}
                                    - **Rol:** {new_role}
                                    """)
                                    
                                    # Enviar email de bienvenida si está configurado
                                    try:
                                        user_data = {
                                            'username': new_username,
                                            'full_name': new_full_name,
                                            'email': new_email,
                                            'role': new_role
                                        }
                                        
                                        if email_service.send_welcome_email(user_data, new_password):
                                            st.success("📧 Email de bienvenida enviado")
                                        else:
                                            st.warning("⚠️ Usuario creado pero no se pudo enviar el email de bienvenida")
                                    except Exception as e:
                                        st.warning(f"⚠️ Usuario creado pero error al enviar email: {str(e)}")
                                    
                                    # Esperar antes de recargar para mostrar mensajes
                                    import time
                                    time.sleep(3)
                                    st.rerun()
                                else:
                                    st.error("❌ Error al crear usuario. El nombre de usuario podría ya existir.")
                            except Exception as e:
                                st.error(f"❌ Error al crear usuario: {str(e)}")
                else:
                    st.error("❌ Todos los campos son obligatorios")
    
    with tab3:
        st.subheader("🔄 Recuperar Contraseña")
        
        with st.form("password_recovery_form"):
            recovery_username = st.text_input("Nombre de usuario:")
            submit_recovery = st.form_submit_button("🔄 Generar Token de Recuperación")
            
            if submit_recovery and recovery_username:
                try:
                    token = auth.generate_password_reset_token(recovery_username)
                    if token:
                        st.success(f"✅ Token de recuperación generado: **{token}**")
                        st.info("Este token expira en 1 hora y es de un solo uso.")
                        
                        # Intentar enviar por email
                        user = db.get_user_by_username(recovery_username)
                        if user and user.get('email'):
                            try:
                                if email_service.send_password_recovery_email(user, token):
                                    st.success("📧 Token enviado por email")
                                else:
                                    st.warning("⚠️ No se pudo enviar el email. Usa el token mostrado arriba.")
                            except Exception as e:
                                st.warning(f"⚠️ Error al enviar email: {str(e)}")
                    else:
                        st.error("❌ Usuario no encontrado")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        st.markdown("---")
        st.subheader("🔑 Usar Token de Recuperación")
        
        with st.form("use_recovery_token_form"):
            token_input = st.text_input("Token de recuperación:")
            new_password_recovery = st.text_input("Nueva contraseña:", type="password")
            confirm_password_recovery = st.text_input("Confirmar nueva contraseña:", type="password")
            submit_token = st.form_submit_button("🔑 Cambiar Contraseña")
            
            if submit_token and token_input and new_password_recovery and confirm_password_recovery:
                if new_password_recovery != confirm_password_recovery:
                    st.error("❌ Las contraseñas no coinciden")
                else:
                    from utils import validate_password
                    is_valid, message = validate_password(new_password_recovery)
                    if not is_valid:
                        st.error(f"❌ {message}")
                    else:
                        try:
                            if auth.reset_password_with_token(token_input, new_password_recovery):
                                st.success("✅ Contraseña cambiada exitosamente")
                            else:
                                st.error("❌ Token inválido o expirado")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    with tab4:
        st.subheader("⚙️ Configuración de Email SMTP")
        
        with st.form("smtp_config_form"):
            smtp_server = st.text_input("Servidor SMTP:", value=email_service.smtp_server or "")
            smtp_port = st.number_input("Puerto SMTP:", value=email_service.smtp_port or 587, min_value=1, max_value=65535)
            smtp_username = st.text_input("Usuario SMTP:", value=email_service.smtp_username or "")
            smtp_password = st.text_input("Contraseña SMTP:", type="password")
            sender_email = st.text_input("Email remitente:", value=getattr(email_service, 'from_email', '') or "")
            sender_name = st.text_input("Nombre remitente:", value=getattr(email_service, 'from_name', '') or "Sistema FMRE")
            
            submit_smtp = st.form_submit_button("💾 Guardar Configuración SMTP")
            
            if submit_smtp:
                try:
                    email_service.configure_smtp(
                        smtp_server, smtp_port, smtp_username, 
                        smtp_password if smtp_password else email_service.smtp_password,
                        sender_email, sender_name
                    )
                    st.success("✅ Configuración SMTP guardada")
                except Exception as e:
                    st.error(f"❌ Error al guardar configuración: {str(e)}")
        
        # Test de conexión
        if st.button("🧪 Probar Conexión SMTP"):
            if email_service.test_smtp_connection():
                st.success("✅ Conexión SMTP exitosa")
            else:
                st.error("❌ Error en la conexión SMTP")

# Configuración de la página
st.set_page_config(
    page_title="Sistema FMRE - Control de Reportes",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
    }
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    @media (max-width: 768px) {
        .logo-container {
            flex-direction: column;
            gap: 10px;
        }
        .logo-container img {
            width: 80px !important;
        }
        .logo-container h1 {
            font-size: 1.8rem !important;
            text-align: center;
        }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        padding: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-logo {
        display: block;
        margin: 0 auto 20px auto;
        max-width: 150px;
        height: auto;
    }
    .error-message {
        padding: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar base de datos y autenticación
@st.cache_resource
def init_database():
    return FMREDatabase()

@st.cache_resource
def init_exporter():
    return FMREExporter()

def init_auth():
    if 'auth_manager' not in st.session_state:
        db = init_database()
        auth = AuthManager(db)
        auth.create_default_admin()  # Crear admin por defecto
        st.session_state.auth_manager = auth
    return st.session_state.auth_manager

db = init_database()
exporter = init_exporter()
auth = init_auth()

# Verificar autenticación
if not auth.is_logged_in():
    auth.show_login_form()
    st.stop()

# Usuario actual
current_user = auth.get_current_user()

# Título principal
st.markdown('<h1 style="color: #1f77b4; margin: 20px 0; font-size: 2.2rem; text-align: center;">Sistema Integral de Gestión de QSOs (SIGQ)</h1>', unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("Navegación")

# Información del usuario
st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **Usuario:** {current_user['full_name']}")
st.sidebar.markdown(f"🎭 **Rol:** {current_user['role'].title()}")

# Sistema corregido - debug removido

if st.sidebar.button("🚪 Cerrar Sesión"):
    auth.logout()

st.sidebar.markdown("---")

# Crear menú dinámico basado en el rol del usuario
menu_options = ["🏠 Registro de Reportes", "📊 Dashboard", "📁 Exportar Datos", "🔍 Buscar/Editar", "🏆 Ranking", "👤 Mi Perfil"]

# Solo mostrar Gestión de Usuarios si es admin
if current_user['role'] == 'admin':
    menu_options.append("👥 Gestión de Usuarios")

page = st.sidebar.selectbox(
    "Navegación:",
    menu_options
)

# Selector de fecha de sesión
st.sidebar.markdown("---")
st.sidebar.subheader("Sesión Actual")
session_date = st.sidebar.date_input(
    "Fecha de sesión:",
    value=date.today(),
    help="Selecciona la fecha de la sesión de boletín"
)


def show_profile_management():
    """Muestra la página de gestión de perfil del usuario"""
    st.header("👤 Mi Perfil")
    st.markdown("### Gestiona tu información personal")
    
    # Obtener información actual del usuario
    user_info = db.get_user_by_username(current_user['username'])
    
    if not user_info:
        st.error("❌ Error al cargar información del usuario")
        return
    
    # Convertir tupla a diccionario usando índices conocidos
    # Estructura real: (id, username, password_hash, full_name, email, role, preferred_system, hf_frequency_pref, hf_mode_pref, hf_power_pref, created_at, last_login)
    user_dict = {
        'id': user_info[0],
        'username': user_info[1],
        'password_hash': user_info[2],
        'full_name': user_info[3] if len(user_info) > 3 else '',
        'email': user_info[4] if len(user_info) > 4 else '',
        'role': user_info[5] if len(user_info) > 5 else '',
        'preferred_system': user_info[6] if len(user_info) > 6 else 'ASL',
        'created_at': user_info[10] if len(user_info) > 10 else '',
        'last_login': user_info[11] if len(user_info) > 11 else ''
    }
    
    # Crear tabs para organizar la información
    tab1, tab2 = st.tabs(["📝 Información Personal", "🔐 Cambiar Contraseña"])
    
    with tab1:
        st.subheader("Actualizar Información Personal")
        
        with st.form("update_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_full_name = st.text_input(
                    "Nombre Completo:",
                    value=user_dict['full_name'],
                    help="Tu nombre completo como aparecerá en los reportes"
                )
                
                new_email = st.text_input(
                    "Correo Electrónico:",
                    value=user_dict['email'],
                    help="Tu dirección de correo electrónico"
                )
            
            with col2:
                st.text_input(
                    "Nombre de Usuario:",
                    value=user_dict['username'],
                    disabled=True,
                    help="El nombre de usuario no se puede cambiar"
                )
                
                st.text_input(
                    "Rol:",
                    value=user_dict['role'].title(),
                    disabled=True,
                    help="Tu rol en el sistema"
                )
            
            # Información adicional
            st.markdown("---")
            col3, col4 = st.columns(2)
            
            with col3:
                if user_dict['created_at']:
                    formatted_created = format_timestamp(user_dict['created_at'])
                    st.info(f"📅 **Miembro desde:** {formatted_created}")
            
            with col4:
                if user_dict['last_login']:
                    formatted_login = format_timestamp(user_dict['last_login'])
                    st.info(f"🕒 **Último acceso:** {formatted_login}")
            
            submitted = st.form_submit_button("💾 Actualizar Información", type="primary")
            
            if submitted:
                # Validar datos
                if not new_full_name.strip():
                    st.error("❌ El nombre completo es obligatorio")
                elif not new_email.strip():
                    st.error("❌ El correo electrónico es obligatorio")
                elif '@' not in new_email:
                    st.error("❌ Ingresa un correo electrónico válido")
                else:
                    # Actualizar información
                    success = db.update_user_profile(
                        user_dict['id'],
                        new_full_name.strip(),
                        new_email.strip()
                    )
                    
                    if success:
                        st.success("✅ Información actualizada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar la información")
    
    with tab2:
        st.subheader("Cambiar Contraseña")
        
        with st.form("change_password_form"):
            current_password = st.text_input(
                "Contraseña Actual:",
                type="password",
                help="Ingresa tu contraseña actual para confirmar el cambio"
            )
            
            new_password = st.text_input(
                "Nueva Contraseña:",
                type="password",
                help="Mínimo 6 caracteres"
            )
            
            confirm_password = st.text_input(
                "Confirmar Nueva Contraseña:",
                type="password",
                help="Repite la nueva contraseña"
            )
            
            submitted_password = st.form_submit_button("🔐 Cambiar Contraseña", type="primary")
            
            if submitted_password:
                # Validar contraseña actual
                if not auth.verify_password(current_password, user_dict['password_hash']):
                    st.error("❌ La contraseña actual es incorrecta")
                elif len(new_password) < 6:
                    st.error("❌ La nueva contraseña debe tener al menos 6 caracteres")
                elif new_password != confirm_password:
                    st.error("❌ Las contraseñas no coinciden")
                elif current_password == new_password:
                    st.error("❌ La nueva contraseña debe ser diferente a la actual")
                else:
                    # Cambiar contraseña
                    success = db.change_user_password(
                        user_dict['id'],
                        new_password
                    )
                    
                    if success:
                        st.success("✅ Contraseña cambiada correctamente")
                        st.info("🔄 Por seguridad, deberás iniciar sesión nuevamente")
                        if st.button("🚪 Cerrar Sesión"):
                            auth.logout()
                    else:
                        st.error("❌ Error al cambiar la contraseña")

def registro_reportes():
    st.title("📋 Registro de Reportes")
    
    # Obtener sistema preferido del usuario y configuración HF
    user_preferred_system = "ASL"  # Default
    user_hf_frequency = ""
    user_hf_mode = ""
    user_hf_power = ""
    
    if current_user:
        user_preferred_system = db.get_user_preferred_system(current_user['username']) or "ASL"
        # Obtener configuración HF preferida del usuario
        user_data = db.get_user_by_username(current_user['username'])
        if user_data and len(user_data) > 6:  # Verificar que existan los campos HF
            user_hf_frequency = user_data[7] or ""  # hf_frequency_pref
            user_hf_mode = user_data[8] or ""       # hf_mode_pref  
            user_hf_power = user_data[9] or ""      # hf_power_pref
        
    # Configuración de Sistema Preferido
    st.subheader("⚙️ Configuración de Sistema Preferido")
    
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4; margin-bottom: 20px;">
        <h4 style="color: #1f77b4; margin-top: 0;">📡 ¿Qué es el Sistema Preferido?</h4>
        <p style="margin-bottom: 10px;">
            <strong>Configura tu sistema de radio favorito</strong> para que aparezca <strong>pre-seleccionado automáticamente</strong> 
            en todos tus reportes, ahorrándote tiempo en cada registro.
        </p>
        <p style="margin-bottom: 0;">
            <strong>🎯 Ventaja especial HF:</strong> Si seleccionas HF, también puedes configurar tu 
            <strong>frecuencia, modo y potencia por defecto</strong> para que aparezcan automáticamente.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"💡 **Tu sistema preferido actual:** {user_preferred_system}")
    
    if user_preferred_system == "HF" and (user_hf_frequency or user_hf_mode or user_hf_power):
        st.write("**Configuración HF preferida:**")
        if user_hf_frequency:
            st.write(f"📻 Frecuencia: {user_hf_frequency} MHz")
        if user_hf_mode:
            st.write(f"📡 Modo: {user_hf_mode}")
        if user_hf_power:
            st.write(f"⚡ Potencia: {user_hf_power} W")
    
    # Selector para cambiar sistema preferido
    new_preferred = st.selectbox(
        "Cambiar sistema preferido:",
        get_sistemas(),
        index=get_sistemas().index(user_preferred_system) if user_preferred_system in get_sistemas() else 0,
        key="change_preferred_system"
    )
    
    # Campos HF adicionales si se selecciona HF
    new_hf_frequency = ""
    new_hf_mode = ""
    new_hf_power = ""
    
    if new_preferred == "HF":
        st.markdown("**📻 Configuración HF Preferida:**")
        col_hf1, col_hf2, col_hf3 = st.columns(3)
        
        with col_hf1:
            new_hf_frequency = st.text_input(
                "Frecuencia (MHz)", 
                value=user_hf_frequency,
                placeholder="14.230", 
                help="1.8-30 MHz",
                key="pref_hf_freq"
            )
        
        with col_hf2:
            new_hf_mode = st.selectbox(
                "Modo", 
                ["", "USB", "LSB", "CW", "DIGITAL"],
                index=["", "USB", "LSB", "CW", "DIGITAL"].index(user_hf_mode) if user_hf_mode in ["", "USB", "LSB", "CW", "DIGITAL"] else 0,
                key="pref_hf_mode"
            )
        
        with col_hf3:
            new_hf_power = st.text_input(
                "Potencia (W)", 
                value=user_hf_power,
                placeholder="100",
                key="pref_hf_power"
            )
        
        # Botón después de los campos HF
        update_button = st.button("💾 Actualizar Preferido", help="Guardar configuración preferida")
    else:
        # Botón inmediatamente después del selector si no es HF
        update_button = st.button("💾 Actualizar Preferido", help="Guardar configuración preferida")
    
    if update_button:
        if current_user:
            # Actualizar sistema preferido
            result = db.update_user_preferred_system(current_user['username'], new_preferred)
            
            # Si es HF, actualizar también la configuración HF preferida
            if new_preferred == "HF":
                hf_result = db.update_user_hf_preferences(
                    current_user['username'], 
                    new_hf_frequency, 
                    new_hf_mode, 
                    new_hf_power
                )
            
            if result:
                st.success(f"✅ **Sistema preferido actualizado a: {new_preferred}**")
                if new_preferred == "HF":
                    st.success("✅ **Configuración HF preferida guardada**")
                st.info("ℹ️ Los cambios se aplicarán inmediatamente en el próximo reporte.")
                st.rerun()
            else:
                st.error("❌ Error al actualizar sistema preferido")
        else:
            st.error("❌ No hay usuario autenticado")
    
    st.markdown("---")
    
    # Selección rápida desde historial
    st.subheader("⚡ Registro Rápido desde Historial")
    
    station_history = db.get_station_history(50)  # Aumentar límite para más opciones
    
    if not station_history.empty:
        # Limpiar selecciones si está marcado
        if st.session_state.get('clear_selections', False):
            for key in ['station_zona', 'station_sistema', 'station_all']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.clear_selections = False
        
        # Crear tabs para categorizar las estaciones
        tab1, tab2, tab3 = st.tabs(["🌍 Por Zona", "📡 Por Sistema", "📻 Por Indicativo"])
        
        selected_station = None
        
        with tab1:
            st.write("**Estaciones agrupadas por Zona:**")
            # Agrupar por zona
            zonas_disponibles = station_history['zona'].unique()
            zona_seleccionada = st.selectbox(
                "Seleccionar zona:",
                options=["-- Todas las zonas --"] + list(zonas_disponibles),
                key="zona_filter"
            )
            
            if zona_seleccionada != "-- Todas las zonas --":
                stations_filtered = station_history[station_history['zona'] == zona_seleccionada]
                if not stations_filtered.empty:
                    station_options = ["-- Seleccionar estación --"]
                    for _, station in stations_filtered.iterrows():
                        display_text = f"{station['call_sign']} - {station['operator_name']} - {station.get('estado', 'N/A')} - {station.get('ciudad', station.get('qth', 'N/A'))} - {station['zona']} - {station['sistema']} ({station['use_count']} usos)"
                        station_options.append(display_text)
                else:
                    station_options = ["-- No hay estaciones en esta zona --"]
                
                selected_station = st.selectbox(
                    "Estaciones en esta zona:",
                    options=station_options,
                    key="station_zona"
                )
        
        with tab2:
            st.write("**Estaciones agrupadas por Sistema:**")
            # Agrupar por sistema
            sistemas_disponibles = station_history['sistema'].unique()
            sistema_seleccionado = st.selectbox(
                "Seleccionar sistema:",
                options=["-- Todos los sistemas --"] + list(sistemas_disponibles),
                key="sistema_filter"
            )
            
            if sistema_seleccionado != "-- Todos los sistemas --":
                stations_filtered = station_history[station_history['sistema'] == sistema_seleccionado]
                if not stations_filtered.empty:
                    station_options = ["-- Seleccionar estación --"]
                    for _, station in stations_filtered.iterrows():
                        display_text = f"{station['call_sign']} - {station['operator_name']} - {station.get('estado', 'N/A')} - {station.get('ciudad', station.get('qth', 'N/A'))} - {station['zona']} - {station['sistema']} ({station['use_count']} usos)"
                        station_options.append(display_text)
                else:
                    station_options = ["-- No hay estaciones con este sistema --"]
                
                selected_station = st.selectbox(
                    "Estaciones con este sistema:",
                    options=station_options,
                    key="station_sistema"
                )
        
        with tab3:
            st.write("**Todas las estaciones ordenadas por uso:**")
            # Mostrar todas las estaciones ordenadas por frecuencia de uso
            history_options_all = ["-- Seleccionar estación --"]
            for _, station in station_history.iterrows():
                display_text = f"{station['call_sign']} - {station['operator_name']} - {station.get('estado', 'N/A')} - {station.get('ciudad', station.get('qth', 'N/A'))} - {station['zona']} - {station['sistema']} ({station['use_count']} usos)"
                history_options_all.append(display_text)
            
            selected_station = st.selectbox(
                "Estaciones más utilizadas:",
                options=history_options_all,
                key="station_all"
            )
        
        # Botón para usar datos (fuera de los tabs)
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            # Determinar qué estación está seleccionada en cualquier tab
            current_selection = None
            if st.session_state.get('station_zona', '').startswith('-- ') == False and st.session_state.get('station_zona'):
                current_selection = st.session_state.get('station_zona')
            elif st.session_state.get('station_sistema', '').startswith('-- ') == False and st.session_state.get('station_sistema'):
                current_selection = st.session_state.get('station_sistema')
            elif st.session_state.get('station_all', '').startswith('-- ') == False and st.session_state.get('station_all'):
                current_selection = st.session_state.get('station_all')
            
            button_disabled = current_selection is None or current_selection.startswith('-- ')
            
            if st.button("📋 Usar Datos Seleccionados", disabled=button_disabled, use_container_width=True):
                if current_selection and not current_selection.startswith('-- '):
                    # Parse station data
                    parts = current_selection.split(' - ')
                    if len(parts) >= 6:  # Now we have estado and ciudad separate
                        call = parts[0]
                        name = parts[1]
                        estado = parts[2]
                        ciudad = parts[3]
                        zona = parts[4]
                        sistema_parts = parts[5].split(' (')[0]  # Remove usage count
                        
                        # Store in session state
                        st.session_state.prefill_call = call
                        st.session_state.prefill_name = name
                        st.session_state.prefill_estado = estado
                        st.session_state.prefill_ciudad = ciudad
                        st.session_state.prefill_zona = zona
                        st.session_state.prefill_sistema = sistema_parts
                        
                        # Marcar para limpiar selecciones en el próximo rerun
                        st.session_state.clear_selections = True
                        
                        st.success("✅ Datos cargados. Completa el formulario abajo.")
                        st.rerun()
    
    st.markdown("---")
    
    # Inicializar valores por defecto desde session_state si existen
    default_call = st.session_state.get('prefill_call', "")
    default_name = st.session_state.get('prefill_name', "")
    default_estado = st.session_state.get('prefill_estado', "")
    default_ciudad = st.session_state.get('prefill_ciudad', "")
    
    # Encontrar índices para los selectbox
    zonas = get_zonas()
    sistemas = get_sistemas()
    estados = get_estados_list()
    
    default_zona = 0
    default_sistema = 0
    default_estado_idx = 0
    
    if 'prefill_zona' in st.session_state:
        try:
            default_zona = zonas.index(st.session_state['prefill_zona'])
        except ValueError:
            default_zona = 0
    
    if 'prefill_sistema' in st.session_state:
        try:
            default_sistema = sistemas.index(st.session_state['prefill_sistema'])
        except ValueError:
            default_sistema = 0
    
    if 'prefill_estado' in st.session_state:
        try:
            default_estado_idx = estados.index(st.session_state['prefill_estado'])
        except ValueError:
            default_estado_idx = 0
    
    # Obtener sistema preferido del usuario
    user_preferred_system = "ASL"  # Default
    if current_user:
        user_preferred_system = db.get_user_preferred_system(current_user['username']) or "ASL"
    
    # Formulario de registro
    with st.form("report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            call_sign = st.text_input("📻 Indicativo", placeholder="(Obligatorio) | Ejemplo: XE1ABC",value=default_call, help="Ejemplo: XE1ABC")
            operator_name = st.text_input("👤 Nombre del Operador",placeholder="(Obligatorio) | Ejemplo: Juan Pérez", value=default_name)
            estado = st.selectbox("🏛️ Estado", estados, index=default_estado_idx, help="Selecciona el estado")
            ciudad = st.text_input("🏙️ Ciudad",placeholder="(Opcional) | Ejemplo: Durangotitlan de los Baches", value=default_ciudad, help="Ejemplo: Monterrey, Guadalajara")
        
        with col2:
            signal_report = st.text_input("📶 Reporte de Señal",value="59", help="Ejemplo: 5x9, Buena, Regular")
            zona = st.selectbox("🌍 Zona", zonas, index=default_zona)
            # Usar sistema preferido como default si no hay prefill
            if 'prefill_sistema' not in st.session_state:
                try:
                    default_sistema = sistemas.index(user_preferred_system)
                except ValueError:
                    default_sistema = 0
            sistema = st.selectbox("📡 Sistema", sistemas, index=default_sistema)
        
        # Campos HF dinámicos con valores preferidos como default
        hf_frequency = ""
        hf_mode = ""
        hf_power = ""
        
        if sistema == "HF":
            st.subheader("📻 Configuración HF")
            col_hf1, col_hf2, col_hf3 = st.columns(3)
            
            with col_hf1:
                hf_frequency = st.text_input(
                    "Frecuencia (MHz)", 
                    value=user_hf_frequency,
                    placeholder="14.230", 
                    help="1.8-30 MHz"
                )
            
            with col_hf2:
                hf_mode = st.selectbox(
                    "Modo", 
                    ["", "USB", "LSB", "CW", "DIGITAL"],
                    index=["", "USB", "LSB", "CW", "DIGITAL"].index(user_hf_mode) if user_hf_mode in ["", "USB", "LSB", "CW", "DIGITAL"] else 0
                )
            
            with col_hf3:
                hf_power = st.text_input(
                    "Potencia (W)", 
                    value=user_hf_power,
                    placeholder="100"
                )
        
        observations = st.text_area(
            "Observaciones",
            placeholder="Comentarios adicionales (opcional)",
            height=100
        )
        
        submitted = st.form_submit_button("📝 Agregar Reporte", use_container_width=True)
        
        if submitted:
            # Validar campos
            is_valid, errors = validate_all_fields(call_sign, operator_name, estado, ciudad, signal_report, zona, sistema)
            
            if is_valid:
                try:
                    # Agregar a la base de datos
                    report_id = db.add_report(
                        call_sign, operator_name, estado, ciudad, 
                        signal_report, zona, sistema, observations
                    )
                    
                    # Limpiar datos precargados después de agregar reporte
                    for key in ['prefill_call', 'prefill_name', 'prefill_estado', 'prefill_ciudad', 'prefill_zona', 'prefill_sistema']:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.success(f"✅ Reporte agregado exitosamente (ID: {report_id})")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al agregar reporte: {str(e)}")
            else:
                for error in errors:
                    st.error(f"❌ {error}")
    
    # Mostrar reportes recientes de la sesión actual
    st.subheader(f"Reportes de la Sesión - {session_date.strftime('%d/%m/%Y')}")
    
    recent_reports = db.get_all_reports(session_date)
    
    if not recent_reports.empty:
        # Mostrar métricas rápidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unique_participants = recent_reports['call_sign'].nunique()
            st.metric("Participantes Únicos", unique_participants)
        
        with col2:
            total_reports = len(recent_reports)
            st.metric("Total de Reportes", total_reports)
        
        with col3:
            avg_quality = recent_reports['signal_quality'].mean()
            quality_text = "Buena" if avg_quality > 2.5 else "Regular" if avg_quality > 1.5 else "Mala"
            st.metric("Calidad Promedio", quality_text)
        
        # Tabla de reportes con frecuencia y modo
        columns_to_show = ['call_sign', 'operator_name', 'qth', 'zona', 'sistema', 'signal_report', 'timestamp']
        
        # Agregar columnas HF si existen datos
        if 'hf_frequency' in recent_reports.columns and 'hf_mode' in recent_reports.columns:
            columns_to_show.insert(-1, 'hf_frequency')  # Antes de timestamp
            columns_to_show.insert(-1, 'hf_mode')       # Antes de timestamp
        
        display_df = recent_reports[columns_to_show].copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
        
        # Configurar nombres de columnas
        column_names = ['Indicativo', 'Operador', 'QTH', 'Zona', 'Sistema', 'Señal', 'Hora']
        if 'hf_frequency' in columns_to_show:
            column_names.insert(-1, 'Frecuencia')
        if 'hf_mode' in columns_to_show:
            column_names.insert(-1, 'Modo')
        
        display_df.columns = column_names
        
        # Limpiar valores vacíos en frecuencia y modo para mejor visualización
        if 'Frecuencia' in display_df.columns:
            display_df['Frecuencia'] = display_df['Frecuencia'].fillna('').replace('', '-')
        if 'Modo' in display_df.columns:
            display_df['Modo'] = display_df['Modo'].fillna('').replace('', '-')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📝 **Primero agrega algunos reportes para que aparezcan en el historial**")
        st.info("Una vez que tengas reportes, podrás usar la función de registro rápido desde el historial.")

# Página: Registro de Reportes
if page == "🏠 Registro de Reportes":
    registro_reportes()

# Página: Dashboard
elif page == "📊 Dashboard":
    st.header("Dashboard de Estadísticas")

    # Obtener estadísticas
    stats = db.get_statistics(session_date.strftime('%Y-%m-%d'))

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Participantes",
            stats['total_participants'],
            help="Número de indicativos únicos"
        )
    
    with col2:
        st.metric(
            "Total Reportes",
            stats['total_reports'],
            help="Número total de reportes registrados"
        )
    
    with col3:
        avg_per_participant = stats['total_reports'] / max(stats['total_participants'], 1)
        st.metric(
            "Promedio por Participante",
            f"{avg_per_participant:.1f}",
            help="Reportes promedio por participante"
        )
    
    with col4:
        if not stats['signal_quality'].empty:
            good_signals = stats['signal_quality'][stats['signal_quality']['signal_quality'] == 3]['count'].sum()
            total_signals = stats['signal_quality']['count'].sum()
            good_percentage = (good_signals / max(total_signals, 1)) * 100
            st.metric(
                "% Señales Buenas",
                f"{good_percentage:.1f}%",
                help="Porcentaje de señales reportadas como buenas"
            )
        else:
            st.metric("% Señales Buenas", "0%")
    
    # Gráficas - Primera fila
    col1, col2 = st.columns(2)
    
    with col1:
        # Participantes por zona
        if not stats['by_zona'].empty:
            st.subheader("Participantes por Zona")
            
            fig_zona = px.bar(
                stats['by_zona'],
                x='zona',
                y='count',
                title="Distribución por Zonas",
                labels={'zona': 'Zona', 'count': 'Participantes'},
                color='count',
                color_continuous_scale='Blues'
            )
            fig_zona.update_layout(showlegend=False)
            st.plotly_chart(fig_zona, use_container_width=True)
        else:
            st.info("No hay datos de zonas disponibles")
    
    with col2:
        # Participantes por sistema
        if not stats['by_sistema'].empty:
            st.subheader("Participantes por Sistema")
            
            fig_sistema = px.pie(
                stats['by_sistema'],
                values='count',
                names='sistema',
                title="Distribución por Sistemas"
            )
            st.plotly_chart(fig_sistema, use_container_width=True)
        else:
            st.info("No hay datos de sistemas disponibles")
    
    # Gráficas - Segunda fila
    col1, col2 = st.columns(2)
    
    with col1:
        # Participantes por región
        if not stats['by_region'].empty:
            st.subheader("Participantes por Región")
            
            fig_region = px.bar(
                stats['by_region'],
                x='region',
                y='count',
                title="Distribución por Estados",
                labels={'region': 'Estado', 'count': 'Participantes'}
            )
            fig_region.update_layout(showlegend=False)
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("No hay datos de regiones disponibles")
    
    with col2:
        # Calidad de señal
        if not stats['signal_quality'].empty:
            st.subheader("Distribución de Calidad de Señal")
            
            quality_df = stats['signal_quality'].copy()
            quality_df['quality_text'] = quality_df['signal_quality'].map(get_signal_quality_text)
            
            fig_quality = px.pie(
                quality_df,
                values='count',
                names='quality_text',
                title="Calidad de Señales Reportadas"
            )
            st.plotly_chart(fig_quality, use_container_width=True)
        else:
            st.info("No hay datos de calidad de señal disponibles")
    
    # Estaciones más activas
    if not stats['most_active'].empty:
        st.subheader("Estaciones Más Activas")
        
        active_df = stats['most_active'].head(10)
        fig_active = px.bar(
            active_df,
            x='call_sign',
            y='reports_count',
            title="Top 10 Estaciones por Número de Reportes",
            labels={'call_sign': 'Indicativo', 'reports_count': 'Reportes'}
        )
        fig_active.update_layout(showlegend=False)
        st.plotly_chart(fig_active, use_container_width=True)
    
    # Actividad por hora
    if not stats['by_hour'].empty:
        st.subheader("Actividad por Hora")
        
        fig_hour = px.line(
            stats['by_hour'],
            x='hour',
            y='count',
            title="Reportes por Hora del Día",
            labels={'hour': 'Hora', 'count': 'Número de Reportes'}
        )
        fig_hour.update_traces(mode='lines+markers')
        st.plotly_chart(fig_hour, use_container_width=True)

# Página: Gestión de Reportes
elif page == "📋 Gestión de Reportes":
    st.header("Gestión de Reportes")
    
    # Búsqueda
    search_term = st.text_input(
        "🔍 Buscar reportes:",
        placeholder="Buscar por indicativo, nombre o QTH",
        help="Ingresa cualquier término para buscar en los reportes"
    )
    
    # Obtener reportes
    if search_term:
        reports_df = db.search_reports(search_term)
        st.subheader(f"Resultados de búsqueda: '{search_term}'")
    else:
        reports_df = db.get_all_reports(session_date)
        st.subheader(f"Todos los reportes - {session_date.strftime('%d/%m/%Y')}")
    
    if not reports_df.empty:
        # Mostrar reportes con opciones de edición
        for idx, report in reports_df.iterrows():
            with st.expander(f"{report['call_sign']} - {report['operator_name']} ({format_timestamp(report['timestamp'])})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Indicativo:** {report['call_sign']}")
                    st.write(f"**Operador:** {report['operator_name']}")
                    st.write(f"**QTH:** {report['qth']}")
                
                with col2:
                    st.write(f"**Señal:** {report['signal_report']}")
                    st.write(f"**Zona:** {report.get('zona', 'N/A')}")
                    st.write(f"**Sistema:** {report.get('sistema', 'N/A')}")
                    st.write(f"**Región:** {report.get('region', 'N/A')}")
                    if report.get('observations'):
                        st.write(f"**Observaciones:** {report['observations']}")
                
                with col3:
                    if st.button(f"🗑️ Eliminar", key=f"delete_{report['id']}"):
                        try:
                            db.delete_report(report['id'])
                            st.success("Reporte eliminado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar reporte: {str(e)}")
    else:
        st.info("No se encontraron reportes.")

# Página: Historial de Estaciones
elif page == "📻 Historial de Estaciones":
    st.header("Historial de Estaciones")
    
    # Obtener historial
    station_history = db.get_station_history(100)
    
    if not station_history.empty:
        # Métricas del historial
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_stations = len(station_history)
            st.metric("Total de Estaciones", total_stations)
        
        with col2:
            most_used = station_history.iloc[0] if len(station_history) > 0 else None
            if most_used is not None:
                st.metric("Más Utilizada", most_used['call_sign'], f"{most_used['use_count']} usos")
        
        with col3:
            avg_uses = station_history['use_count'].mean()
            st.metric("Promedio de Usos", f"{avg_uses:.1f}")
        
        # Búsqueda en historial
        search_history = st.text_input(
            "🔍 Buscar en historial:",
            placeholder="Buscar por indicativo, operador o QTH"
        )
        
        # Filtrar historial si hay búsqueda
        if search_history:
            filtered_history = station_history[
                station_history['call_sign'].str.contains(search_history, case=False, na=False) |
                station_history['operator_name'].str.contains(search_history, case=False, na=False) |
                station_history['qth'].str.contains(search_history, case=False, na=False)
            ]
        else:
            filtered_history = station_history
        
        # Mostrar tabla de historial
        if not filtered_history.empty:
            st.subheader("Estaciones en el Historial")
            
            # Preparar datos para mostrar
            display_history = filtered_history.copy()
            display_history['last_used'] = pd.to_datetime(display_history['last_used']).dt.strftime('%d/%m/%Y %H:%M')
            display_history = display_history[['call_sign', 'operator_name', 'qth', 'zona', 'sistema', 'use_count', 'last_used']]
            display_history.columns = ['Indicativo', 'Operador', 'QTH', 'Zona', 'Sistema', 'Usos', 'Último Uso']
            
            st.dataframe(
                display_history,
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfica de estaciones más utilizadas
            if len(filtered_history) > 0:
                st.subheader("Estaciones Más Utilizadas")
                
                top_stations = filtered_history.head(10)
                fig_stations = px.bar(
                    top_stations,
                    x='call_sign',
                    y='use_count',
                    title="Top 10 Estaciones por Número de Usos",
                    labels={'call_sign': 'Indicativo', 'use_count': 'Número de Usos'}
                )
                fig_stations.update_layout(showlegend=False)
                st.plotly_chart(fig_stations, use_container_width=True)
        else:
            st.info("No se encontraron estaciones en el historial con ese criterio de búsqueda.")
    else:
        st.info("No hay estaciones en el historial aún.")

# Página: Exportar Datos
elif page == "📁 Exportar Datos":
    st.header("Exportar Datos")
    
    # Opciones de exportación
    col1, col2 = st.columns(2)
    
    with col1:
        export_date = st.date_input(
            "Fecha de sesión a exportar:",
            value=session_date
        )
        
        export_format = st.selectbox(
            "Formato de exportación:",
            ["CSV", "Excel", "PDF"]
        )
    
    with col2:
        include_stats = st.checkbox(
            "Incluir estadísticas",
            value=True,
            help="Incluir resumen estadístico en la exportación"
        )
        
        all_sessions = st.checkbox(
            "Exportar todas las sesiones",
            value=False,
            help="Exportar datos de todas las fechas"
        )
    
    if st.button("📥 Generar Exportación", use_container_width=True):
        try:
            # Obtener datos
            if all_sessions:
                export_df = db.get_all_reports()
                stats = db.get_statistics() if include_stats else None
            else:
                export_df = db.get_all_reports(export_date)
                stats = db.get_statistics(export_date) if include_stats else None
            
            if export_df.empty:
                st.warning("No hay datos para exportar en el período seleccionado.")
            else:
                # Generar exportación según formato
                if export_format == "CSV":
                    data, filename = exporter.export_to_csv(export_df)
                    st.download_button(
                        label="📄 Descargar CSV",
                        data=data,
                        file_name=filename,
                        mime="text/csv"
                    )
                
                elif export_format == "Excel":
                    data, filename = exporter.export_to_excel(export_df)
                    st.download_button(
                        label="📊 Descargar Excel",
                        data=data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                elif export_format == "PDF":
                    try:
                        data, filename = exporter.export_to_pdf(export_df, stats, session_date=export_date, current_user=current_user)
                        st.download_button(
                            label="📑 Descargar PDF",
                            data=data,
                            file_name=filename,
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Error al generar PDF: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                
                # Mostrar resumen
                st.success(f"✅ Exportación generada: {len(export_df)} reportes")
                
                if include_stats and stats:
                    summary = exporter.create_session_summary(stats, export_date)
                    
                    st.subheader("Resumen de la Exportación")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Participantes", summary['total_participantes'])
                    with col2:
                        st.metric("Reportes", summary['total_reportes'])
                    with col3:
                        if summary['calidad_señal']:
                            buenas = summary['calidad_señal'].get('Buena', {}).get('porcentaje', 0)
                            st.metric("% Señales Buenas", f"{buenas}%")
        
        except Exception as e:
            st.error(f"❌ Error al generar exportación: {str(e)}")

# Página: Buscar/Editar
elif page == "🔍 Buscar/Editar":
    st.header("Buscar y Editar Reportes")
    
    # Búsqueda de reportes
    search_term = st.text_input(
        "🔍 Buscar reportes:",
        placeholder="Buscar por indicativo, operador, QTH, zona o sistema"
    )
    
    # Filtros adicionales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_date = st.date_input(
            "Filtrar por fecha:",
            value=None,
            help="Dejar vacío para buscar en todas las fechas"
        )
    
    with col2:
        # Obtener zonas únicas de la base de datos
        available_zones = db.get_distinct_zones()
        search_zona = st.selectbox(
            "Filtrar por zona:",
            ["Todas"] + available_zones
        )
    
    with col3:
        # Obtener sistemas únicos de la base de datos
        available_systems = db.get_distinct_systems()
        search_sistema = st.selectbox(
            "Filtrar por sistema:",
            ["Todos"] + available_systems
        )
    
    # Obtener reportes filtrados
    if search_term or search_date or search_zona != "Todas" or search_sistema != "Todos":
        # Construir filtros
        filters = {}
        if search_date:
            filters['session_date'] = search_date.strftime('%Y-%m-%d')
        if search_zona != "Todas":
            filters['zona'] = search_zona
        if search_sistema != "Todos":
            filters['sistema'] = search_sistema
        
        # Buscar reportes
        reports_df = db.search_reports(search_term, filters)
        
        if not reports_df.empty:
            st.subheader(f"Resultados de búsqueda ({len(reports_df)} reportes)")
            
            # Mostrar reportes encontrados
            for idx, report in reports_df.iterrows():
                with st.expander(f"📻 {report['call_sign']} - {report['operator_name']} ({report['session_date']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Indicativo:** {report['call_sign']}")
                        st.write(f"**Operador:** {report['operator_name']}")
                        if 'estado' in report and report['estado']:
                            st.write(f"**Estado:** {report['estado']}")
                        if 'ciudad' in report and report['ciudad']:
                            st.write(f"**Ciudad:** {report['ciudad']}")
                        elif 'qth' in report and report['qth']:
                            st.write(f"**QTH:** {report['qth']}")
                        st.write(f"**Zona:** {report['zona']}")
                        st.write(f"**Sistema:** {report['sistema']}")
                    
                    with col2:
                        st.write(f"**Reporte de Señal:** {report['signal_report']}")
                        st.write(f"**Fecha:** {report['session_date']}")
                        if report['observations']:
                            st.write(f"**Observaciones:** {report['observations']}")
                    
                    # Botón para eliminar
                    if st.button(f"🗑️ Eliminar Reporte", key=f"delete_{report['id']}"):
                        try:
                            db.delete_report(report['id'])
                            st.success("Reporte eliminado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar reporte: {str(e)}")
        else:
            st.info("No se encontraron reportes con los criterios de búsqueda especificados.")
    else:
        st.info("Ingresa un término de búsqueda o selecciona filtros para buscar reportes.")

# Página: Ranking y Reconocimientos
elif page == "🏆 Ranking":
    show_motivational_dashboard()

# Página: Mi Perfil
elif page == "👤 Mi Perfil":
    show_profile_management()

# Página: Gestión de Usuarios
elif page == "👥 Gestión de Usuarios":
    show_user_management()

def show_profile_management():
    """Muestra la página de gestión de perfil del usuario"""
    st.header("👤 Mi Perfil")
    st.markdown("### Gestiona tu información personal")
    
    # Obtener información actual del usuario
    user_info = db.get_user_by_username(current_user['username'])
    
    if not user_info:
        st.error("❌ Error al cargar información del usuario")
        return
    
    # Convertir tupla a diccionario usando índices conocidos
    # Estructura real: (id, username, password_hash, full_name, email, role, preferred_system, hf_frequency_pref, hf_mode_pref, hf_power_pref, created_at, last_login)
    user_dict = {
        'id': user_info[0],
        'username': user_info[1],
        'password_hash': user_info[2],
        'full_name': user_info[3] if len(user_info) > 3 else '',
        'email': user_info[4] if len(user_info) > 4 else '',
        'role': user_info[5] if len(user_info) > 5 else '',
        'preferred_system': user_info[6] if len(user_info) > 6 else 'ASL',
        'created_at': user_info[10] if len(user_info) > 10 else '',
        'last_login': user_info[11] if len(user_info) > 11 else ''
    }
    
    # Crear tabs para organizar la información
    tab1, tab2 = st.tabs(["📝 Información Personal", "🔐 Cambiar Contraseña"])
    
    with tab1:
        st.subheader("Actualizar Información Personal")
        
        with st.form("update_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_full_name = st.text_input(
                    "Nombre Completo:",
                    value=user_dict['full_name'],
                    help="Tu nombre completo como aparecerá en los reportes"
                )
                
                new_email = st.text_input(
                    "Correo Electrónico:",
                    value=user_dict['email'],
                    help="Tu dirección de correo electrónico"
                )
            
            with col2:
                st.text_input(
                    "Nombre de Usuario:",
                    value=user_dict['username'],
                    disabled=True,
                    help="El nombre de usuario no se puede cambiar"
                )
                
                st.text_input(
                    "Rol:",
                    value=user_dict['role'].title(),
                    disabled=True,
                    help="Tu rol en el sistema"
                )
            
            # Información adicional
            st.markdown("---")
            col3, col4 = st.columns(2)
            
            with col3:
                if user_dict['created_at']:
                    formatted_created = format_timestamp(user_dict['created_at'])
                    st.info(f"📅 **Miembro desde:** {formatted_created}")
            
            with col4:
                if user_dict['last_login']:
                    formatted_login = format_timestamp(user_dict['last_login'])
                    st.info(f"🕒 **Último acceso:** {formatted_login}")
            
            submitted = st.form_submit_button("💾 Actualizar Información", type="primary")
            
            if submitted:
                # Validar datos
                if not new_full_name.strip():
                    st.error("❌ El nombre completo es obligatorio")
                elif not new_email.strip():
                    st.error("❌ El correo electrónico es obligatorio")
                elif '@' not in new_email:
                    st.error("❌ Ingresa un correo electrónico válido")
                else:
                    # Actualizar información
                    success = db.update_user_profile(
                        user_dict['id'],
                        new_full_name.strip(),
                        new_email.strip()
                    )
                    
                    if success:
                        st.success("✅ Información actualizada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar la información")
    
    with tab2:
        st.subheader("Cambiar Contraseña")
        
        with st.form("change_password_form"):
            current_password = st.text_input(
                "Contraseña Actual:",
                type="password",
                help="Ingresa tu contraseña actual para confirmar el cambio"
            )
            
            new_password = st.text_input(
                "Nueva Contraseña:",
                type="password",
                help="Mínimo 6 caracteres"
            )
            
            confirm_password = st.text_input(
                "Confirmar Nueva Contraseña:",
                type="password",
                help="Repite la nueva contraseña"
            )
            
            submitted_password = st.form_submit_button("🔐 Cambiar Contraseña", type="primary")
            
            if submitted_password:
                # Validar contraseña actual
                if not auth.verify_password(current_password, user_dict['password_hash']):
                    st.error("❌ La contraseña actual es incorrecta")
                elif len(new_password) < 6:
                    st.error("❌ La nueva contraseña debe tener al menos 6 caracteres")
                elif new_password != confirm_password:
                    st.error("❌ Las contraseñas no coinciden")
                elif current_password == new_password:
                    st.error("❌ La nueva contraseña debe ser diferente a la actual")
                else:
                    # Cambiar contraseña
                    success = db.change_user_password(
                        user_dict['id'],
                        new_password
                    )
                    
                    if success:
                        st.success("✅ Contraseña cambiada correctamente")
                        st.info("🔄 Por seguridad, deberás iniciar sesión nuevamente")
                        if st.button("🚪 Cerrar Sesión"):
                            auth.logout()
                    else:
                        st.error("❌ Error al cambiar la contraseña")

def show_motivational_dashboard():
    """Muestra el dashboard de rankings y reconocimientos"""
    st.header("🏆 Ranking")
    st.markdown("### ¡Competencia Sana entre Radioaficionados!")
    
    # Obtener estadísticas motivacionales
    motivational_stats = db.get_motivational_stats()
    
    # Pestañas para organizar las estadísticas
    tab1, tab2, tab3, tab4 = st.tabs(["🥇 Estaciones Top", "🌍 Zonas Activas", "📡 Sistemas Populares", "📊 Resumen General"])
    
    with tab1:
        st.subheader("🎯 Estaciones Más Reportadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Este Año**")
            if not motivational_stats['top_stations_year'].empty:
                for idx, row in motivational_stats['top_stations_year'].head(5).iterrows():
                    if idx == 0:
                        st.markdown(f"🥇 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 1:
                        st.markdown(f"🥈 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 2:
                        st.markdown(f"🥉 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    else:
                        st.markdown(f"🏅 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
            else:
                st.info("No hay datos suficientes para mostrar el ranking anual")
        
        with col2:
            st.markdown("#### 📆 **Este Mes**")
            if not motivational_stats['top_stations_month'].empty:
                for idx, row in motivational_stats['top_stations_month'].head(5).iterrows():
                    if idx == 0:
                        st.markdown(f"🥇 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 1:
                        st.markdown(f"🥈 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    elif idx == 2:
                        st.markdown(f"🥉 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
                    else:
                        st.markdown(f"🏅 **{row['call_sign']}** - {row['operator_name']}")
                        st.markdown(f"   📊 {row['total_reports']} reportes")
            else:
                st.info("No hay datos suficientes para mostrar el ranking mensual")
    
    with tab2:
        st.subheader("🌍 Zonas Más Activas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Este Año**")
            if not motivational_stats['top_zones_year'].empty:
                for idx, row in motivational_stats['top_zones_year'].iterrows():
                    st.markdown(f"🏆 **Zona {row['zona']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de zonas para este año")
        
        with col2:
            st.markdown("#### 📆 **Este Mes**")
            if not motivational_stats['top_zones_month'].empty:
                for idx, row in motivational_stats['top_zones_month'].iterrows():
                    st.markdown(f"🏆 **Zona {row['zona']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de zonas para este mes")
    
    with tab3:
        st.subheader("📡 Sistemas Más Utilizados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Este Año**")
            if not motivational_stats['top_systems_year'].empty:
                for idx, row in motivational_stats['top_systems_year'].iterrows():
                    st.markdown(f"🔧 **{row['sistema']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de sistemas para este año")
        
        with col2:
            st.markdown("#### 📆 **Este Mes**")
            if not motivational_stats['top_systems_month'].empty:
                for idx, row in motivational_stats['top_systems_month'].iterrows():
                    st.markdown(f"🔧 **{row['sistema']}**")
                    st.markdown(f"   👥 {row['unique_stations']} estaciones únicas")
                    st.markdown(f"   📊 {row['total_reports']} reportes totales")
                    st.markdown("---")
            else:
                st.info("No hay datos de sistemas para este mes")
    
    with tab4:
        st.subheader("📊 Resumen General de Actividad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 **Estadísticas del Año**")
            if not motivational_stats['general_year'].empty:
                year_stats = motivational_stats['general_year'].iloc[0]
                st.metric("📊 Total Reportes", year_stats['total_reports'])
                st.metric("👥 Estaciones Únicas", year_stats['unique_stations'])
                st.metric("📅 Días Activos", year_stats['active_days'])
            else:
                st.info("No hay estadísticas generales del año")
        
        with col2:
            st.markdown("#### 📆 **Estadísticas del Mes**")
            if not motivational_stats['general_month'].empty:
                month_stats = motivational_stats['general_month'].iloc[0]
                st.metric("📊 Total Reportes", month_stats['total_reports'])
                st.metric("👥 Estaciones Únicas", month_stats['unique_stations'])
                st.metric("📅 Días Activos", month_stats['active_days'])
            else:
                st.info("No hay estadísticas generales del mes")
    
    # Mensaje motivacional
    st.markdown("---")
    st.markdown("### 🎉 ¡Sigue Participando!")
    st.info("💪 **¡Cada reporte cuenta!** Mantente activo en las redes y ayuda a tu zona y sistema favorito a liderar las estadísticas. ¡La competencia sana nos hace crecer como comunidad radioaficionada! 📻✨")

def show_user_management():
    # Verificar si el usuario es admin
    if current_user['role'] != 'admin':
        st.error("❌ Acceso denegado. Solo los administradores pueden acceder a esta sección.")
        st.stop()
        
    st.header("👥 Gestión de Usuarios")
    
    # Inicializar servicio de email
    if 'email_service' not in st.session_state:
        st.session_state.email_service = EmailService()
    
    email_service = st.session_state.email_service
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Usuarios", "➕ Crear Usuario", "🔄 Recuperar Contraseña", "⚙️ Configuración Email"])
    
    with tab1:
        st.subheader("Lista de Usuarios")
        
        # Obtener usuarios
        users = db.get_all_users()
        
        if users is not None and len(users) > 0:
            for user in users:
                with st.expander(f"👤 {user['username']} ({user['role']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Usuario:** {user['username']}")
                        st.write(f"**Nombre:** {user.get('full_name', 'N/A')}")
                        st.write(f"**Rol:** {user['role']}")
                        if user.get('email'):
                            st.write(f"**Email:** {user['email']}")
                        st.write(f"**Creado:** {user.get('created_at', 'N/A')}")
                    
                    with col2:
                        # Botón para editar usuario
                        if st.button(f"✏️ Editar", key=f"edit_user_{user['id']}"):
                            st.session_state[f"editing_user_{user['id']}"] = True
                            st.rerun()
                        
                        # Solo permitir eliminar si no es el usuario actual y no es admin
                        if user['username'] != current_user['username'] and user['username'] != 'admin':
                            if st.button(f"🗑️ Eliminar", key=f"delete_user_{user['id']}"):
                                try:
                                    db.delete_user(user['id'])
                                    st.success(f"Usuario {user['username']} eliminado")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al eliminar usuario: {str(e)}")
                        else:
                            st.info("No se puede eliminar este usuario")
                    
                    # Formulario de edición si está activado
                    if st.session_state.get(f"editing_user_{user['id']}", False):
                        st.markdown("---")
                        st.subheader("✏️ Editar Usuario")
                        
                        with st.form(f"edit_user_form_{user['id']}"):
                            edit_full_name = st.text_input("Nombre completo:", value=user.get('full_name', ''))
                            edit_email = st.text_input("Email:", value=user.get('email', ''))
                            edit_role = st.selectbox("Rol:", ["operator", "admin"], 
                                                   index=0 if user['role'] == 'operator' else 1)
                            
                            # Opción para cambiar contraseña
                            change_password = st.checkbox("Cambiar contraseña")
                            new_password = ""
                            confirm_new_password = ""
                            
                            if change_password:
                                new_password = st.text_input("Nueva contraseña:", type="password", 
                                                           help="Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 carácter especial")
                                confirm_new_password = st.text_input("Confirmar nueva contraseña:", type="password")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                save_changes = st.form_submit_button("💾 Guardar Cambios")
                            
                            with col_cancel:
                                cancel_edit = st.form_submit_button("❌ Cancelar")
                            
                            if save_changes:
                                # Validar campos obligatorios
                                if not edit_full_name or not edit_email:
                                    st.error("❌ Nombre completo y email son obligatorios")
                                else:
                                    # Validar contraseña si se va a cambiar
                                    password_valid = True
                                    if change_password:
                                        if new_password != confirm_new_password:
                                            st.error("❌ Las contraseñas no coinciden")
                                            password_valid = False
                                        else:
                                            from utils import validate_password
                                            is_valid, message = validate_password(new_password)
                                            if not is_valid:
                                                st.error(f"❌ {message}")
                                                password_valid = False
                                    
                                    if password_valid:
                                        try:
                                            # Actualizar información del usuario
                                            db.update_user(user['id'], edit_full_name, edit_role, edit_email)
                                            
                                            # Cambiar contraseña si se solicitó
                                            if change_password:
                                                import hashlib
                                                password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                                                db.change_password(user['username'], password_hash)
                                            
                                            st.success("✅ Usuario actualizado exitosamente")
                                            
                                            # Limpiar estado de edición
                                            del st.session_state[f"editing_user_{user['id']}"]
                                            st.rerun()
                                            
                                        except Exception as e:
                                            st.error(f"❌ Error al actualizar usuario: {str(e)}")
                            
                            if cancel_edit:
                                # Limpiar estado de edición
                                del st.session_state[f"editing_user_{user['id']}"]
                                st.rerun()
        else:
            st.info("No hay usuarios registrados")
    
    with tab2:
        st.subheader("➕ Crear Nuevo Usuario")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Nombre de usuario:")
            new_full_name = st.text_input("Nombre completo:")
            new_email = st.text_input("Email:")
            new_password = st.text_input("Contraseña:", type="password", help="Mínimo 8 caracteres, 1 mayúscula, 1 número, 1 carácter especial")
            confirm_password = st.text_input("Confirmar contraseña:", type="password")
            new_role = st.selectbox("Rol:", ["operator", "admin"])
            
            submit_create = st.form_submit_button("✅ Crear Usuario")
            
            if submit_create:
                if new_username and new_full_name and new_email and new_password and confirm_password:
                    # Validar que las contraseñas coincidan
                    if new_password != confirm_password:
                        st.error("❌ Las contraseñas no coinciden")
                    else:
                        # Validar fortaleza de la contraseña
                        from utils import validate_password
                        is_valid, message = validate_password(new_password)
                        
                        if not is_valid:
                            st.error(f"❌ {message}")
                        else:
                            try:
                                # Crear usuario
                                user_id = db.create_user(new_username, new_password, new_full_name, new_email, new_role)
                                
                                if user_id:
                                    st.success(f"🎉 ¡Usuario creado exitosamente!")
                                    st.info(f"👤 **Usuario:** {new_username}")
                                    st.info(f"👨‍💼 **Nombre:** {new_full_name}")
                                    st.info(f"📧 **Email:** {new_email}")
                                    st.info(f"🎭 **Rol:** {new_role.title()}")
                                    
                                    # Enviar email de bienvenida si está configurado
                                    if email_service.is_configured():
                                        user_data = {
                                            'username': new_username,
                                            'full_name': new_full_name,
                                            'email': new_email,
                                            'role': new_role
                                        }
                                        
                                        if email_service.send_welcome_email(user_data, new_password):
                                            st.success("📧 Email de bienvenida enviado correctamente")
                                        else:
                                            st.warning("⚠️ Usuario creado pero no se pudo enviar el email")
                                    else:
                                        st.warning("⚠️ Usuario creado. Configura SMTP para enviar credenciales por email")
                                    
                                    # Esperar un momento antes de recargar para que se vea el mensaje
                                    import time
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Error al crear usuario (posiblemente el usuario ya existe)")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Por favor completa todos los campos")
    
    with tab3:
        st.subheader("🔄 Recuperar Contraseña")
        
        with st.form("password_recovery_form"):
            recovery_email = st.text_input("Email del usuario:")
            submit_recovery = st.form_submit_button("📧 Enviar Email de Recuperación")
            
            if submit_recovery:
                if recovery_email:
                    if email_service.is_configured():
                        try:
                            # Buscar usuario por email
                            user = db.get_user_by_email(recovery_email)
                            
                            if user:
                                # Generar token y enviar email
                                if email_service.send_password_reset_email(user):
                                    st.success("📧 Email de recuperación enviado")
                                else:
                                    st.error("❌ Error al enviar email de recuperación")
                            else:
                                st.error("❌ No se encontró usuario con ese email")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                    else:
                        st.error("❌ Servicio de email no configurado")
                else:
                    st.error("❌ Por favor ingresa un email")
    
    with tab4:
        st.subheader("⚙️ Configuración del Servicio de Email")
        
        # Estado actual del servicio
        if email_service.is_configured():
            st.success("✅ Servicio de email configurado")
            st.info(f"Servidor: {email_service.smtp_server}:{email_service.smtp_port}")
            st.info(f"Usuario: {email_service.smtp_username}")
        else:
            st.warning("⚠️ Servicio de email no configurado")
        
        with st.form("email_config_form"):
            st.write("**Configuración SMTP:**")
            
            smtp_server = st.text_input("Servidor SMTP:", value=email_service.smtp_server or "smtp.gmail.com")
            smtp_port = st.number_input("Puerto SMTP:", value=email_service.smtp_port or 587, min_value=1, max_value=65535)
            smtp_username = st.text_input("Usuario SMTP:", value=email_service.smtp_username or "")
            smtp_password = st.text_input("Contraseña SMTP:", type="password")
            from_email = st.text_input("Email remitente:", value=email_service.from_email or smtp_username)
            from_name = st.text_input("Nombre remitente:", value=email_service.from_name or "Sistema FMRE")
            
            submit_config = st.form_submit_button("💾 Guardar Configuración")
            
            if submit_config:
                if smtp_server and smtp_username and smtp_password:
                    email_service.configure_smtp(
                        smtp_server=smtp_server,
                        smtp_port=smtp_port,
                        smtp_username=smtp_username,
                        smtp_password=smtp_password,
                        from_email=from_email or smtp_username,
                        from_name=from_name
                    )
                    st.success("✅ Configuración de email guardada")
                    st.rerun()
                else:
                    st.error("❌ Por favor completa los campos obligatorios")

# Footer
st.markdown("---")
# Footer con logo usando base64
import base64
try:
    with open("assets/LogoFMRE_small.png", "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <div style='text-align: center; color: #666;'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 5px;'>
                <img src="data:image/png;base64,{logo_data}" alt="FMRE Logo" style="max-width: 100%; height: auto;">
                <span style="font-weight: bold;">SIGQ v1.3</span>
            </div>
            <div>
                Federación Mexicana de Radioexperimentadores<br>
                Desarrollado con ❤️ por los miembros del Radio Club Guadiana A.C.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
except:
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            📻 FMRE SIR v1.0 | Federación Mexicana de Radioexperimentadores<br>
            Desarrollado con ❤️ por los miembros del Radio Club Guadiana A.C.
        </div>
        """,
        unsafe_allow_html=True
    )
