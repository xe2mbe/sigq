#!/usr/bin/env python3
"""
Script de prueba para verificar si update_report funciona correctamente
"""

from database import FMREDatabase

def test_update_report():
    print("=== PRUEBA DE UPDATE_REPORT ===")
    
    # Inicializar base de datos
    db = FMREDatabase()
    
    # Obtener todos los reportes para ver qué hay
    reports = db.get_all_reports()
    print(f"Total de reportes en DB: {len(reports)}")
    
    if len(reports) > 0:
        # Tomar el primer reporte
        first_report = reports.iloc[0]
        report_id = first_report['id']
        original_call_sign = first_report['call_sign']
        
        print(f"\n--- REPORTE ORIGINAL ---")
        print(f"ID: {report_id}")
        print(f"Call Sign: {original_call_sign}")
        print(f"Operator: {first_report['operator_name']}")
        print(f"QTH: {first_report['qth']}")
        
        # Intentar actualizar el call_sign
        new_call_sign = "TEST123"
        print(f"\n--- INTENTANDO UPDATE ---")
        print(f"Cambiando call_sign de '{original_call_sign}' a '{new_call_sign}'")
        
        try:
            result = db.update_report(report_id, call_sign=new_call_sign)
            print(f"Resultado update_report: {result}")
            
            # Verificar si se actualizó
            updated_reports = db.get_all_reports()
            updated_report = updated_reports[updated_reports['id'] == report_id]
            
            if not updated_report.empty:
                current_call_sign = updated_report.iloc[0]['call_sign']
                print(f"\n--- VERIFICACIÓN ---")
                print(f"Call sign después del update: {current_call_sign}")
                
                if current_call_sign == new_call_sign:
                    print("✅ UPDATE FUNCIONÓ CORRECTAMENTE")
                else:
                    print("❌ UPDATE NO FUNCIONÓ - El valor no cambió")
            else:
                print("❌ ERROR - No se encontró el reporte después del update")
                
            # Restaurar valor original
            print(f"\n--- RESTAURANDO VALOR ORIGINAL ---")
            restore_result = db.update_report(report_id, call_sign=original_call_sign)
            print(f"Resultado restauración: {restore_result}")
            
        except Exception as e:
            print(f"❌ ERROR en update_report: {e}")
    
    else:
        print("❌ No hay reportes en la base de datos para probar")

if __name__ == "__main__":
    test_update_report()
