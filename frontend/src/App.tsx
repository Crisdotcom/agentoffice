import { useEffect, useState } from 'react'

type ApiState = 'checking' | 'ok' | 'error'

const ROLES = [
  { name: 'Office Manager', text: 'Breaks your goals into tasks and assigns them to the team.' },
  { name: 'Marketing Lead', text: 'Positioning, campaigns and ready-to-use copy.' },
  { name: 'Software Developer', text: 'Builds websites, scripts and integrations.' },
  { name: 'Lead Prospector', text: 'Finds and qualifies customers, drafts outreach.' },
  { name: 'Legal Reviewer', text: 'Flags risks in contracts and terms. Not legal advice.' },
]

const STATUS_TEXT: Record<ApiState, string> = {
  checking: 'Checking API…',
  ok: 'API connected',
  error: 'API unreachable — is the backend running?',
}

export default function App() {
  const [api, setApi] = useState<ApiState>('checking')

  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/health', { signal: controller.signal })
      .then((res) => setApi(res.ok ? 'ok' : 'error'))
      .catch((err: unknown) => {
        if (!(err instanceof DOMException && err.name === 'AbortError')) setApi('error')
      })
    return () => controller.abort()
  }, [])

  return (
    <main className="shell">
      <p className="eyebrow">AgentOffice · Phase 0</p>
      <h1>Your office of AI agents</h1>
      <p className="lede">
        Bring any LLM with your own key, give each agent a role, a model and a reasoning level, and
        let them work together as a team.
      </p>
      <p className="status" role="status" data-state={api}>
        {STATUS_TEXT[api]}
      </p>

      <ul className="roles" aria-label="Starter roles">
        {ROLES.map((role) => (
          <li className="role" key={role.name}>
            <h2>{role.name}</h2>
            <p>{role.text}</p>
          </li>
        ))}
      </ul>
    </main>
  )
}
