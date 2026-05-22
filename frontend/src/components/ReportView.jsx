// Two-pane report view shown after analysis succeeds.
//
// Left sidebar (sticky on desktop, stacks on mobile):
//   - Quick Facts  - structured metadata extracted by Agent 1
//   - Interviewer profile - Agent 2 output
//   - Company insights    - Agent 3 output
//   - Airflow strategy    - Agent 6 output
//
// Right main pane (scrollable, the focus):
//   - Predicted questions - Agent 4 output
//   - Crafted answers     - Agent 5 output

import ReactMarkdown from 'react-markdown'

export default function ReportView({ result, onEditInputs }) {
  const parsed = result.parsed_data || {}

  const company = pickField(parsed, 'company_name', 'company', 'employer')
  const role = pickField(parsed, 'job_title', 'title', 'role', 'position')
  const recruiter = pickField(
    parsed,
    'recruiter_full_name',
    'recruiter_name',
    'recruiter',
  )
  const clues = parsed.interviewer_clues || parsed.clues || {}
  const highlights = parsed.resume_highlights || parsed.highlights || []

  function downloadMarkdown() {
    if (!result?.markdown_report) return
    const blob = new Blob([result.markdown_report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'psychflow-report.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto max-w-7xl flex flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="min-w-0">
            <h1 className="text-xl font-bold text-slate-900 leading-tight">
              PsychFlow <span className="text-brand-600">AI</span>
            </h1>
            {(company || role) && (
              <p className="text-xs text-slate-600 mt-0.5 truncate">
                {[company, role].filter(Boolean).join(' \u00b7 ')}
              </p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={onEditInputs}
              className="btn-secondary"
            >
              {'\u2190 Edit inputs'}
            </button>
            <button
              type="button"
              onClick={downloadMarkdown}
              className="btn-primary"
            >
              {'\u2b07 Download .md'}
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6 grid grid-cols-1 lg:grid-cols-[20rem_minmax(0,1fr)] gap-6">
        {/* SIDEBAR -- sticky on desktop, stacks above main on mobile */}
        <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto lg:pr-2">
          <SidebarCard title={'\ud83d\udccb Quick facts'} tone="brand">
            <FactList
              facts={[
                ['Company', company],
                ['Role', role],
                ['Recruiter', recruiter],
                ['Location', clues.location],
                ['Experience', clues.years_of_experience || clues.experience],
                ['University', clues.university],
                [
                  "Past co's",
                  clues.previous_companies || clues.past_companies,
                ],
              ]}
            />
            {Array.isArray(highlights) && highlights.length > 0 && (
              <div className="mt-3 pt-3 border-t border-brand-200">
                <p className="text-[10px] uppercase tracking-wide font-semibold text-brand-700 mb-1">
                  Resume highlights
                </p>
                <ul className="list-disc pl-5 text-sm text-slate-800 space-y-1">
                  {highlights.map((h, i) => (
                    <li key={i} className="leading-snug">
                      {typeof h === 'string' ? h : JSON.stringify(h)}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </SidebarCard>

          <SidebarCard title={'\ud83e\udde0 Interviewer profile'}>
            <SidebarMarkdown>{result.psychology_profile}</SidebarMarkdown>
          </SidebarCard>

          <SidebarCard title={'\ud83c\udfe2 Company insights'}>
            <SidebarMarkdown>{result.company_analysis}</SidebarMarkdown>
          </SidebarCard>

          <SidebarCard title={'\ud83c\udfaf Airflow strategy'}>
            <SidebarMarkdown>{result.airflow_strategy}</SidebarMarkdown>
          </SidebarCard>
        </aside>

        {/* MAIN -- the focus: predicted questions + crafted answers */}
        <main className="space-y-6 min-w-0">
          <MainSection
            title={'\u2753 Predicted questions'}
            subtitle='Ranked by likelihood. "(reported)" means the question was found in real Glassdoor / LeetCode / Reddit web results.'
            content={result.predicted_questions}
          />
          <MainSection
            title={'\ud83d\udca1 Crafted answers'}
            subtitle="Witty, concise, and tied back to the role. Match the order of the questions above."
            content={result.crafted_answers}
          />
        </main>
      </div>
    </div>
  )
}

// ---------- helpers ----------

function pickField(obj, ...keys) {
  if (!obj) return null
  for (const k of keys) {
    const v = obj[k]
    if (v != null && v !== '' && !(Array.isArray(v) && v.length === 0)) {
      return v
    }
  }
  return null
}

function formatValue(v) {
  if (v == null) return ''
  if (Array.isArray(v)) return v.filter(Boolean).join(', ')
  if (typeof v === 'object') {
    return Object.entries(v)
      .filter(([, val]) => val != null && val !== '')
      .map(([k, val]) => `${k}: ${val}`)
      .join('; ')
  }
  return String(v)
}

// ---------- presentational components ----------

function SidebarCard({ title, tone, children }) {
  const cls =
    tone === 'brand'
      ? 'rounded-lg border border-brand-200 bg-brand-50 p-4 shadow-sm'
      : 'rounded-lg border border-slate-200 bg-white p-4 shadow-sm'
  return (
    <div className={cls}>
      <h3 className="text-sm font-bold text-slate-900 mb-2">{title}</h3>
      {children}
    </div>
  )
}

function FactList({ facts }) {
  const visible = facts.filter(([, v]) => v != null && v !== '')
  if (visible.length === 0) {
    return (
      <p className="text-xs text-slate-500">
        No structured facts extracted from the inputs.
      </p>
    )
  }
  return (
    <dl className="space-y-2">
      {visible.map(([label, value]) => (
        <div key={label}>
          <dt className="text-[10px] uppercase tracking-wide font-semibold text-brand-700">
            {label}
          </dt>
          <dd className="text-sm text-slate-800 leading-snug">
            {formatValue(value)}
          </dd>
        </div>
      ))}
    </dl>
  )
}

function SidebarMarkdown({ children }) {
  return (
    <div className="sidebar-markdown">
      <ReactMarkdown>{children || ''}</ReactMarkdown>
    </div>
  )
}

function MainSection({ title, subtitle, content }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-bold text-slate-900">{title}</h2>
      {subtitle && (
        <p className="text-sm text-slate-500 mt-1 mb-4">{subtitle}</p>
      )}
      <div className="main-markdown">
        <ReactMarkdown>{content || ''}</ReactMarkdown>
      </div>
    </section>
  )
}
