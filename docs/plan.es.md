# Plan: Oficina de agentes de IA open source (open-core)

## Contexto
Partimos de una carpeta vacía. El objetivo es un proyecto open source en GitHub donde el dueño de un negocio puede:
- Conectar **cualquier LLM** con su propia API key (BYOK).
- Crear **agentes con roles** (marketing, desarrollador, captador de prospectos, abogado, etc.).
- Elegir **modelo y nivel de razonamiento por agente**, mezclando proveedores (Anthropic para dev, OpenAI para marketing…).
- Que los agentes **se comuniquen y compartan contexto** para trabajar en equipo.
- Ver todo en una **oficina 3D** (fase 2).
- Modelo de negocio **open-core**: versión libre (self-hosted) + versión de pago alojada con funciones extra.

Decisiones tomadas: **Python (backend) + React (frontend)**, licencia **AGPL-3.0**, MVP = **motor de agentes + UI 2D**, frontend siguiendo la skill `googlechrome/modern-web-guidance`.

> ⚠️ **Nombre:** "OpenOffice" es marca registrada de Apache. Hay que usar otro nombre público (ej. *AgentOffice*, *Agentia HQ*, *OfficeOS*, *Crewspace*). Se define antes de crear el repo; abajo uso `agentoffice` como placeholder.

---

## Arquitectura

```
┌────────────── Frontend (React + Vite + TS) ──────────────┐
│ Dashboard 2D (MVP) · Oficina 3D (R3F, fase 2) · Chat     │
└──────────────┬───────────── REST + WebSocket ────────────┘
┌──────────────▼──────── Backend (FastAPI) ─────────────────┐
│ API · Auth · Gestión de agentes/equipos/proveedores        │
│ Orquestador ── Bus de mensajes ── Memoria compartida       │
│ llm-gateway (propio) ── Tools / MCP ── Control de costos   │
└──────┬──────────────────┬───────────────────┬─────────────┘
   Postgres+pgvector     Redis (pub/sub+cola)   Workers (arq)
```

### 1. Capa LLM agnóstica propia: `llm-gateway` (en lugar de LiteLLM)
Construimos nuestra propia capa en vez de depender de LiteLLM: control total, menos dependencias (menor riesgo de supply-chain), código más pequeño y auditable, y se puede publicar como librería independiente (marketing extra para el proyecto).

**Clave: no hacen falta 100 adaptadores, bastan 4 protocolos:**
| Adaptador | Cubre |
|---|---|
| `anthropic` (Messages API) | Claude |
| `openai` (Responses / Chat Completions) | GPT, o-series |
| `gemini` (Gemini API) | Gemini |
| `openai_compatible` (base_url configurable) | Groq, DeepSeek, Mistral, xAI, Together, OpenRouter, Ollama, LM Studio, vLLM… |

**Diseño del paquete** (`backend/packages/llm_gateway/`):
- `types.py` — tipos canónicos (Pydantic): `Message`, bloques de contenido (`Text`, `Image`, `ToolCall`, `ToolResult`, `Thinking`), `ToolSpec` (JSON Schema), `StreamEvent`, `Usage`.
- `providers/base.py` — interfaz `Provider` con `complete()`, `stream()` (async), `count_tokens()`, `list_models()`.
- `providers/{anthropic,openai,gemini,openai_compatible}.py` — traducción canónico ⇄ nativo, con `httpx` async directo (o SDK oficial donde aporte).
- `reasoning.py` — mapeo del nivel normalizado por proveedor.
- `registry/models.json` — catálogo de modelos y capacidades (mantenible por la comunidad vía PR).
- `pricing.py` — cálculo de costo desde `Usage` + precios del catálogo.
- `errors.py` + reintentos con backoff, timeouts, manejo de rate limits.
- Tests de contrato por adaptador con respuestas grabadas (fixtures), sin gastar tokens en CI.

**Detalle importante entre proveedores:** los bloques de *thinking* son específicos de cada proveedor (Anthropic los firma). Cuando el contexto pasa de un agente a otro con distinto LLM, se descartan los thinking y se pasa solo texto, tool calls y resultados — por eso la comunicación entre agentes usa el formato canónico + resúmenes.

- **Nivel de razonamiento normalizado** `off | low | medium | high` que el sistema traduce por proveedor:
  - OpenAI → `reasoning_effort`; Anthropic → extended/adaptive thinking (budget); Gemini → `thinking_budget`; modelos sin razonamiento → se oculta la opción.
- **Catálogo de modelos** (`model_registry`) con capacidades: soporta tools, visión, razonamiento, ventana de contexto, precio por token. La UI solo muestra opciones válidas para cada modelo.
- **API keys cifradas en reposo** (Fernet / envelope encryption con master key del entorno); nunca se devuelven al frontend.

### 2. Agentes y roles
- Un agente = `{rol, system prompt, modelo, proveedor, razonamiento, tools permitidas, presupuesto, escritorio en la oficina}`.
- **Plantillas de rol en YAML** (`roles/marketing.yaml`, `developer.yaml`, `sales_prospector.yaml`, `legal.yaml`, `manager.yaml`…) — la comunidad puede contribuir roles vía PR.
- Disclaimer obligatorio en roles sensibles (abogado: "no constituye asesoría legal").

### 3. Comunicación entre agentes (clave para mezclar LLMs)
El problema: cada proveedor tiene formato distinto. Solución: **formato canónico interno** y contexto compartido fuera del modelo.
- **Mensaje canónico** (`AgentMessage`: from, to, thread, tipo [task|question|result|handoff], contenido, artefactos adjuntos). `llm-gateway` lo convierte al formato de cada proveedor en cada llamada.
- **Agente Manager/Orquestador**: recibe el objetivo del usuario, lo descompone en tareas y las asigna (patrón jerárquico). Configurable también en modo "colaborativo" donde los agentes se delegan entre sí.
- Los agentes se comunican **mediante tools**, no por texto libre: `send_message(agent, msg)`, `delegate_task(agent, task)`, `ask(agent, question)`, `write_shared(key, content)`, `read_shared(query)`.
- **Memoria compartida (blackboard)**: documentos/artefactos del proyecto + memoria semántica en pgvector. Cada agente recibe un **resumen de contexto** relevante en lugar del historial completo de otros (controla tokens y funciona entre modelos con ventanas distintas).
- **Bus de eventos** (Redis pub/sub): cada acción emite un evento (`agent.thinking`, `agent.message_sent`, `task.completed`…) → se transmite por WebSocket a la UI (y luego anima la oficina 3D).
- **Guardrails**: límite de turnos por hilo (evita loops infinitos entre agentes), presupuesto de tokens/USD por agente y por tarea, **aprobación humana** para acciones externas (enviar email, publicar, ejecutar código en producción).

### 4. Herramientas (tools)
- Integradas: búsqueda web, leer URL, archivos del workspace, generación de documentos.
- **Soporte MCP (cliente)**: cualquier servidor MCP (Gmail, CRM, Notion, GitHub…) se conecta y se asigna a agentes específicos — así la comunidad extiende sin tocar el core.
- Ejecución de código (agente dev) en **sandbox Docker** aislado — fase 3.

### 5. Frontend
- React + Vite + TypeScript, siguiendo `modern-web-guidance` (se instala y revisa en Fase 0).
- TanStack Query para datos, Zustand para estado de tiempo real, componentes accesibles.
- MVP 2D: lista/tablero de agentes, editor de agente (modelo + razonamiento), gestor de API keys, chat con un agente o con el equipo, **timeline en vivo** de mensajes entre agentes, tablero de tareas, panel de costos.
- Fase 2 3D: **React Three Fiber + drei**. Oficina low-poly (GLB), cada agente en su escritorio con estados animados (idle, pensando, hablando, esperando aprobación); líneas/burbujas cuando dos agentes se comunican; click en agente → abre su panel. Fallback 2D automático en equipos débiles. Assets se pueden modelar con el MCP de Blender disponible.

### 6. Open-core: libre vs. pago
| Open source (AGPL, self-hosted) | Cloud de pago |
|---|---|
| Agentes ilimitados, BYOK, todos los proveedores | Alojamiento gestionado, sin instalar nada |
| Orquestación, memoria, MCP, UI 2D/3D | Agentes 24/7 y tareas programadas |
| 1 usuario / 1 oficina | Multiusuario, equipos, roles y permisos, SSO |
| Docker Compose | Créditos LLM incluidos (sin traer key) |
| | Integraciones premium, backups, analítica, oficinas/skins 3D premium, soporte |

- Repo público `agentoffice` (AGPL). Funciones cloud en **repo privado separado** que consume el core como paquete/plugins (puntos de extensión: auth provider, billing, storage, scheduler). Así el core se mantiene limpio y no se filtra código de pago.
- **CLA** (o DCO + CLA) para contribuidores, necesario para poder relicenciar el código en la versión comercial.

---

## Estructura del repo (monorepo)
```
agentoffice/
├── backend/
│   ├── app/
│   │   ├── api/            # routers FastAPI (agents, teams, providers, tasks, ws)
│   │   ├── core/           # config, seguridad, cifrado de keys
│   │   ├── llm/            # integración del gateway con la app (keys, presupuesto)
│   │   ├── agents/         # runtime del agente, loop de tools
│   │   ├── orchestration/  # manager, bus, threads, guardrails
│   │   ├── memory/         # blackboard, pgvector, resúmenes
│   │   ├── tools/          # tools integradas + cliente MCP
│   │   ├── models/         # SQLAlchemy
│   │   └── workers/        # tareas arq
│   ├── packages/llm_gateway/  # capa LLM propia (publicable en PyPI)
│   ├── roles/              # plantillas YAML
│   ├── alembic/
│   └── tests/
├── frontend/
│   └── src/ (features/agents, features/office3d, features/chat, lib/ws …)
├── docker-compose.yml      # api, worker, web, postgres, redis
├── docs/                   # arquitectura, crear roles, agregar proveedor
├── LICENSE (AGPL-3.0) · README · CONTRIBUTING · CODE_OF_CONDUCT · SECURITY.md
└── .github/workflows/      # lint, tests, build de imágenes
```
Stack backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, httpx, arq, `uv` (workspace) para dependencias, Ruff + pytest.

---

## Roadmap

**Fase 0 – Fundación (1 semana)**
Nombre definitivo, repo GitHub, licencia AGPL, README con visión, monorepo, Docker Compose, CI, instalar/revisar skill `modern-web-guidance`.

**Fase 1 – MVP motor de agentes + UI 2D (4–6 semanas)**
1. `llm-gateway`: tipos canónicos + adaptadores `anthropic`, `openai`, `gemini`, `openai_compatible` (streaming, tools, razonamiento, costos) con tests de contrato.
2. Gestión de proveedores y API keys cifradas + test de conexión + catálogo de modelos.
3. CRUD de agentes + 5 plantillas de rol.
4. Runtime del agente con loop de tools y streaming.
5. Comunicación entre agentes (tools de mensajería, manager, blackboard, límites de turnos).
6. Eventos por WebSocket + timeline en vivo.
7. Control de costos por agente/tarea.
8. UI 2D: agentes, chat, tareas, costos.
**Demo de lanzamiento:** "Lanza un producto": manager (Claude) reparte → marketing (GPT) escribe campaña, dev (Claude) hace landing, legal (Gemini) revisa términos.

**Fase 2 – Oficina 3D (3–4 semanas)**
Escena R3F, escritorios y avatares, animaciones ligadas a eventos, interacción click-to-chat, editor de distribución de oficina.

**Fase 3 – Poder real (continuo)**
Cliente MCP, sandbox de código, aprobaciones humanas, tareas programadas, memoria a largo plazo, marketplace de roles comunitario.

**Fase 4 – Cloud de pago**
Multi-tenant, auth/SSO, billing (Stripe), créditos LLM, despliegue gestionado, landing comercial.

---

## Verificación
- **Unit tests** (pytest): mapeo de razonamiento por proveedor, cifrado de keys, conversión de mensaje canónico, guardrails (límite de turnos/presupuesto).
- **Tests de contrato** de cada adaptador de `llm-gateway` con respuestas grabadas, más un test "en vivo" opcional (solo local, con keys reales) por proveedor.
- **Tests de integración** con un `FakeProvider` del gateway para el flujo manager → agentes → resultado, sin gastar tokens en CI.
- **Prueba E2E manual**: `docker compose up`, cargar keys de 2 proveedores distintos, crear 3 agentes con modelos distintos, ejecutar la demo y verificar en el timeline que se pasan contexto y que el costo se registra.
- Frontend: Vitest + Playwright para flujos principales; revisar en el navegador integrado.

## Primer paso al aprobar
Ejecutar Fase 0: elegir nombre, scaffolding del monorepo (backend FastAPI + frontend React/Vite), Docker Compose, LICENSE, README y CI.
