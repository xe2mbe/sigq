import re
from datetime import datetime

def validate_call_sign(call_sign):
    """
    Valida el formato del indicativo de llamada mexicano
    Formato típico: XE1ABC, XE2ABC, etc.
    """
    if not call_sign:
        return False, "El indicativo no puede estar vacío"
    
    # Patrón para indicativos mexicanos
    pattern = r'^(XE|XF|4A|6D)[0-9][A-Z]{1,3}$'
    
    if re.match(pattern, call_sign.upper()):
        return True, ""
    else:
        return False, "Formato de indicativo inválido. Ejemplo: XE1ABC, XE2DEF"

def validate_qth(qth):
    """Valida el formato del QTH (ubicación) - DEPRECATED, usar validate_ciudad"""
    if not qth or len(qth.strip()) < 2:
        return False, "El QTH debe tener al menos 2 caracteres"
    
    if len(qth) > 50:
        return False, "El QTH no puede exceder 50 caracteres"
    
    return True, ""

def validate_operator_name(name):
    """Valida el nombre del operador"""
    if not name or len(name.strip()) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    if len(name) > 100:
        return False, "El nombre no puede exceder 100 caracteres"
    
    # Solo letras, espacios y algunos caracteres especiales
    pattern = r'^[A-Za-zÀ-ÿ\s\-\.]+$'
    if not re.match(pattern, name):
        return False, "El nombre solo puede contener letras, espacios, guiones y puntos"
    
    return True, ""

def validate_signal_report(signal):
    """Valida el reporte de señal"""
    if not signal:
        return False, "El reporte de señal es obligatorio"
    
    valid_signals = [
        'buena', 'regular', 'mala', 'excelente', 'fuerte', 'débil',
        '5', '4', '3', '2', '1', '59', '58', '57', '56', '55'
    ]
    
    if signal.lower() in valid_signals or any(vs in signal.lower() for vs in valid_signals):
        return True, ""
    else:
        return False, "Reporte de señal inválido. Use: Buena/Regular/Mala o escala RST"

def format_call_sign(call_sign):
    """Formatea el indicativo en mayúsculas"""
    return call_sign.upper().strip() if call_sign else ""

def format_qth(qth):
    """Formatea el QTH en mayúsculas"""
    return qth.upper().strip() if qth else ""

def format_name(name):
    """Formatea el nombre con capitalización apropiada"""
    return name.title().strip() if name else ""

def get_mexican_states():
    """Retorna lista de estados mexicanos con sus códigos"""
    return {
        'AG': 'Aguascalientes',
        'BC': 'Baja California',
        'BS': 'Baja California Sur',
        'CM': 'Campeche',
        'CS': 'Chiapas',
        'CH': 'Chihuahua',
        'CO': 'Coahuila',
        'CL': 'Colima',
        'DF': 'Ciudad de México',
        'DG': 'Durango',
        'GT': 'Guanajuato',
        'GR': 'Guerrero',
        'HG': 'Hidalgo',
        'JA': 'Jalisco',
        'EM': 'Estado de México',
        'MI': 'Michoacán',
        'MO': 'Morelos',
        'NA': 'Nayarit',
        'NL': 'Nuevo León',
        'OA': 'Oaxaca',
        'PU': 'Puebla',
        'QT': 'Querétaro',
        'QR': 'Quintana Roo',
        'SL': 'San Luis Potosí',
        'SI': 'Sinaloa',
        'SO': 'Sonora',
        'TB': 'Tabasco',
        'TM': 'Tamaulipas',
        'TL': 'Tlaxcala',
        'VE': 'Veracruz',
        'YU': 'Yucatán',
        'ZA': 'Zacatecas'
    }

def get_estados_list():
    """Retorna lista ordenada de estados para dropdown"""
    estados = ['Extranjera']  # Primera opción
    estados.extend(sorted(get_mexican_states().values()))
    return estados

def validate_estado(estado):
    """Valida el estado seleccionado"""
    valid_estados = get_estados_list()
    
    if not estado:
        return False, "El estado es obligatorio"
    
    if estado not in valid_estados:
        return False, f"Estado inválido. Debe ser uno de la lista"
    
    return True, ""

def validate_ciudad(ciudad):
    """Valida el campo ciudad"""
    if not ciudad or len(ciudad.strip()) < 2:
        return False, "La ciudad debe tener al menos 2 caracteres"
    
    if len(ciudad) > 50:
        return False, "La ciudad no puede exceder 50 caracteres"
    
    return True, ""

def extract_region_from_qth(qth):
    """Extrae la región del QTH basado en los primeros caracteres"""
    if not qth or len(qth) < 2:
        return "XX"
    
    region_code = qth[:2].upper()
    states = get_mexican_states()
    
    if region_code in states:
        return region_code
    else:
        # Intentar encontrar coincidencia parcial
        for code, state in states.items():
            if state.upper().startswith(qth[:3].upper()):
                return code
        return "XX"  # Región desconocida

def format_timestamp(timestamp):
    """Formatea timestamp para mostrar"""
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return timestamp
    else:
        dt = timestamp
    
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def get_signal_quality_text(quality_num):
    """Convierte calidad numérica a texto"""
    quality_map = {
        1: "Mala",
        2: "Regular", 
        3: "Buena"
    }
    return quality_map.get(quality_num, "Desconocida")

def validate_zona(zona):
    """Valida la zona seleccionada"""
    valid_zonas = ['XE1', 'XE2', 'XE3', 'Extranjera']
    
    if not zona:
        return False, "La zona es obligatoria"
    
    if zona not in valid_zonas:
        return False, f"Zona inválida. Debe ser: {', '.join(valid_zonas)}"
    
    return True, ""

def validate_sistema(sistema):
    """Valida el sistema seleccionado"""
    valid_sistemas = ['IRLP', 'ASL', 'DMR', 'Fusion', 'D-Star', 'Otro']
    
    if not sistema:
        return False, "El sistema es obligatorio"
    
    if sistema not in valid_sistemas:
        return False, f"Sistema inválido. Debe ser: {', '.join(valid_sistemas)}"
    
    return True, ""

def get_zonas():
    """Retorna lista de zonas disponibles"""
    return ['XE1', 'XE2', 'XE3', 'Extranjera']

def get_sistemas():
    """Retorna lista de sistemas disponibles"""
    return ['IRLP', 'ASL', 'DMR', 'Fusion', 'D-Star', 'Otro']

def validate_password(password):
    """Valida que la contraseña cumpla con los requisitos de seguridad"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return True, "Contraseña válida"

def validate_all_fields(call_sign, operator_name, estado, ciudad, signal_report, zona, sistema):
    """Valida todos los campos del formulario"""
    errors = []
    
    valid, msg = validate_call_sign(call_sign)
    if not valid:
        errors.append(f"Indicativo: {msg}")
    
    valid, msg = validate_operator_name(operator_name)
    if not valid:
        errors.append(f"Nombre: {msg}")
    
    valid, msg = validate_estado(estado)
    if not valid:
        errors.append(f"Estado: {msg}")
    
    valid, msg = validate_ciudad(ciudad)
    if not valid:
        errors.append(f"Ciudad: {msg}")
    
    valid, msg = validate_signal_report(signal_report)
    if not valid:
        errors.append(f"Señal: {msg}")
    
    valid, msg = validate_zona(zona)
    if not valid:
        errors.append(f"Zona: {msg}")
    
    valid, msg = validate_sistema(sistema)
    if not valid:
        errors.append(f"Sistema: {msg}")
    
    return len(errors) == 0, errors
