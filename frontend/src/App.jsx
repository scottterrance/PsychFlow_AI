import { useState } from 'react'
import { analyze } from './api.js'
import InputForm from './components/InputForm.jsx'
import ReportView from './components/ReportView.jsx'

export default function App() {
  // Inputs are kept at the top level so they survive when the user clicks
  // "Edit inputs" on the report view to come back and tweak them.
  const [recruiterMessage, setRecruiterMessage] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [resume, setResume] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  async function onAnalyze() {
    setError(null)
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
      setError({
        message: err.message || 'Something went wrong.',
        status: err.status || 0,
      })
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return (
      <ReportView result={result} onEditInputs={() => setResult(null)} />
    )
  }

  return (
    <InputForm
      recruiterMessage={recruiterMessage}
      setRecruiterMessage={setRecruiterMessage}
      jobDescription={jobDescription}
      setJobDescription={setJobDescription}
      resume={resume}
      setResume={setResume}
      loading={loading}
      error={error}
      onAnalyze={onAnalyze}
    />
  )
}
