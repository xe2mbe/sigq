#!/usr/bin/env python3
"""
Script para resetear contraseña de usuario vía línea de comandos
Uso: python reset_password.py <username> <nueva_contraseña>
"""

import sys
import hashlib
import sqlite3
import os

def hash_password(password):
    """Genera hash SHA256 de la contraseña (mismo método que auth.py)"""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_user_password(username, new_password, db_path="fmre_reports.db"):
    """Resetea la contraseña de un usuario"""
    if not os.path.exists(db_path):
        print(f"❌ Error: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar que el usuario existe
        cursor.execute("SELECT id, username, full_name FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Error: Usuario '{username}' no encontrado")
            conn.close()
            return False
        
        # Generar nuevo hash
        password_hash = hash_password(new_password)
        
        # Actualizar contraseña
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Contraseña actualizada exitosamente para usuario '{username}' ({user[2]})")
            print(f"🔑 Nueva contraseña: {new_password}")
            conn.close()
            return True
        else:
            print(f"❌ Error: No se pudo actualizar la contraseña")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error de base de datos: {str(e)}")
        return False

def list_users(db_path="fmre_reports.db"):
    """Lista todos los usuarios"""
    if not os.path.exists(db_path):
        print(f"❌ Error: Base de datos no encontrada en {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, full_name, role FROM users ORDER BY username")
        users = cursor.fetchall()
        
        if users:
            print("\n👥 Usuarios disponibles:")
            print("-" * 50)
            for username, full_name, role in users:
                print(f"• {username} - {full_name} ({role})")
        else:
            print("❌ No se encontraron usuarios")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error de base de datos: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("🔧 Script de Reset de Contraseña - SIGQ")
        print("=" * 40)
        print("Uso:")
        print("  python reset_password.py <username> <nueva_contraseña>")
        print("  python reset_password.py --list")
        print("\nEjemplos:")
        print("  python reset_password.py admin admin123")
        print("  python reset_password.py --list")
        return
    
    if sys.argv[1] == "--list":
        list_users()
        return
    
    if len(sys.argv) != 3:
        print("❌ Error: Se requieren exactamente 2 argumentos: <username> <nueva_contraseña>")
        return
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    if len(new_password) < 6:
        print("❌ Error: La contraseña debe tener al menos 6 caracteres")
        return
    
    print(f"🔄 Reseteando contraseña para usuario: {username}")
    success = reset_user_password(username, new_password)
    
    if success:
        print("\n✅ ¡Contraseña reseteada exitosamente!")
        print("🚀 Ya puedes iniciar sesión en SIGQ con la nueva contraseña")
    else:
        print("\n❌ No se pudo resetear la contraseña")

if __name__ == "__main__":
    main()
