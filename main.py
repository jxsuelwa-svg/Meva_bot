import json
import sqlite3
import threading
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================= CONFIGURACIÓN =================
TOKEN = "8423978432:AAHAziHcphZasmLJ-iayp4iJ48ceM9y8Kts"
ADMIN_ID = 7390841762
URL_API = f"https://api.telegram.org/bot{TOKEN}"

# ================= BASE DE DATOS =================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0.0
)
""")
conn.commit()


def get_user_balance(user_id):
  cursor.execute(
      "SELECT balance FROM users WHERE user_id = ?",
      (user_id,),
  )
  row = cursor.fetchone()
  if row:
    return row[0]
  else:
    cursor.execute(
        "INSERT INTO users (user_id, balance) VALUES (?, 0.0)",
        (user_id,),
    )
    conn.commit()
    return 0.0


def update_user_balance(user_id, amount):
  get_user_balance(user_id)  # Asegurar existencia
  cursor.execute(
      "UPDATE users SET balance = balance + ? WHERE user_id = ?",
      (amount, user_id),
  )
  conn.commit()


# ================= SERVIDOR WEB (Para Render) =================
class DummyHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Bot de Telegram Activo y Operativo 24/7!")

  def log_message(self, format, *args):
    pass  # Evita saturar la consola con logs del servidor web


def run_web_server():
  server = HTTPServer(("0.0.0.0", 10000), DummyHandler)
  server.serve_forever()


# ================= FUNCIONES DE TELEGRAM =================
def enviar_mensaje(chat_id, texto, reply_markup=None):
  url = f"{URL_API}/sendMessage"
  data = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
  if reply_markup:
    data["reply_markup"] = json.dumps(reply_markup)

  req = urllib.request.Request(
      url,
      data=json.dumps(data).encode("utf-8"),
      headers={"Content-Type": "application/json"},
  )
  try:
    with urllib.request.urlopen(req) as response:
      return json.loads(response.read().decode())
  except Exception as e:
    print(f"Error al enviar mensaje: {e}")


def manejar_mensajes():
  offset = 0
  print("¡Bot iniciado correctamente y escuchando mensajes!")

  while True:
    url = f"{URL_API}/getUpdates?offset={offset}&timeout=30"
    try:
      req = urllib.request.Request(url)
      with urllib.request.urlopen(req, timeout=35) as response:
        resultado = json.loads(response.read().decode())

        if resultado.get("ok"):
          for update in resultado.get("result", []):
            offset = update["update_id"] + 1

            # Procesar mensajes de texto
            if "message" in update:
              msg = update["message"]
              chat_id = msg["chat"]["id"]
              user_id = msg["from"]["id"]
              text = msg.get("text", "")

              if text == "/start":
                enviar_mensaje(
                    chat_id,
                    "👋 **¡Bienvenido al sistema de gestión de números virtuales!**\n\n"
                    "Comandos disponibles:\n"
                    "💰 `/saldo` - Consultar tu saldo actual\n"
                    "💳 `/recargar` - Solicitar recarga de saldo\n"
                    "📱 `/comprar` - Adquirir un número virtual",
                )

              elif text == "/saldo":
                saldo = get_user_balance(user_id)
                enviar_mensaje(
                    chat_id,
                    f"💳 **Tu saldo actual es:** `${saldo:.2f}` USD",
                )

              elif text == "/recargar":
                enviar_mensaje(
                    chat_id,
                    "ℹ️ Para recargar saldo, por favor contacta al administrador.",
                )
                # Notificar al admin
                enviar_mensaje(
                    ADMIN_ID,
                    f"🔔 El usuario `{user_id}` ha solicitado una recarga.",
                )

              elif text == "/comprar":
                enviar_mensaje(
                    chat_id,
                    "📱 Selecciona el servicio para tu número virtual (Función en desarrollo).",
                )

              # Comandos de administración rápidos (Ej: /add 7390841762 50)
              elif text.startswith("/add") and user_id == ADMIN_ID:
                partes = text.split()
                if len(partes) == 3:
                  target_id = int(partes[1])
                  monto = float(partes[2])
                  update_user_balance(target_id, monto)
                  nuevo_saldo = get_user_balance(target_id)
                  enviar_mensaje(
                      chat_id,
                      f"✅ Se han añadido ${monto} al usuario `{target_id}`.\n"
                      f"Nuevo saldo del usuario: `${nuevo_saldo:.2f}`",
                  )
                  enviar_mensaje(
                      target_id,
                      f"🎉 ¡Tu cuenta ha sido recargada con `${monto:.2f}`!\n"
                      f"Tu nuevo saldo es: `${nuevo_saldo:.2f}`",
                  )
                else:
                  enviar_mensaje(
                      chat_id,
                      "⚠️ Formato incorrecto. Usa: `/add <user_id> <monto>`",
                  )

    except Exception as e:
      print(f"Error en el ciclo de actualizaciones: {e}")
      time.sleep(5)


# ================= INICIO DE HILOS =================
if __name__ == "__main__":
  # Iniciar servidor web en segundo plano para cumplir con los requisitos de Render
  threading.Thread(target=run_web_server, daemon=True).start()

  # Iniciar el bot de Telegram
  manejar_mensajes()
