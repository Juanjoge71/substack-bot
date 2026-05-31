import anthropic

_client: anthropic.AsyncAnthropic | None = None


def get_client(api_key: str) -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


async def summarize_post(post: dict, api_key: str) -> str:
    client = get_client(api_key)

    prompt = f"""Actúa como mi asistente de síntesis estratégica. Contexto sobre mí: soy consultor y asesor con experiencia ejecutiva, trabajo con clientes en transformación tecnológica, estrategia de TI y ciberseguridad OT. Uso este resumen para alimentar mi segundo cerebro en Capacities.

Voy a darte un artículo de Substack. Analízalo con esta estructura exacta:

---

## 🏷️ TAGS PARA CAPACITIES
Propón exactamente 3 tags: 1 de tema + 1 de uso + 1 de formato.
Elige de estas opciones:

Tema: #IA, #liderazgo, #estrategia, #coaching, #tecnología, #desarrollo-personal, #negocios, #ciencia, #ciberseguridad, #finanzas

Uso: #para-clientes, #para-talleres, #para-reflexión-propia

Formato: #framework, #caso-de-estudio, #investigación, #opinión

Si el artículo claramente abarca un segundo tema relevante, añade solo ese tag adicional (máximo 4 en total).

## 📂 COLECCIÓN
Colección: Substack

## 🧭 TESIS CENTRAL
Una sola oración que capture la idea principal del artículo.

## 💡 IDEAS CLAVE (las 3-5 más importantes)
Para cada idea:
- **Idea:** qué plantea
- **Por qué importa:** el mecanismo o evidencia detrás
- **Tensión o matiz:** qué cuestiona o contradice esta idea

## 📖 HISTORIAS Y CASOS
(Solo si el artículo los incluye — si no, omite esta sección)
Para cada caso o historia mencionada:
- **Quién / Qué:** persona, empresa o situación
- **Qué hicieron:** la acción o decisión clave
- **Resultado:** qué logró o demostró
- **Lección transferible:** qué puedo extraer yo de este caso

## ⚡ APLICABILIDAD POR DIMENSIÓN
Para cada idea accionable, indica en cuál de estas dimensiones aplica (puede ser más de una):
🔹 CONSULTOR / ASESOR — cómo usarlo con clientes, en sesiones, en entregables
🔹 COACH / MENTOR — cómo usarlo para acompañar el desarrollo de personas
🔹 EXPOSITOR / FACILITADOR — cómo convertirlo en contenido, ejemplo o ejercicio para una audiencia
🔹 VIDA PERSONAL — cómo aplicarlo en hábitos, decisiones o relaciones cotidianas (solo si genuinamente aplica, no fuerces)

Para cada dimensión relevante, da 1 o 2 accionables concretos y específicos. Si una dimensión no aplica para este artículo, omítela.

## 🔗 CONEXIONES CON MI CONOCIMIENTO PREVIO
¿Con qué conceptos que ya tengo procesados conecta este artículo?
¿Qué confirma, contradice o extiende?

Sugiere @links usando SOLO los Zettels de esta lista — si la conexión es genuina y directa, no por similitud superficial:

CYBERSECURITY: @Separación entre autenticación y confidencialidad, @La gestión de claves es el eslabón débil real, @TLS Handshake — secuencia de establecimiento de sesión segura, @Firma digital — autenticidad e integridad en un solo mecanismo, @Modelo OSI de seguridad — cinco servicios fundamentales, @Diferencia entre firewalls e IDS — complementarios no equivalentes, @Air Gap, @IEC 62443, @IDMZ (Industrial Demilitarized Zone), @Modelo Purdue, @ISA-95, @Credential Stuffing — Relleno de Credenciales, @MFA / 2FA — Autenticación Multifactor, @Ingeniería Social y Phishing, @Seguridad vs Usabilidad, @Autenticación vs Autorización

ECONOMÍA DEL COMPORTAMIENTO: @El Método Seinfeld, @Descuento Hiperbólico, @La Falacia del Costo Hundido, @Efecto de Dotación (Endowment Effect), @El Método del Clip (o Paper Clip Strategy), @Choice Architecture, @Economía del comportamiento, @Nudge, @Metacognición, @Memoria de trabajo, @Deuda Epistémica

NEUROCIENCIA: @Estímulo Emocionalmente Competente (ECS), @Pensamiento Visual vs Pensamiento Lineal, @Efecto Einstellung, @Sistema de Activación Reticular (SAR), @Cognitive Offloading, @Carga Cognitiva, @Pensamiento Sistémático

COMPORTAMIENTO Y PSICOLOGÍA: @La Regla de los 18 Minutos, @Incongruencia Entre Palabras y Cuerpo

STORYTELLING: @El Mapa de Mensajes de Tres Pasos

AI: @La Tesis de la Ortogonalidad en los Sistemas Inteligentes, @La Ideología de la Abstracción Infraestructural en Tecnología, @Manipulación Empática Adaptativa, @Ideología de la Escala (Ideology of Scale), @Las Cuatro Olas de la Evolución de la IA, @Matriz de Desplazamiento y Empatía Laboral

FINANZAS: @Sabiduría Mundana Elemental (Elementary Worldly Wisdom), @El Efecto Lollapalooza, @Red de Modelos Mentales (Latticework of Mental Models)

LIDERAZGO: @El Rol del Líder como Compositor y Conductor en la Era de la IA, @Empathetic Strength (Fuerza Empática)

Si el artículo no conecta genuinamente con ninguno, escribe: "Sin conexiones directas con Zettels existentes."

## ❓ PREGUNTAS QUE ABRE
2 o 3 preguntas que este artículo debería provocarme — para reflexión propia o para llevar a conversaciones con clientes o coachees.

## 🕳️ LO QUE EL ARTÍCULO NO DICE
(Solo si es relevante — omite si no aplica)
¿Qué asumió el autor sin demostrar? ¿Qué perspectiva importante omitió?

## 📌 FRASE PARA RECORDAR
La idea más poderosa del artículo en una sola oración memorable.

---

FORMATO DE SALIDA:
- Usa markdown estándar
- Cada punto de lista en una sola línea, sin saltos innecesarios
- Las listas dentro de Ideas Clave: máximo 2 líneas por punto
- No escribas introducción ni cierre — solo la estructura pedida

---

ARTÍCULO: "{post['title']}" por {post['author']}

{post['content']}"""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
