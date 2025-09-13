#!/usr/bin/env python3
"""
Script de debug para investigar el problema de filtrado en búsqueda
"""

import sqlite3
import pandas as pd
from datetime import datetime, date

def debug_search_issue():
    """Investiga por qué solo se muestran 6 registros en la búsqueda"""
    
    db_path = "fmre_reports.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 1. Verificar total de reportes en la base de datos
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_reports = cursor.fetchone()[0]
        print(f"📊 Total de reportes en la base de datos: {total_reports}")
        
        # 2. Verificar reportes de hoy
        today = date.today().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM reports WHERE session_date = ?", (today,))
        today_reports = cursor.fetchone()[0]
        print(f"📅 Reportes de hoy ({today}): {today_reports}")
        
        # 3. Verificar todas las fechas disponibles
        cursor.execute("SELECT DISTINCT session_date, COUNT(*) as count FROM reports GROUP BY session_date ORDER BY session_date DESC")
        dates = cursor.fetchall()
        print(f"\n📆 Fechas disponibles:")
        for date_str, count in dates:
            print(f"  - {date_str}: {count} reportes")
        
        # 4. Verificar zonas disponibles
        cursor.execute("SELECT DISTINCT zona, COUNT(*) as count FROM reports GROUP BY zona ORDER BY count DESC")
        zones = cursor.fetchall()
        print(f"\n🌍 Zonas disponibles:")
        for zona, count in zones:
            print(f"  - {zona}: {count} reportes")
        
        # 5. Verificar sistemas disponibles
        cursor.execute("SELECT DISTINCT sistema, COUNT(*) as count FROM reports GROUP BY sistema ORDER BY count DESC")
        systems = cursor.fetchall()
        print(f"\n📡 Sistemas disponibles:")
        for sistema, count in systems:
            print(f"  - {sistema}: {count} reportes")
        
        # 6. Simular la búsqueda problemática (fecha específica, todas las zonas, todos los sistemas)
        print(f"\n🔍 Simulando búsqueda con filtros:")
        
        # Probar con la fecha de hoy
        filters = {'session_date': today}
        where_conditions = []
        params = []
        
        if filters.get('session_date'):
            where_conditions.append("session_date = ?")
            params.append(filters['session_date'])
        
        query = "SELECT * FROM reports"
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        query += " ORDER BY timestamp DESC"
        
        print(f"Query ejecutada: {query}")
        print(f"Parámetros: {params}")
        
        df = pd.read_sql_query(query, conn, params=params)
        print(f"Resultados obtenidos: {len(df)} reportes")
        
        if len(df) > 0:
            print(f"\n📋 Primeros 10 resultados:")
            for idx, row in df.head(10).iterrows():
                print(f"  - {row['call_sign']} ({row['operator_name']}) - {row['session_date']}")
        
        # 7. Verificar si hay algún problema con la estructura de la tabla
        cursor.execute("PRAGMA table_info(reports)")
        columns = cursor.fetchall()
        print(f"\n🏗️ Estructura de la tabla 'reports':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error durante el debug: {str(e)}")

if __name__ == "__main__":
    debug_search_issue()
