# Discord GitHub Webhook Bot

Este proyecto integra un **bot de Discord** con un **servidor Flask** que recibe *webhooks* de GitHub.  
Permite notificar automáticamente en un canal de Discord sobre **nuevos issues y pull requests** en un repositorio, mostrando información enriquecida y comandos interactivos.

---

## 🚀 Características

- 🌐 Servidor **Flask** que expone un endpoint `/webhook` para recibir eventos de GitHub.  
- 🤖 **Bot de Discord** con comandos y eventos personalizados.  
- 🔔 Notificaciones automáticas en Discord para **issues** y **pull requests**.  
- 🐳 **Docker y Docker Compose** para despliegue sencillo.  
- 🕒 Conversión de fechas a la zona horaria de **Lima**.  
- 📂 Estructura modular para fácil extensión de eventos y comandos.  

---

## 📂 Estructura del proyecto

```yaml
├── actions/            # Handlers para eventos de GitHub (issues, pull_request)
├── utils/              # Utilidades (formateo de fechas)
├── discordbot.py       # Lógica y comandos del bot de Discord
├── main.py             # Servidor Flask y webhook principal
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Imagen Docker para el bot y servidor
├── docker-compose.yml  # Orquestación de servicios
└── README.md           # Documentación del proyecto
```

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/discord-github-webhook-bot.git
cd discord-github-webhook-bot
```
### 2️⃣ Ejecutar localmente
```bash
python main.py
```
El servidor Flask estará activo en 👉 http://localhost:5000/.

### 2️⃣ Opcional: Exponer el servidor con ngrok
Si deseas recibir webhooks de GitHub en desarrollo local, puedes usar [ngrok](https://ngrok.com/) para exponer tu servidor Flask a internet:

```bash
ngrok http 5000
```
Esto generará una URL pública que puedes usar como endpoint del webhook en GitHub:

```
http://<tu-url-ngrok>/webhook
```

### 3️⃣ Usar con Docker Compose

Despliegue de ambiente y ejecución del servidor web
```bash
docker-compose up --build -d
```

Eliminación de ambiente
```bash
docker-compose down -v
```

## 🛠️ Uso
Configura el webhook de GitHub para que apunte a:

```arduino
http://TU_DOMINIO/webhook
```
O si usas ngrok:

```arduino
http://<tu-url-ngrok>/webhook
```
Cuando se cree un issue o pull request, el bot notificará automáticamente en el canal de Discord configurado.

##  📦 Librerías principales
* Flask
* discord.py (py-cord)
* python-dotenv
* aiohttp
* PyGithub (API de GitHub)

## 🖥️ Tecnologías y herramientas
* Docker
* Docker Compose
* ngrok (para desarrollo local y pruebas de webhooks)