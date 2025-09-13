#!/usr/bin/env python3
"""
Test simple de la función update_report sin pandas
"""

import sqlite3

def test_direct_db():
    print("=== TEST DIRECTO DE BASE DE DATOS ===")
    
    # Conectar directamente a la DB
    conn = sqlite3.connect("fmre_reports.db")
    cursor = conn.cursor()
    
    # Ver qué reportes hay
    cursor.execute("SELECT id, call_sign, operator_name FROM reports LIMIT 5")
    reports = cursor.fetchall()
    
    print(f"Reportes encontrados: {len(reports)}")
    for report in reports:
        print(f"ID: {report[0]}, Call: {report[1]}, Operador: {report[2]}")
    
    if reports:
        # Tomar el primer reporte
        report_id = reports[0][0]
        original_call = reports[0][1]
        
        print(f"\n--- PROBANDO UPDATE DIRECTO ---")
        print(f"ID: {report_id}, Call original: {original_call}")
        
        # Intentar update directo
        new_call = "TESTXXX"
        cursor.execute("UPDATE reports SET call_sign = ? WHERE id = ?", (new_call, report_id))
        rows_affected = cursor.rowcount
        print(f"Rows affected: {rows_affected}")
        
        conn.commit()
        
        # Verificar
        cursor.execute("SELECT call_sign FROM reports WHERE id = ?", (report_id,))
        result = cursor.fetchone()
        current_call = result[0] if result else "NO ENCONTRADO"
        
        print(f"Call después del update: {current_call}")
        
        if current_call == new_call:
            print("✅ UPDATE DIRECTO FUNCIONA")
        else:
            print("❌ UPDATE DIRECTO FALLÓ")
        
        # Restaurar
        cursor.execute("UPDATE reports SET call_sign = ? WHERE id = ?", (original_call, report_id))
        conn.commit()
        print(f"Restaurado a: {original_call}")
    
    conn.close()

if __name__ == "__main__":
    test_direct_db()
