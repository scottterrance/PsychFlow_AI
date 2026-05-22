// The initial form view - paste recruiter message, JD, resume, then click
// "Run analysis". Replaced by ReportView once a result comes back.

export default function InputForm({
  recruiterMessage,
  setRecruiterMessage,
  jobDescription,
  setJobDescription,
  resume,
  setResume,
  loading,
  error,
  onAnalyze,
}) {
  const isRateLimit = error?.status === 429

  function onSubmit(e) {
    e.preventDefault()
    onAnalyze()
  }

  return (
    <div className="min-h-screen bg-slate-50">
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
              Runs 6 Groq agents + live web research. Typically 15-30 seconds
              (longer if rate-limited).
            </p>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Analyzing...' : 'Run analysis'}
            </button>
          </div>
        </form>

        {error && isRateLimit && (
          <div className="card border-amber-200 bg-amber-50 text-sm text-amber-900">
            <strong className="block mb-1">Groq rate limit hit</strong>
            <p className="mb-2">{error.message}</p>
            <p className="text-xs text-amber-800">
              Tip: edit{' '}
              <code className="rounded bg-amber-100 px-1">backend/.env</code>{' '}
              and set{' '}
              <code className="rounded bg-amber-100 px-1">
                GROQ_MODEL=llama-3.1-8b-instant
              </code>{' '}
              for the smallest, fastest model that almost never hits the limit.
            </p>
          </div>
        )}

        {error && !isRateLimit && (
          <div className="card border-red-200 bg-red-50 text-sm text-red-800">
            <strong className="mr-1">Error:</strong>
            {error.message}
          </div>
        )}
      </main>

      <footer className="mx-auto max-w-5xl px-4 py-6 text-center text-xs text-slate-500">
        Powered by Groq (free tier) + DuckDuckGo + FastAPI + React.
      </footer>
    </div>
  )
}
