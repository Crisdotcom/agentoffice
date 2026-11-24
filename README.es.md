# AgentOffice

**Crea una oficina de agentes de IA para tu negocio.** Conecta cualquier LLM con tu propia API key,
contrata agentes para distintas labores (marketing, desarrollador, captador de prospectos, revisor legal…),
elige el modelo y el nivel de razonamiento de cada uno y míralos trabajar en equipo.

> 🇬🇧 [Read in English](README.md)

> **Estado:** desarrollo temprano (Fase 0). Aún no es utilizable — dale estrella para seguir el avance.

## Por qué AgentOffice

- **Cualquier LLM, por agente.** Anthropic para tu desarrollador, OpenAI para marketing, Gemini para
  revisión legal o un modelo local con Ollama — en el mismo equipo.
- **Trabajo en equipo real.** Los agentes se comunican con un formato de mensajes neutral y un espacio de
  trabajo compartido, así el contexto fluye aunque usen modelos distintos.
- **Tú tienes el control.** Modelo y razonamiento por agente, presupuestos de tokens/costo, límite de
  turnos y aprobación humana para acciones externas.
- **Mira tu oficina.** Un panel en vivo hoy; una oficina 3D donde ves trabajar a los agentes, en el roadmap.
- **Tus keys, tus datos.** Autoalójalo; las API keys se guardan cifradas.

## Inicio rápido (desarrollo)

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:5173
- API: http://localhost:8000/api/health

Detalles en [docs/architecture.md](docs/architecture.md) y el [roadmap](docs/roadmap.md).

## Open source y versión alojada

AgentOffice es open source bajo **AGPL-3.0**. Se planea una edición cloud de pago con funciones extra
(alojamiento gestionado, equipos multiusuario, SSO, agentes 24/7, créditos LLM incluidos) que financiará
el desarrollo del núcleo abierto.

## Licencia

[GNU Affero General Public License v3.0](LICENSE)
