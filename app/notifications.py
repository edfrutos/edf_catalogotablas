"""
Sistema de notificaciones y alertas
Este módulo se encarga de enviar notificaciones y alertas cuando
se detectan problemas en el sistema o cuando se alcanzan umbrales críticos.
"""

import smtplib
import logging
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app, render_template_string

# Configuración del logger
logger = logging.getLogger(__name__)

# Cargar configuración de notificaciones (usando directorio seguro)
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(APP_ROOT, 'app_data')
os.makedirs(CONFIG_DIR, exist_ok=True)  # Crear directorio si no existe
CONFIG_FILE = os.path.join(CONFIG_DIR, 'edefrutos2025_notifications_config.json')
DEFAULT_CONFIG = {
    "enabled": False,
    "smtp": {
        "server": "smtp.gmail.com",
        "port": 587,
        "username": "",
        "password": "",
        "use_tls": True
    },
    "recipients": [],
    "thresholds": {
        "cpu": 85,
        "memory": 85,
        "disk": 85,
        "error_rate": 10
    },
    "cooldown_minutes": 60,  # Tiempo mínimo entre alertas del mismo tipo
    "last_alerts": {}
}

def load_config():
    """Carga la configuración de notificaciones desde el archivo de configuración"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Asegurar que la estructura es correcta combinando con los defaults
                result = DEFAULT_CONFIG.copy()
                result.update(config)
                return result
        except Exception as e:
            logger.error(f"Error al cargar configuración de notificaciones: {str(e)}")
    return DEFAULT_CONFIG

def save_config(config):
    """Guarda la configuración de notificaciones en el archivo de configuración"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error al guardar configuración de notificaciones: {str(e)}")
        return False

def send_email(subject, body_html, recipients=None):
    """
    Envía un correo electrónico con el asunto y cuerpo especificados.
    """
    config = load_config()
    
    if not config["enabled"] or not config["smtp"]["username"]:
        logger.warning("Las notificaciones por correo están desactivadas o mal configuradas")
        return False
    
    if not recipients:
        recipients = config["recipients"]
    
    if not recipients:
        logger.warning("No hay destinatarios configurados para las notificaciones")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[edefrutos2025] {subject}"
        msg['From'] = config["smtp"]["username"]
        msg['To'] = ", ".join(recipients)
        
        # Añadir cuerpo HTML
        msg.attach(MIMEText(body_html, 'html'))
        
        # Iniciar conexión SMTP
        with smtplib.SMTP(config["smtp"]["server"], config["smtp"]["port"]) as server:
            if config["smtp"]["use_tls"]:
                server.starttls()
            
            if config["smtp"]["username"] and config["smtp"]["password"]:
                server.login(config["smtp"]["username"], config["smtp"]["password"])
            
            server.send_message(msg)
        
        logger.info(f"Correo enviado correctamente a {len(recipients)} destinatarios")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo: {str(e)}")
        return False

def check_and_alert(metrics):
    """
    Verifica las métricas del sistema y envía alertas si es necesario.
    """
    config = load_config()
    if not config["enabled"]:
        return
    
    alerts = []
    current_time = datetime.now()
    
    # Verificar CPU
    if metrics["system_status"]["cpu_usage"] > config["thresholds"]["cpu"]:
        alert_key = "cpu"
        last_alert = config["last_alerts"].get(alert_key, "1970-01-01 00:00:00")
        last_alert_time = datetime.strptime(last_alert, "%Y-%m-%d %H:%M:%S")
        
        # Verificar si ha pasado suficiente tiempo desde la última alerta
        minutes_since_last = (current_time - last_alert_time).total_seconds() / 60
        if minutes_since_last > config["cooldown_minutes"]:
            alerts.append({
                "type": "CPU",
                "value": metrics["system_status"]["cpu_usage"],
                "threshold": config["thresholds"]["cpu"],
                "message": f"Uso de CPU elevado: {metrics['system_status']['cpu_usage']}% (umbral: {config['thresholds']['cpu']}%)"
            })
            config["last_alerts"][alert_key] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Verificar memoria
    if metrics["system_status"]["memory_usage"]["percent"] > config["thresholds"]["memory"]:
        alert_key = "memory"
        last_alert = config["last_alerts"].get(alert_key, "1970-01-01 00:00:00")
        last_alert_time = datetime.strptime(last_alert, "%Y-%m-%d %H:%M:%S")
        
        minutes_since_last = (current_time - last_alert_time).total_seconds() / 60
        if minutes_since_last > config["cooldown_minutes"]:
            alerts.append({
                "type": "Memoria",
                "value": metrics["system_status"]["memory_usage"]["percent"],
                "threshold": config["thresholds"]["memory"],
                "message": f"Uso de memoria elevado: {metrics['system_status']['memory_usage']['percent']}% (umbral: {config['thresholds']['memory']}%)"
            })
            config["last_alerts"][alert_key] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Verificar disco
    if metrics["system_status"]["disk_usage"]["percent"] > config["thresholds"]["disk"]:
        alert_key = "disk"
        last_alert = config["last_alerts"].get(alert_key, "1970-01-01 00:00:00")
        last_alert_time = datetime.strptime(last_alert, "%Y-%m-%d %H:%M:%S")
        
        minutes_since_last = (current_time - last_alert_time).total_seconds() / 60
        if minutes_since_last > config["cooldown_minutes"]:
            alerts.append({
                "type": "Disco",
                "value": metrics["system_status"]["disk_usage"]["percent"],
                "threshold": config["thresholds"]["disk"],
                "message": f"Espacio en disco bajo: {metrics['system_status']['disk_usage']['percent']}% usado (umbral: {config['thresholds']['disk']}%)"
            })
            config["last_alerts"][alert_key] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Verificar tasa de errores si hay suficientes solicitudes
    if metrics["request_stats"]["total_requests"] > 100:
        error_rate = (metrics["request_stats"]["error_count"] / metrics["request_stats"]["total_requests"]) * 100
        if error_rate > config["thresholds"]["error_rate"]:
            alert_key = "error_rate"
            last_alert = config["last_alerts"].get(alert_key, "1970-01-01 00:00:00")
            last_alert_time = datetime.strptime(last_alert, "%Y-%m-%d %H:%M:%S")
            
            minutes_since_last = (current_time - last_alert_time).total_seconds() / 60
            if minutes_since_last > config["cooldown_minutes"]:
                alerts.append({
                    "type": "Tasa de errores",
                    "value": error_rate,
                    "threshold": config["thresholds"]["error_rate"],
                    "message": f"Tasa de errores elevada: {error_rate:.2f}% ({metrics['request_stats']['error_count']} errores de {metrics['request_stats']['total_requests']} solicitudes)"
                })
                config["last_alerts"][alert_key] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Verificar estado de la base de datos
    if not metrics["database_status"]["is_available"]:
        alert_key = "database"
        last_alert = config["last_alerts"].get(alert_key, "1970-01-01 00:00:00")
        last_alert_time = datetime.strptime(last_alert, "%Y-%m-%d %H:%M:%S")
        
        minutes_since_last = (current_time - last_alert_time).total_seconds() / 60
        if minutes_since_last > config["cooldown_minutes"]:
            alerts.append({
                "type": "Base de datos",
                "value": "No disponible",
                "threshold": "N/A",
                "message": f"La base de datos no está disponible. Error: {metrics['database_status']['error']}"
            })
            config["last_alerts"][alert_key] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Si hay alertas, enviar correo
    if alerts:
        save_config(config)  # Guardar las últimas alertas
        
        # Generar HTML para el correo
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .alert { margin-bottom: 15px; padding: 10px; border-radius: 5px; }
                .critical { background-color: #ffdddd; border-left: 5px solid #f44336; }
                .warning { background-color: #ffffcc; border-left: 5px solid #ffeb3b; }
                h2 { color: #333; }
                table { border-collapse: collapse; width: 100%; }
                th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .footer { margin-top: 20px; font-size: 12px; color: #777; }
            </style>
        </head>
        <body>
            <h2>Alerta del sistema edefrutos2025</h2>
            <p>Se han detectado las siguientes alertas en el sistema:</p>
            
            <table>
                <tr>
                    <th>Tipo</th>
                    <th>Valor</th>
                    <th>Umbral</th>
                    <th>Mensaje</th>
                </tr>
                {% for alert in alerts %}
                <tr>
                    <td><strong>{{ alert.type }}</strong></td>
                    <td>{{ alert.value }}%</td>
                    <td>{{ alert.threshold }}%</td>
                    <td>{{ alert.message }}</td>
                </tr>
                {% endfor %}
            </table>
            
            <h3>Detalles del sistema</h3>
            <ul>
                <li><strong>CPU:</strong> {{ metrics.system_status.cpu_usage }}%</li>
                <li><strong>Memoria:</strong> {{ metrics.system_status.memory_usage.used_mb }} MB de {{ metrics.system_status.memory_usage.total_mb }} MB ({{ metrics.system_status.memory_usage.percent }}%)</li>
                <li><strong>Disco:</strong> {{ metrics.system_status.disk_usage.used_gb }} GB de {{ metrics.system_status.disk_usage.total_gb }} GB ({{ metrics.system_status.disk_usage.percent }}%)</li>
                <li><strong>Base de datos:</strong> {% if metrics.database_status.is_available %}Disponible ({{ metrics.database_status.response_time_ms }} ms){% else %}No disponible{% endif %}</li>
                <li><strong>Solicitudes totales:</strong> {{ metrics.request_stats.total_requests }}</li>
                <li><strong>Errores:</strong> {{ metrics.request_stats.error_count }}</li>
            </ul>
            
            <div class="footer">
                <p>Este es un mensaje automático del sistema de monitoreo. Por favor, no responda a este correo.</p>
                <p>Fecha y hora: {{ timestamp }}</p>
            </div>
        </body>
        </html>
        """
        
        # Renderizar la plantilla
        html_content = render_template_string(
            html_template, 
            alerts=alerts, 
            metrics=metrics, 
            timestamp=current_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Enviar correo
        subject = f"ALERTA: {len(alerts)} problema(s) detectado(s) en edefrutos2025"
        send_email(subject, html_content)
        
        logger.info(f"Se han enviado {len(alerts)} alertas por correo")
        return True
    
    return False

def update_settings(enabled=None, smtp_settings=None, recipients=None, thresholds=None, cooldown=None):
    """
    Actualiza la configuración de notificaciones.
    """
    config = load_config()
    
    if enabled is not None:
        config["enabled"] = enabled
    
    if smtp_settings:
        config["smtp"].update(smtp_settings)
    
    if recipients:
        config["recipients"] = recipients
    
    if thresholds:
        config["thresholds"].update(thresholds)
    
    if cooldown:
        config["cooldown_minutes"] = cooldown
    
    return save_config(config)

def get_settings():
    """
    Obtiene la configuración actual de notificaciones.
    """
    return load_config()

def send_test_email(recipient):
    """
    Envía un correo de prueba para verificar la configuración.
    """
    subject = "Prueba de notificación de edefrutos2025"
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .content { padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            h2 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <div class="content">
            <h2>¡Configuración de notificaciones correcta!</h2>
            <p>Este es un correo de prueba del sistema de monitoreo de edefrutos2025.</p>
            <p>Si estás recibiendo este correo, la configuración de notificaciones es correcta.</p>
            <p>Fecha y hora: {}</p>
        </div>
    </body>
    </html>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return send_email(subject, html_content, [recipient])

# Función para inicializar el módulo
def init_app(app):
    """
    Inicializa el sistema de notificaciones
    """
    # Cargar configuración o crear por defecto
    config = load_config()
    save_config(config)
    
    logger.info("Sistema de notificaciones inicializado")
    return True
