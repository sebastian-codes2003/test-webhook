
# Discord GitHub Pull Request Manager

Este proyecto permite **notificar y gestionar pull requests de GitHub directamente desde Discord**. Un bot recibe los webhooks de GitHub y publica los pull requests en un canal de Discord, donde los usuarios pueden:
- **Aprobar** un pull request
- **Rechazar** un pull request
- **Hacer merge** de ramas
Todo esto mediante botones y comandos interactivos en Discord, facilitando la colaboración y revisión de código sin salir de la plataforma.

---

## 🚀 Características

- 🌐 Servidor **Flask** que expone un endpoint `/webhook` para recibir eventos de GitHub.
- 🤖 **Bot de Discord** que publica pull requests en un canal y permite gestionarlos (aprobar, rechazar, merge) desde Discord.
- 🔔 Notificaciones automáticas y acciones interactivas sobre pull requests.
- 🐳 **Docker y Docker Compose** para despliegue sencillo.
- 🕒 Conversión de fechas a la zona horaria de **Lima**.
- 📂 Estructura modular para fácil extensión de eventos y comandos.

---

## 📂 Estructura del proyecto

```yaml
├── handlers/           # Handlers para eventos de GitHub (issues, pull_request)
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

### 2️⃣ Configurar variables de entorno
Crea y edita el archivo `.env` en la raíz del proyecto (ver sección abajo).

### 3️⃣ Ejecutar localmente
```bash
python main.py
```
El servidor Flask estará activo en 👉 http://localhost:5000/.

### 4️⃣ Opcional: Exponer el servidor con ngrok
Si deseas recibir webhooks de GitHub en desarrollo local, puedes usar [ngrok](https://ngrok.com/) para exponer tu servidor Flask a internet:
```bash
ngrok http 5000
```
Esto generará una URL pública que puedes usar como endpoint del webhook en GitHub:
```
http://<tu-url-ngrok>/webhook
```

### 5️⃣ Usar con Docker Compose
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
Cuando se cree un pull request, el bot lo publicará en el canal de Discord configurado. Desde ahí, los usuarios podrán aprobar, rechazar o hacer merge del pull request directamente desde Discord.

##  📦 Librerías principales
* Flask
* discord.py (py-cord)
* python-dotenv
* aiohttp
* PyGithub (API de GitHub)

## 🖥️ Tecnologías y herramientas
* Docker
* Docker Compose

## 🗝️ Configuración del archivo .env


Debes crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

| Variable                | Descripción                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `TOKEN_DISCORD`      | Token de autenticación del bot de Discord. Permite que el bot se conecte y opere en tu servidor. |
| `CHANNEL_ID_PULL_REQUEST` | ID del canal de Discord donde se publicarán y gestionarán los pull requests. |
| `TOKEN_GITHUB`       | Token personal de GitHub para acceder a la API y recibir eventos de webhooks. |
| `ADMINS_REVIEWER`    | Lista de IDs de usuarios de Discord autorizados para aprobar o rechazar pull requests. |
| `ADMINS_MERGE`       | Lista de IDs de usuarios de Discord autorizados para hacer merge de los pull requests. |



Asegúrate de completar cada variable con tus propios datos. Puedes usar `.env.template` como referencia.