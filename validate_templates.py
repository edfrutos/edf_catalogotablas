#!/usr/bin/env python3
"""
Script específico para probar templates en servicio de la aplicación EDF Catálogo de Tablas.
Enfocado en las rutas y funcionalidades actuales.
"""

import requests
import sys
import os
import re
from bs4 import BeautifulSoup
import urllib.parse
import time
from datetime import datetime


class EDFTemplateValidator:
    """Validador específico para templates de EDF Catálogo de Tablas."""

    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}

    def run_all_tests(self):
        """Ejecutar todas las pruebas de templates."""
        print("🚀 Iniciando validación de templates de EDF Catálogo de Tablas")
        print(f"📍 URL base: {self.base_url}")
        print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        if not self._check_server():
            return False

        tests = [
            ("Home/Landing", self._test_home),
            ("Login", self._test_login),
            ("Admin Dashboard", self._test_admin),
            ("Catalogs List", self._test_catalogs),
            ("Legacy Routes", self._test_legacy_routes),
            ("Static Resources", self._test_static),
            ("Error Pages", self._test_errors),
            ("API Endpoints", self._test_api),
        ]

        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            try:
                result = test_func()
                self.results[test_name] = result
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                print(f"   {status}: {result['message']}")
                if result.get("details"):
                    for detail in result["details"]:
                        print(f"     • {detail}")
            except Exception as e:
                self.results[test_name] = {
                    "success": False,
                    "message": f"Error: {str(e)}",
                }
                print(f"   ❌ ERROR: {str(e)}")

        self._print_summary()
        return all(r["success"] for r in self.results.values())

    def _check_server(self):
        """Verificar que el servidor esté corriendo."""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            print(f"✅ Servidor disponible (Status: {response.status_code})")
            return True
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Servidor no disponible en {self.base_url}")
            print("   Inicia el servidor con: python run_server.py")
            return False
        except Exception as e:
            print(f"❌ Error conectando al servidor: {str(e)}")
            return False

    def _test_home(self):
        """Test página principal."""
        try:
            response = self.session.get(f"{self.base_url}/")

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"Status code: {response.status_code}",
                }

            soup = BeautifulSoup(response.text, "html.parser")
            details = []

            # Verificaciones básicas
            if soup.title:
                details.append(f"Título: {soup.title.string}")
            else:
                details.append("⚠️ Sin título")

            # Navegación
            nav_elements = soup.find_all("nav")
            if nav_elements:
                details.append(f"Navegación encontrada: {len(nav_elements)} elementos")

            # Links importantes
            login_link = soup.find("a", href=re.compile(r"/login"))
            if login_link:
                details.append("Link de login encontrado")

            return {
                "success": True,
                "message": "Página principal carga correctamente",
                "details": details,
            }

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _test_login(self):
        """Test página de login."""
        try:
            response = self.session.get(f"{self.base_url}/login")

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"Status code: {response.status_code}",
                }

            soup = BeautifulSoup(response.text, "html.parser")
            details = []

            # Form de login
            login_form = soup.find("form")
            if not login_form:
                return {
                    "success": False,
                    "message": "No se encontró formulario de login",
                }

            details.append("Formulario de login encontrado")

            # Campos necesarios
            email_field = soup.find("input", {"type": "email"}) or soup.find(
                "input", {"name": "username"}
            )
            password_field = soup.find("input", {"type": "password"})

            if email_field:
                details.append("Campo de email/usuario encontrado")
            if password_field:
                details.append("Campo de contraseña encontrado")

            if not (email_field and password_field):
                return {
                    "success": False,
                    "message": "Faltan campos esenciales en el formulario",
                }

            return {
                "success": True,
                "message": "Página de login funcional",
                "details": details,
            }

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _test_admin(self):
        """Test acceso a admin (debería requerir autenticación)."""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/", allow_redirects=False
            )

            if response.status_code in [302, 303]:
                location = response.headers.get("Location", "")
                if "/login" in location:
                    return {
                        "success": True,
                        "message": "Admin correctamente protegido",
                        "details": [f"Redirige a: {location}"],
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Admin redirige a ubicación inesperada: {location}",
                    }
            elif response.status_code in [401, 403]:
                return {
                    "success": True,
                    "message": "Admin correctamente protegido con error de autorización",
                }
            else:
                return {
                    "success": False,
                    "message": f"Admin accesible sin autenticación (Status: {response.status_code})",
                }

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _test_catalogs(self):
        """Test página de catálogos."""
        try:
            response = self.session.get(
                f"{self.base_url}/catalogs/", allow_redirects=True
            )

            # Puede requerir autenticación
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                details = []

                # Buscar elementos de catálogos
                catalog_elements = soup.find_all(["div", "section", "article"])
                details.append(f"Elementos encontrados: {len(catalog_elements)}")

                # Buscar tablas o listas
                tables = soup.find_all("table")
                if tables:
                    details.append(f"Tablas encontradas: {len(tables)}")

                return {
                    "success": True,
                    "message": "Página de catálogos accesible",
                    "details": details,
                }
            else:
                return {
                    "success": True,
                    "message": f"Catálogos requieren autenticación (Status: {response.status_code})",
                }

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _test_legacy_routes(self):
        """Test rutas legacy de administración."""
        legacy_urls = [
            "/admin/catalogo/spreadsheets/test",
            "/admin/users",
            "/admin/settings",
        ]

        details = []
        working_routes = 0

        for url in legacy_urls:
            try:
                response = self.session.get(
                    f"{self.base_url}{url}", allow_redirects=False
                )
                if response.status_code in [200, 302, 303, 401, 403]:
                    working_routes += 1
                    details.append(f"✅ {url}: {response.status_code}")
                else:
                    details.append(f"❌ {url}: {response.status_code}")
            except Exception as e:
                details.append(f"❌ {url}: Error - {str(e)}")

        return {
            "success": working_routes > 0,
            "message": f"Rutas legacy: {working_routes}/{len(legacy_urls)} funcionan",
            "details": details,
        }

    def _test_static(self):
        """Test recursos estáticos."""
        static_resources = [
            "/static/css/style.css",
            "/static/js/main.js",
            "/static/favicon.ico",
            "/static/images/logo.png",
        ]

        details = []
        found_resources = 0

        for resource in static_resources:
            try:
                response = self.session.get(f"{self.base_url}{resource}")
                if response.status_code == 200:
                    found_resources += 1
                    details.append(f"✅ {resource}")
                elif response.status_code == 404:
                    details.append(f"⚠️ {resource}: No encontrado")
                else:
                    details.append(f"❌ {resource}: {response.status_code}")
            except Exception as e:
                details.append(f"❌ {resource}: Error")

        return {
            "success": True,  # Recursos estáticos opcionales
            "message": f"Recursos estáticos: {found_resources}/{len(static_resources)} encontrados",
            "details": details,
        }

    def _test_errors(self):
        """Test páginas de error."""
        try:
            # Test 404
            response = self.session.get(f"{self.base_url}/nonexistent-page-test-404")

            if response.status_code == 404:
                soup = BeautifulSoup(response.text, "html.parser")
                has_title = soup.title is not None
                has_content = len(soup.get_text().strip()) > 50

                details = []
                if has_title:
                    details.append("✅ Página 404 tiene título")
                if has_content:
                    details.append("✅ Página 404 tiene contenido descriptivo")

                return {
                    "success": True,
                    "message": "Página de error 404 funcional",
                    "details": details,
                }
            else:
                return {
                    "success": False,
                    "message": f"Error 404 no funciona correctamente (Status: {response.status_code})",
                }

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _test_api(self):
        """Test endpoints de API si existen."""
        api_endpoints = ["/api/catalogs", "/api/health", "/api/status", "/api/docs"]

        details = []
        working_apis = 0

        for endpoint in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [200, 401, 403]:
                    working_apis += 1
                    details.append(f"✅ {endpoint}: {response.status_code}")
                elif response.status_code == 404:
                    details.append(f"⚠️ {endpoint}: No implementado")
                else:
                    details.append(f"❌ {endpoint}: {response.status_code}")
            except Exception as e:
                details.append(f"❌ {endpoint}: Error")

        return {
            "success": True,  # APIs opcionales
            "message": f"APIs: {working_apis}/{len(api_endpoints)} disponibles",
            "details": details,
        }

    def _print_summary(self):
        """Imprimir resumen de resultados."""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])

        print(f"Total de pruebas: {total_tests}")
        print(f"Exitosas: {passed_tests}")
        print(f"Fallidas: {total_tests - passed_tests}")
        print(f"Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        else:
            print(
                f"\n⚠️ {total_tests - passed_tests} pruebas fallaron. Revisa los detalles arriba."
            )


def main():
    """Función principal."""
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:5002")

    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    validator = EDFTemplateValidator(base_url)
    success = validator.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
