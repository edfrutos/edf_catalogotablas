"""
Módulo de excepciones personalizadas para la aplicación edf_catalogotablas.
Este módulo define las excepciones específicas utilizadas en toda la aplicación.
"""


class DatabaseConnectionError(Exception):
    """Se lanza cuando hay problemas de conexión con la base de datos MongoDB."""
    pass


class AuthenticationError(Exception):
    """Se lanza cuando hay problemas en la autenticación de usuarios."""
    pass


class FileUploadError(Exception):
    """Se lanza cuando hay problemas al subir archivos."""
    pass


class ResourceNotFoundError(Exception):
    """Se lanza cuando no se encuentra un recurso solicitado."""
    pass


class InvalidConfigurationError(Exception):
    """Se lanza cuando hay problemas de configuración de la aplicación."""
    pass


class APIError(Exception):
    """Clase base para errores relacionados con la API."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
