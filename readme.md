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

.
├── actions/ # Handlers de eventos de GitHub
├── bot/ # Lógica del bot de Discord
├── main.py # Entrada principal del servidor Flask
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.template
└── README.md

yaml
Copy code

---

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/discord-github-webhook-bot.git
cd discord-github-webhook-bot
```
### 2️⃣ Configurar variables de entorno
Copia el archivo .env.template a .env y completa los valores necesarios:
```bash
cp .env.template .env
```
### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```
### 4️⃣ Ejecutar localmente
```bash
python main.py
```
El servidor Flask estará activo en 👉 http://localhost:5000/.

### 5️⃣ Usar con Docker
```bash
docker-compose up --build -d
```

## 🛠️ Uso
Configura el webhook de GitHub para que apunte a:

``` arduino
http://TU_DOMINIO/webhook
```
Cuando se cree un issue o pull request, el bot notificará automáticamente en el canal de Discord configurado.

## 🤖 Principales comandos del bot
* /saludo → El bot responde con un saludo.
* !button → Muestra un botón interactivo en Discord.

##  🔧 Extensión
Puedes agregar más eventos de GitHub editando el diccionario EVENT_HANDLERS en main.py y creando nuevos handlers en la carpeta actions.

##  📦 Dependencias principales
* Flask
* discord.py (py-cord)
* python-dotenv
* aiohttp
* Docker