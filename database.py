import sqlite3
import pandas as pd
from datetime import datetime
import os

class FMREDatabase:
    def __init__(self, db_path="fmre_reports.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si necesitamos migrar la base de datos
        self._migrate_database(cursor)
        
        # Tabla de reportes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sign TEXT NOT NULL,
                operator_name TEXT NOT NULL,
                estado TEXT NOT NULL,
                ciudad TEXT NOT NULL,
                signal_report TEXT NOT NULL,
                zona TEXT NOT NULL,
                sistema TEXT NOT NULL,
                observations TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_date DATE,
                region TEXT,
                signal_quality INTEGER
            )
        ''')
        
        # Tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date DATE UNIQUE,
                total_participants INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'operator',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        ''')
        
        # Tabla de historial de estaciones (con compatibilidad para qth)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS station_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sign TEXT NOT NULL,
                operator_name TEXT NOT NULL,
                qth TEXT,
                estado TEXT,
                ciudad TEXT,
                zona TEXT NOT NULL,
                sistema TEXT NOT NULL,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                use_count INTEGER DEFAULT 1,
                UNIQUE(call_sign, operator_name)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _migrate_database(self, cursor):
        """Migra la base de datos agregando columnas faltantes"""
        try:
            # Verificar columnas en tabla reports
            cursor.execute("PRAGMA table_info(reports)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Agregar columna zona si no existe
            if 'zona' not in columns:
                cursor.execute("ALTER TABLE reports ADD COLUMN zona TEXT DEFAULT 'XE1'")
                print("Columna 'zona' agregada a la tabla reports")
            
            # Agregar columna sistema si no existe
            if 'sistema' not in columns:
                cursor.execute("ALTER TABLE reports ADD COLUMN sistema TEXT DEFAULT 'Otro'")
                print("Columna 'sistema' agregada a la tabla reports")
            
            # Agregar columna estado si no existe
            if 'estado' not in columns:
                cursor.execute("ALTER TABLE reports ADD COLUMN estado TEXT DEFAULT 'Extranjera'")
                print("Columna 'estado' agregada a la tabla reports")
            
            # Verificar y agregar columna email en users si no existe
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [column[1] for column in cursor.fetchall()]
            if 'email' not in user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
                print("Columna 'email' agregada a la tabla users")
            
            # Agregar columna ciudad si no existe
            if 'ciudad' not in columns:
                cursor.execute("ALTER TABLE reports ADD COLUMN ciudad TEXT DEFAULT ''")
                print("Columna 'ciudad' agregada a la tabla reports")
                
                # Migrar datos existentes de qth a ciudad
                cursor.execute("UPDATE reports SET ciudad = qth WHERE ciudad = ''")
                print("Datos de QTH migrados a ciudad")
            
            # Si existe la columna qth, hacerla opcional para compatibilidad
            if 'qth' in columns:
                # SQLite no permite modificar constraints directamente, pero podemos asegurar que qth tenga un valor
                cursor.execute("UPDATE reports SET qth = ciudad WHERE qth IS NULL OR qth = ''")
                print("Columna QTH actualizada para compatibilidad")
            
            # Verificar columnas en tabla station_history
            cursor.execute("PRAGMA table_info(station_history)")
            history_columns = [column[1] for column in cursor.fetchall()]
            
            # Agregar columnas faltantes en station_history
            if 'qth' not in history_columns:
                cursor.execute("ALTER TABLE station_history ADD COLUMN qth TEXT")
                print("Columna 'qth' agregada a la tabla station_history para compatibilidad")
            
            if 'estado' not in history_columns:
                cursor.execute("ALTER TABLE station_history ADD COLUMN estado TEXT DEFAULT 'Extranjera'")
                print("Columna 'estado' agregada a la tabla station_history")
            
            if 'ciudad' not in history_columns:
                cursor.execute("ALTER TABLE station_history ADD COLUMN ciudad TEXT DEFAULT ''")
                print("Columna 'ciudad' agregada a la tabla station_history")
                
                # Migrar datos existentes de qth a ciudad en historial
                cursor.execute("UPDATE station_history SET ciudad = qth WHERE ciudad = '' AND qth IS NOT NULL")
                print("Datos de QTH migrados a ciudad en historial")
            
            # Asegurar que qth tenga valores para compatibilidad
            cursor.execute("UPDATE station_history SET qth = ciudad WHERE qth IS NULL AND ciudad IS NOT NULL")
            cursor.execute("UPDATE station_history SET estado = 'Extranjera' WHERE estado IS NULL")
            cursor.execute("UPDATE station_history SET ciudad = 'N/A' WHERE ciudad IS NULL OR ciudad = ''")
            print("Valores por defecto aplicados en station_history")
                
        except Exception as e:
            print(f"Error durante la migración: {e}")
    
    def add_report(self, call_sign, operator_name, estado, ciudad, signal_report, zona, sistema, observations="", session_date=None):
        """Agrega un nuevo reporte a la base de datos"""
        if session_date is None:
            session_date = datetime.now().date()
        
        # Extraer región del estado
        if estado == "Extranjera":
            region = "EX"
        else:
            # Buscar código del estado
            states = {v: k for k, v in self._get_mexican_states().items()}
            region = states.get(estado, "XX")
        
        # Convertir señal a calidad numérica (1=mala, 2=regular, 3=buena)
        signal_quality = self._convert_signal_to_quality(signal_report)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar si la tabla tiene la columna qth (para compatibilidad)
            cursor.execute("PRAGMA table_info(reports)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'qth' in columns and 'ciudad' in columns:
                # Tabla tiene ambas columnas, insertar en ambas para compatibilidad
                cursor.execute('''
                    INSERT INTO reports (call_sign, operator_name, qth, estado, ciudad, signal_report, zona, sistema,
                                       observations, session_date, region, signal_quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (call_sign.upper(), operator_name, ciudad.title(), estado, ciudad.title(), signal_report, zona, sistema,
                      observations, session_date, region, signal_quality))
            else:
                # Tabla nueva solo con estado y ciudad
                cursor.execute('''
                    INSERT INTO reports (call_sign, operator_name, estado, ciudad, signal_report, zona, sistema,
                                       observations, session_date, region, signal_quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (call_sign.upper(), operator_name, estado, ciudad.title(), signal_report, zona, sistema,
                      observations, session_date, region, signal_quality))
        except sqlite3.OperationalError as e:
            if any(col in str(e) for col in ["no column named zona", "no column named sistema", "no column named estado", "no column named ciudad"]):
                # Forzar migración y reintentar
                self._migrate_database(cursor)
                # Reintentar con la estructura correcta después de migración
                cursor.execute("PRAGMA table_info(reports)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'qth' in columns and 'ciudad' in columns:
                    cursor.execute('''
                        INSERT INTO reports (call_sign, operator_name, qth, estado, ciudad, signal_report, zona, sistema,
                                           observations, session_date, region, signal_quality)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (call_sign.upper(), operator_name, ciudad.title(), estado, ciudad.title(), signal_report, zona, sistema,
                          observations, session_date, region, signal_quality))
                else:
                    cursor.execute('''
                        INSERT INTO reports (call_sign, operator_name, estado, ciudad, signal_report, zona, sistema,
                                           observations, session_date, region, signal_quality)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (call_sign.upper(), operator_name, estado, ciudad.title(), signal_report, zona, sistema,
                          observations, session_date, region, signal_quality))
            else:
                raise e
        
        # Actualizar historial de estaciones
        # Verificar si la tabla station_history tiene columna qth
        cursor.execute("PRAGMA table_info(station_history)")
        history_columns = [column[1] for column in cursor.fetchall()]
        
        # Siempre insertar con todas las columnas para máxima compatibilidad
        cursor.execute('''
            INSERT OR REPLACE INTO station_history 
            (call_sign, operator_name, qth, estado, ciudad, zona, sistema, last_used, use_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT use_count FROM station_history WHERE call_sign = ? AND operator_name = ?), 0) + 1)
        ''', (call_sign.upper(), operator_name, ciudad.title(), estado, ciudad.title(), zona, sistema, call_sign.upper(), operator_name))
        
        # Actualizar contador de sesión
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (session_date, total_participants)
            VALUES (?, (
                SELECT COUNT(DISTINCT call_sign) 
                FROM reports 
                WHERE session_date = ?
            ))
        ''', (session_date, session_date))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def _get_mexican_states(self):
        """Retorna diccionario de estados mexicanos"""
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
    
    def _convert_signal_to_quality(self, signal_report):
        """Convierte el reporte de señal a calidad numérica"""
        signal_lower = signal_report.lower()
        if any(word in signal_lower for word in ['buena', 'excelente', 'fuerte', '5']):
            return 3
        elif any(word in signal_lower for word in ['regular', 'media', '3', '4']):
            return 2
        else:
            return 1
    
    def get_all_reports(self, session_date=None):
        """Obtiene todos los reportes, opcionalmente filtrados por fecha"""
        conn = sqlite3.connect(self.db_path)
        
        if session_date:
            query = "SELECT * FROM reports WHERE session_date = ? ORDER BY timestamp DESC"
            df = pd.read_sql_query(query, conn, params=(session_date,))
        else:
            query = "SELECT * FROM reports ORDER BY timestamp DESC"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def update_report(self, report_id, **kwargs):
        """Actualiza un reporte existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [report_id]
        
        cursor.execute(f"UPDATE reports SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    def delete_report(self, report_id):
        """Elimina un reporte"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()
    
    def get_statistics(self, session_date=None):
        """Obtiene estadísticas de los reportes"""
        conn = sqlite3.connect(self.db_path)
        
        base_query = "FROM reports"
        where_clause = ""
        params = ()
        
        if session_date:
            where_clause = " WHERE session_date = ?"
            params = (session_date,)
        
        # Estadísticas generales
        stats = {}
        
        # Total de participantes únicos
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(DISTINCT call_sign) {base_query} {where_clause}", params)
        stats['total_participants'] = cursor.fetchone()[0]
        
        # Total de reportes
        cursor.execute(f"SELECT COUNT(*) {base_query} {where_clause}", params)
        stats['total_reports'] = cursor.fetchone()[0]
        
        # Participantes por región
        query = f"SELECT region, COUNT(DISTINCT call_sign) as count {base_query} {where_clause} GROUP BY region ORDER BY count DESC"
        stats['by_region'] = pd.read_sql_query(query, conn, params=params)
        
        # Ranking de estaciones más activas
        query = f"SELECT call_sign, operator_name, COUNT(*) as reports_count {base_query} {where_clause} GROUP BY call_sign ORDER BY reports_count DESC LIMIT 10"
        stats['most_active'] = pd.read_sql_query(query, conn, params=params)
        
        # Distribución de calidad de señal
        query = f"SELECT signal_quality, COUNT(*) as count {base_query} {where_clause} GROUP BY signal_quality"
        stats['signal_quality'] = pd.read_sql_query(query, conn, params=params)
        
        # Participantes por zona
        query = f"SELECT zona, COUNT(DISTINCT call_sign) as count {base_query} {where_clause} GROUP BY zona ORDER BY count DESC"
        stats['by_zona'] = pd.read_sql_query(query, conn, params=params)
        
        # Participantes por sistema
        query = f"SELECT sistema, COUNT(DISTINCT call_sign) as count {base_query} {where_clause} GROUP BY sistema ORDER BY count DESC"
        stats['by_sistema'] = pd.read_sql_query(query, conn, params=params)
        
        # Reportes por hora
        query = f"SELECT strftime('%H', timestamp) as hour, COUNT(*) as count {base_query} {where_clause} GROUP BY hour ORDER BY hour"
        stats['by_hour'] = pd.read_sql_query(query, conn, params=params)
        
        conn.close()
        return stats
    
    def search_reports(self, search_term, filters=None):
        """Busca reportes por indicativo, nombre o QTH con filtros opcionales"""
        conn = sqlite3.connect(self.db_path)
        
        # Query base
        where_conditions = []
        params = []
        
        # Búsqueda por término
        if search_term:
            where_conditions.append("(call_sign LIKE ? OR operator_name LIKE ? OR ciudad LIKE ? OR estado LIKE ?)")
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
        # Aplicar filtros adicionales
        if filters:
            if filters.get('session_date'):
                where_conditions.append("session_date = ?")
                params.append(filters['session_date'])
            
            if filters.get('zona') and filters['zona'] != 'Todas':
                where_conditions.append("zona = ?")
                params.append(filters['zona'])
            
            if filters.get('sistema') and filters['sistema'] != 'Todos':
                where_conditions.append("sistema = ?")
                params.append(filters['sistema'])
        
        # Construir query final
        query = "SELECT * FROM reports"
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        query += " ORDER BY timestamp DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        
        conn.close()
        return df
    
    def get_distinct_zones(self):
        """Obtiene las zonas únicas de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT zona FROM reports WHERE zona IS NOT NULL ORDER BY zona")
        zones = [row[0] for row in cursor.fetchall()]
        conn.close()
        return zones
    
    def get_distinct_systems(self):
        """Obtiene los sistemas únicos de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sistema FROM reports WHERE sistema IS NOT NULL ORDER BY sistema")
        systems = [row[0] for row in cursor.fetchall()]
        conn.close()
        return systems
    
    def get_motivational_stats(self):
        """Obtiene estadísticas motivacionales para competencia entre radioaficionados"""
        conn = sqlite3.connect(self.db_path)
        stats = {}
        
        # Estación más reportada del año
        current_year = datetime.now().year
        query = """
            SELECT call_sign, operator_name, COUNT(*) as total_reports
            FROM reports 
            WHERE strftime('%Y', session_date) = ?
            GROUP BY call_sign, operator_name
            ORDER BY total_reports DESC
            LIMIT 10
        """
        stats['top_stations_year'] = pd.read_sql_query(query, conn, params=(str(current_year),))
        
        # Estación más reportada del mes
        current_month = datetime.now().strftime('%Y-%m')
        query = """
            SELECT call_sign, operator_name, COUNT(*) as total_reports
            FROM reports 
            WHERE strftime('%Y-%m', session_date) = ?
            GROUP BY call_sign, operator_name
            ORDER BY total_reports DESC
            LIMIT 10
        """
        stats['top_stations_month'] = pd.read_sql_query(query, conn, params=(current_month,))
        
        # Zona más activa del año
        query = """
            SELECT zona, COUNT(DISTINCT call_sign) as unique_stations, COUNT(*) as total_reports
            FROM reports 
            WHERE strftime('%Y', session_date) = ?
            GROUP BY zona
            ORDER BY total_reports DESC
        """
        stats['top_zones_year'] = pd.read_sql_query(query, conn, params=(str(current_year),))
        
        # Zona más activa del mes
        query = """
            SELECT zona, COUNT(DISTINCT call_sign) as unique_stations, COUNT(*) as total_reports
            FROM reports 
            WHERE strftime('%Y-%m', session_date) = ?
            GROUP BY zona
            ORDER BY total_reports DESC
        """
        stats['top_zones_month'] = pd.read_sql_query(query, conn, params=(current_month,))
        
        # Sistema más usado del año
        query = """
            SELECT sistema, COUNT(DISTINCT call_sign) as unique_stations, COUNT(*) as total_reports
            FROM reports 
            WHERE strftime('%Y', session_date) = ?
            GROUP BY sistema
            ORDER BY total_reports DESC
        """
        stats['top_systems_year'] = pd.read_sql_query(query, conn, params=(str(current_year),))
        
        # Sistema más usado del mes
        query = """
            SELECT sistema, COUNT(DISTINCT call_sign) as unique_stations, COUNT(*) as total_reports
            FROM reports 
            WHERE strftime('%Y-%m', session_date) = ?
            GROUP BY sistema
            ORDER BY total_reports DESC
        """
        stats['top_systems_month'] = pd.read_sql_query(query, conn, params=(current_month,))
        
        # Estadísticas generales del año
        query = """
            SELECT 
                COUNT(*) as total_reports,
                COUNT(DISTINCT call_sign) as unique_stations,
                COUNT(DISTINCT session_date) as active_days
            FROM reports 
            WHERE strftime('%Y', session_date) = ?
        """
        stats['general_year'] = pd.read_sql_query(query, conn, params=(str(current_year),))
        
        # Estadísticas generales del mes
        query = """
            SELECT 
                COUNT(*) as total_reports,
                COUNT(DISTINCT call_sign) as unique_stations,
                COUNT(DISTINCT session_date) as active_days
            FROM reports 
            WHERE strftime('%Y-%m', session_date) = ?
        """
        stats['general_month'] = pd.read_sql_query(query, conn, params=(current_month,))
        
        conn.close()
        return stats
    
    def get_sessions(self):
        """Obtiene todas las sesiones registradas"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM sessions ORDER BY session_date DESC", conn)
        conn.close()
        return df
    
    def get_station_history(self, limit=20):
        """Obtiene el historial de estaciones ordenado por uso"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM station_history 
            ORDER BY use_count DESC, last_used DESC 
            LIMIT ?
        ''', conn, params=(limit,))
        conn.close()
        return df
    
    def clear_station_history(self):
        """Limpia todo el historial de estaciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM station_history")
        conn.commit()
        conn.close()
        return cursor.rowcount
    
    def create_user(self, username, password_hash, full_name, email=None, role='operator'):
        """Crea un nuevo usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, full_name, email, role))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def get_user(self, username):
        """Obtiene un usuario por nombre de usuario"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return dict(user)
        return None
    
    def get_all_users(self):
        """Obtiene todos los usuarios"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, email, created_at, last_login FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        conn.close()
        
        # Convertir a lista de diccionarios
        if users:
            return [dict(user) for user in users]
        return []
    
    def update_user(self, user_id, full_name=None, role=None, email=None):
        """Actualiza información de un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)
        if role:
            updates.append("role = ?")
            params.append(role)
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if updates:
            params.append(user_id)
            cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        
        conn.close()
        return cursor.rowcount > 0
    
    def delete_user(self, user_id):
        """Elimina un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def change_password(self, username, new_password_hash):
        """Cambia la contraseña de un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_password_hash, username))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def update_last_login(self, username):
        """Actualiza la última fecha de login del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?", (username,))
        conn.commit()
        conn.close()
