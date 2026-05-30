# Substack → Capacities Bot — Setup

## 1. Instalar dependencias

```bash
cd substack_bot
pip install -r requirements.txt
```

## 2. Crear archivo .env

Copia `.env.example` a `.env` y llena los valores:

```
TELEGRAM_BOT_TOKEN=    ← BotFather → /mybots → API Token
ANTHROPIC_API_KEY=     ← console.anthropic.com → API Keys
CAPACITIES_API_KEY=    ← Capacities → Settings → API
CAPACITIES_SPACE_ID=   ← Capacities → Settings → API (aparece ahí)
WEBHOOK_URL=           ← se llena en paso 4
```

## 3. Instalar ngrok

Descarga de https://ngrok.com/download e instala.
Autentícate: `ngrok authtoken TU_TOKEN`

## 4. Levantar todo

**Terminal 1 — servidor:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — ngrok:**
```bash
ngrok http 8000
```

Ngrok te da una URL tipo `https://abc123.ngrok-free.app`.
Cópiala en tu `.env` como `WEBHOOK_URL=https://abc123.ngrok-free.app`.

Reinicia el servidor (Terminal 1) para que registre el webhook.

## 5. Probar

Manda cualquier link de Substack al bot JuanBot en Telegram.
El bot responderá con el resumen y guardará en Capacities.

## Notas

- La URL de ngrok cambia cada vez que reinicias (plan gratuito).
  Para URL fija: usa ngrok con dominio estático o despliega en Railway.
- El bot solo procesa links que contengan `substack.com`.
