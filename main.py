from flask import Flask, request
#from actions.issues import handle_issues
from handlers.pull_request import handle_pull_request
import threading
import discordbot  # importamos funciones y bot
from discordbot import run_bot


app = Flask(__name__)

EVENT_HANDLERS = {
    # "issues": handle_issues,
    "pull_request": handle_pull_request,
    # "fork": handle_fork,
    # "push": handle_push,
}


@app.route("/")
def home():
    return "Servidor Flask activo 🚀"


@app.route("/webhook", methods=["POST"])
def github_webhook():
    try:
        data = request.json
        event = request.headers.get("X-GitHub-Event")

        # Intentamos obtener el handler para el evento
        handler = EVENT_HANDLERS.get(event)
        if handler:
            handler(data)
        else:
            print(f"Evento no manejado: {event}")
    except Exception as e:
        # Si algo falla, se captura el error y se imprime
        print(f"Ocurrió un error al procesar el evento {event}: {e}")
        return "Error al procesar el evento", 500

    return "ok", 200


if __name__ == "__main__":
    # lanzamos Flask en un hilo paralelo
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, use_reloader=False),
        daemon=True,
    ).start()
    discordbot.run_bot()
