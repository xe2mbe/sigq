# Guía de Despliegue en Linux con HTTPS (Apache)

Esta guía te ayudará a desplegar tu aplicación SIGQ Streamlit en un servidor Linux que ya tiene Apache ejecutándose (compatible con AllStar Link dashboards como allmon3 y allscan).

## Requisitos Previos

- Servidor Linux (Ubuntu/Debian recomendado) con Apache ya instalado
- Dominio apuntando a tu servidor
- Acceso root o sudo
- Puerto 80 y 443 abiertos en el firewall
- Apache ejecutándose con tus dashboards AllStar Link existentes

## Pasos de Instalación

### 1. Preparar el Servidor

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias (sin nginx ya que usamos Apache)
sudo apt install -y python3 python3-pip python3-venv certbot python3-certbot-apache ufw git

# Habilitar módulos de Apache necesarios
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod headers
```

### 2. Configurar la Aplicación

```bash
# Crear directorio de la aplicación
sudo mkdir -p /var/www/sigq
sudo chown www-data:www-data /var/www/sigq

# Subir archivos de la aplicación al servidor
# Puedes usar scp, rsync, git clone, etc.
# Ejemplo con scp:
# scp -r /ruta/local/sigq/* usuario@servidor:/var/www/sigq/

# Crear entorno virtual
cd /var/www/sigq
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install --upgrade pip

# Instalar dependencias
sudo -u www-data ./venv/bin/pip install streamlit pandas openpyxl reportlab Pillow pytz bcrypt plotly
```

### 3. Configurar Streamlit

```bash
# Crear directorio de configuración
sudo -u www-data mkdir -p /var/www/sigq/.streamlit

# Crear archivo de configuración
sudo tee /var/www/sigq/.streamlit/config.toml << EOF
[server]
port = 8501
address = "127.0.0.1"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
base = "light"
EOF

sudo chown -R www-data:www-data /var/www/sigq/.streamlit
```

### 4. Crear Servicio Systemd

```bash
# Crear archivo de servicio
sudo tee /etc/systemd/system/sigq-streamlit.service << EOF
[Unit]
Description=SIGQ Streamlit Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/sigq
Environment=PATH=/var/www/sigq/venv/bin
ExecStart=/var/www/sigq/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar y iniciar el servicio
sudo systemctl daemon-reload
sudo systemctl enable sigq-streamlit
sudo systemctl start sigq-streamlit

# Verificar estado
sudo systemctl status sigq-streamlit
```

### 5. Configurar Apache Virtual Host

```bash
# Crear configuración de Apache (REEMPLAZA tu-dominio.com con tu dominio real)
sudo tee /etc/apache2/sites-available/sigq.conf << EOF
<VirtualHost *:80>
    ServerName tu-dominio.com
    ServerAlias www.tu-dominio.com
    
    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]
</VirtualHost>

<VirtualHost *:443>
    ServerName tu-dominio.com
    ServerAlias www.tu-dominio.com
    
    # SSL Configuration (will be added by certbot)
    SSLEngine on
    
    # Security Headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    
    # Proxy settings for Streamlit
    ProxyPreserveHost On
    ProxyRequests Off
    
    # Main application proxy
    ProxyPass / http://127.0.0.1:8501/
    ProxyPassReverse / http://127.0.0.1:8501/
    
    # WebSocket support for Streamlit
    ProxyPass /_stcore/stream ws://127.0.0.1:8501/_stcore/stream
    ProxyPassReverse /_stcore/stream ws://127.0.0.1:8501/_stcore/stream
    
    # Handle WebSocket upgrade
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://127.0.0.1:8501/\$1" [P,L]
    
    # Logging
    ErrorLog \${APACHE_LOG_DIR}/sigq_error.log
    CustomLog \${APACHE_LOG_DIR}/sigq_access.log combined
    
    # File upload size limit
    LimitRequestBody 52428800
</VirtualHost>
EOF

# Habilitar el sitio (NO deshabilitar default para preservar AllStar dashboards)
sudo a2ensite sigq.conf

# Verificar configuración
sudo apache2ctl configtest

# Recargar Apache
sudo systemctl reload apache2
```

### 6. Configurar Firewall

```bash
# Habilitar UFW
sudo ufw --force enable

# Permitir SSH, HTTP y HTTPS
sudo ufw allow ssh
sudo ufw allow 'Apache Full'

# Verificar estado
sudo ufw status
```

### 7. Instalar Certificado SSL con Certbot

```bash
# Instalar certificado SSL (REEMPLAZA tu-dominio.com con tu dominio real)
sudo certbot --apache -d tu-dominio.com -d www.tu-dominio.com

# Configurar renovación automática
sudo crontab -e
# Agregar esta línea:
# 0 12 * * * /usr/bin/certbot renew --quiet

# Verificar renovación automática
sudo certbot renew --dry-run
```

## Verificación del Despliegue

1. **Verificar que Streamlit está ejecutándose:**
   ```bash
   sudo systemctl status sigq-streamlit
   curl http://localhost:8501
   ```

2. **Verificar Apache:**
   ```bash
   sudo systemctl status apache2
   sudo apache2ctl configtest
   ```

3. **Verificar SSL:**
   ```bash
   sudo certbot certificates
   ```

4. **Probar la aplicación:**
   - HTTP: `http://tu-dominio.com`
   - HTTPS: `https://tu-dominio.com`

## Comandos Útiles de Mantenimiento

```bash
# Ver logs de la aplicación
sudo journalctl -u sigq-streamlit -f

# Reiniciar la aplicación
sudo systemctl restart sigq-streamlit

# Reiniciar Apache
sudo systemctl reload apache2

# Renovar certificado SSL manualmente
sudo certbot renew

# Ver estado de todos los servicios
sudo systemctl status sigq-streamlit apache2
```

## Solución de Problemas

### La aplicación no inicia
```bash
# Verificar logs
sudo journalctl -u sigq-streamlit -n 50

# Verificar permisos
sudo chown -R www-data:www-data /var/www/sigq

# Probar manualmente
cd /var/www/sigq
sudo -u www-data ./venv/bin/streamlit run app.py
```

### Error 502 Bad Gateway
```bash
# Verificar que Streamlit está ejecutándose en puerto 8501
sudo netstat -tlnp | grep 8501

# Verificar configuración de Apache
sudo apache2ctl configtest

# Ver logs de Apache
sudo tail -f /var/log/apache2/sigq_error.log
```

### Problemas con SSL
```bash
# Verificar certificados
sudo certbot certificates

# Renovar certificados
sudo certbot renew --force-renewal
```

## Notas Importantes

1. **Dominio**: Asegúrate de que tu dominio esté apuntando a la IP de tu servidor
2. **Firewall**: Verifica que los puertos 80 y 443 estén abiertos
3. **Permisos**: Todos los archivos deben pertenecer al usuario `www-data`
4. **Base de datos**: Asegúrate de que los archivos de base de datos tengan los permisos correctos
5. **Backups**: Configura backups regulares de tu aplicación y base de datos

## Estructura de Archivos Recomendada

```
/var/www/sigq/
├── app.py
├── auth.py
├── database.py
├── email_service.py
├── exports.py
├── utils.py
├── requirements.txt
├── assets/
├── backups/
├── venv/
└── .streamlit/
    └── config.toml
```
