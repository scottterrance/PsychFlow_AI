import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { analyze } from './api.js'

const SECTIONS = [
  { key: 'parsed_data', title: '1. Extracted Data', kind: 'json' },
  { key: 'psychology_profile', title: '2. Interviewer Psychology Profile', kind: 'md' },
  { key: 'company_analysis', title: '3. Company & JD Analysis', kind: 'md' },
  { key: 'predicted_questions', title: '4. Predicted Questions', kind: 'md' },
  { key: 'crafted_answers', title: '5. Crafted Answers', kind: 'md' },
  { key: 'airflow_strategy', title: '6. Airflow Strategy', kind: 'md' },
]

export default function App() {
  const [recruiterMessage, setRecruiterMessage] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [resume, setResume] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const data = await analyze({
        recruiter_message: recruiterMessage,
        job_description: jobDescription,
        resume,
      })
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

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
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-5">
          <h1 className="text-2xl font-bold text-slate-900">
            PsychFlow <span className="text-brand-600">AI</span>
          </h1>
          <p className="text-sm text-slate-600">
            6-agent interview prep pipeline. Paste your inputs, get a full prep
            playbook in seconds.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 space-y-6">
        <form onSubmit={onSubmit} className="card space-y-4">
          <div>
            <label className="label">Recruiter message</label>
            <textarea
              className="input"
              rows={4}
              placeholder="Paste the recruiter's email or LinkedIn DM..."
              value={recruiterMessage}
              onChange={(e) => setRecruiterMessage(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="label">Job description</label>
            <textarea
              className="input"
              rows={6}
              placeholder="Paste the full JD..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="label">Your resume (plain text)</label>
            <textarea
              className="input"
              rows={6}
              placeholder="Paste your resume content..."
              value={resume}
              onChange={(e) => setResume(e.target.value)}
              required
            />
          </div>
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500">
              Runs 6 Gemini agents. Typically 15-30 seconds.
            </p>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Analyzing...' : 'Run analysis'}
            </button>
          </div>
        </form>

        {error && (
          <div className="card border-red-200 bg-red-50 text-sm text-red-800">
            <strong className="mr-1">Error:</strong>
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Report</h2>
              <button
                type="button"
                onClick={downloadMarkdown}
                className="btn-primary"
              >
                Download .md
              </button>
            </div>

            {SECTIONS.map((s) => (
              <section key={s.key} className="card">
                <h3 className="text-base font-semibold text-slate-900 mb-3">
                  {s.title}
                </h3>
                {s.kind === 'json' ? (
                  <pre className="rounded-md bg-slate-900 p-3 text-xs text-slate-100 overflow-x-auto">
                    {JSON.stringify(result[s.key], null, 2)}
                  </pre>
                ) : (
                  <div className="markdown-body">
                    <ReactMarkdown>{result[s.key] || ''}</ReactMarkdown>
                  </div>
                )}
              </section>
            ))}
          </div>
        )}
      </main>

      <footer className="mx-auto max-w-5xl px-4 py-6 text-center text-xs text-slate-500">
        Powered by Google Gemini (free tier) + FastAPI + React.
      </footer>
    </div>
  )
}
