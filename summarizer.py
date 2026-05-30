import anthropic

_client: anthropic.AsyncAnthropic | None = None


def get_client(api_key: str) -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


async def summarize_post(post: dict, api_key: str) -> str:
    client = get_client(api_key)

    prompt = f"""Actúa como un analista estratégico senior especializado en síntesis de conocimiento aplicado. Voy a darte un artículo de Substack. Analízalo con esta estructura exacta:

---

## 🏷️ TAGS PARA CAPACITIES
Propón 2 o 3 tags relevantes en formato #tag, eligiendo entre estas categorías según el contenido del artículo:
temas (#IA, #liderazgo, #estrategia, #coaching, #tecnología, #desarrollo-personal, #negocios, #ciencia)
uso (#para-clientes, #para-talleres, #para-reflexión-propia)
formato (#framework, #caso-de-estudio, #investigación, #opinión)

---

## 🧭 TESIS CENTRAL
Una sola oración que capture la idea principal del artículo.

## 💡 IDEAS CLAVE (las 3-5 más importantes)
Para cada idea:
- **Idea:** qué plantea
- **Por qué importa:** el mecanismo o evidencia detrás
- **Tensión o matiz:** qué cuestiona o contradice esta idea

## ⚡ APLICABILIDAD POR DIMENSIÓN
Para cada idea accionable, indica en cuál de estas dimensiones aplica (puede ser más de una):

🔹 CONSULTOR / ASESOR — cómo usarlo con clientes, en sesiones, en entregables
🔹 COACH / MENTOR — cómo usarlo para acompañar el desarrollo de personas
🔹 EXPOSITOR / FACILITADOR — cómo convertirlo en contenido, ejemplo o ejercicio para una audiencia
🔹 VIDA PERSONAL — cómo aplicarlo en hábitos, decisiones o relaciones cotidianas (solo si genuinamente aplica, no fuerces)

Para cada dimensión relevante, da 1 o 2 accionables concretos y específicos. Si una dimensión no aplica para este artículo, omítela.

## 🔗 CONEXIONES
¿Con qué otros conceptos, frameworks o tendencias conecta esto?
¿Hay algo que contradiga o complemente ideas que ya conoces?

## ❓ PREGUNTAS QUE ABRE
2 o 3 preguntas que este artículo debería provocarme — para reflexión propia o para llevar a conversaciones con clientes o coachees.

## 📌 FRASE PARA RECORDAR
La idea más poderosa del artículo en una sola oración memorable.

---

ARTÍCULO: "{post['title']}" por {post['author']}

{post['content']}"""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
