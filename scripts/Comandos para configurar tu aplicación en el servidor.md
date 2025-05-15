¡Perfecto! 🚀  
Ahora preparamos **los comandos básicos de despliegue** para que puedas levantar todo tu proyecto de forma rápida en producción.

---

### 🛠 Comandos para configurar tu aplicación en el servidor

**(Todo esto estando conectado vía SSH a tu servidor)**

---

1. **Ir al directorio de tu proyecto**:

```bash
cd /var/www/vhosts/edefrutos2025.xyz/httpdocs
```

---

2. **(Opcional)** Crear entorno virtual (si no existe):

```bash
python3 -m venv .venv
```

---

3. **Activar el entorno virtual**:

```bash
source .venv/bin/activate
```

---

4. **Actualizar pip** (importante para evitar errores):

```bash
pip install --upgrade pip
```

---

5. **Instalar dependencias** (asegúrate de tener actualizado `requirements.txt`):

```bash
pip install -r requirements.txt
```

---

6. **Crear archivo `.env` si no existe**:

```bash
cp .env.example .env
nano .env
# Rellenas tus variables reales (MongoDB, correo, AWS S3, etc.)
```

---

7. **Configurar Gunicorn manualmente** (si es para test):

```bash
gunicorn --workers 4 --bind 127.0.0.1:8000 run:app
```

*(Asegúrate de que `run.py` esté bien preparado, como vimos.)*

---

8. **Crear servicio systemd para Gunicorn** (esto es para producción):

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Contenido recomendado para `gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for edefrutos2025.xyz
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vhosts/edefrutos2025.xyz/httpdocs
Environment="PATH=/var/www/vhosts/edefrutos2025.xyz/httpdocs/.venv/bin"
ExecStart=/var/www/vhosts/edefrutos2025.xyz/httpdocs/.venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

9. **Recargar systemd y arrancar Gunicorn**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

---

10. **Configurar Apache como proxy** (puedes tener ya un `.conf` en Plesk o configurarlo a mano):

```apache
<VirtualHost *:443>
    ServerName edefrutos2025.xyz
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # Configuración SSL (vamos a suponer que tienes certificado SSL con Let's Encrypt o similar)
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/edefrutos2025.xyz/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/edefrutos2025.xyz/privkey.pem

    ErrorLog ${APACHE_LOG_DIR}/edefrutos2025_error.log
    CustomLog ${APACHE_LOG_DIR}/edefrutos2025_access.log combined
</VirtualHost>
```

---

### 📋 Resumen de carpetas que deben existir

```bash
mkdir -p spreadsheets imagenes_subidas instance
chmod -R 755 spreadsheets imagenes_subidas
```

---

### 🔥 Y tu aplicación Flask quedará corriendo en producción 🔥

---

¿Te preparo ahora también una **versión especial del `requirements.txt` limpia** para producción (sin paquetes de desarrollo)?  
Así dejamos todo profesionalmente limpio. 🚀

¿Seguimos? ✅