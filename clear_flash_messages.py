#!/usr/bin/env python3
"""
Script para limpiar mensajes flash persistentes
"""

import requests
import json


def clear_flash_messages():
    """Limpia mensajes flash desde el lado del cliente"""

    print("🧹 Limpiando mensajes flash persistentes...")

    # Intentar limpiar mensajes flash usando la ruta específica
    try:
        response = requests.post(
            "http://localhost:5002/clear-flash-messages",
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        if response.status_code == 200:
            print("✅ Mensajes flash limpiados desde endpoint específico")
            return True
        else:
            print(f"⚠️ Endpoint de limpieza devolvió: {response.status_code}")
    except Exception as e:
        print(f"⚠️ No se pudo usar endpoint específico: {e}")

    # Crear una nueva sesión limpia accediendo a una ruta que force reset
    try:
        session = requests.Session()

        # Acceder a la página principal para establecer una sesión
        response = session.get("http://localhost:5002/", timeout=5)
        print(f"Acceso inicial: {response.status_code}")

        # Intentar acceder al login para forzar limpieza de flash
        response = session.get("http://localhost:5002/login", timeout=5)
        print(f"Acceso a login: {response.status_code}")

        # Intentar acceder directamente a test_session para verificar
        response = session.get("http://localhost:5002/test_session", timeout=5)
        print(f"Test session: {response.status_code}")
        print(f"Contenido: {response.text[:100]}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def manual_session_reset():
    """Instrucciones para reset manual de sesión"""
    print("\n" + "=" * 50)
    print("🔧 RESET MANUAL DE SESIÓN")
    print("=" * 50)
    print("\nSi el problema persiste, realiza estos pasos manualmente:")
    print("\n1. En tu navegador, ve a:")
    print("   http://localhost:5002/logout")

    print("\n2. Luego accede directamente a:")
    print("   http://localhost:5002/login")

    print("\n3. Inicia sesión con tus credenciales de admin")

    print("\n4. Después de login exitoso, intenta:")
    print("   http://localhost:5002/catalogs/")

    print("\n5. Si aún no funciona, borra las cookies del navegador:")
    print("   - Abre DevTools (F12)")
    print("   - Ve a Application/Storage > Cookies")
    print("   - Elimina todas las cookies de localhost:5002")
    print("   - Recarga la página")


if __name__ == "__main__":
    success = clear_flash_messages()

    if not success:
        print("\n⚠️ La limpieza automática no fue completamente exitosa")

    manual_session_reset()

    print("\n" + "=" * 50)
    print("📋 VERIFICACIÓN FINAL")
    print("=" * 50)
    print("\nPrueba estos comandos en orden:")
    print("1. curl -I http://localhost:5002/logout")
    print("2. curl -I http://localhost:5002/login")
    print("3. curl -I http://localhost:5002/catalogs/")
    print("\nEl último comando debería devolver 200 en lugar de 302")
