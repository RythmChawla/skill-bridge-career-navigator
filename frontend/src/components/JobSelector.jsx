import { useEffect, useState } from 'react'
import { getJobs } from '../api/client'
import './JobSelector.css'

export default function JobSelector({ value, onChange }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const res = await getJobs()
      setJobs(res.data)
      if (res.data.length > 0 && !value) {
        onChange(res.data[0])
      }
    } catch (err) {
      setError('Failed to load jobs')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading-skeleton"></div>
  }

  if (error) {
    return <div className="error">{error}</div>
  }

  return (
    <div className="job-selector-container">
      <div className="job-grid">
        {jobs.map(job => (
          <button
            key={job.id}
            className={`job-card ${value?.id === job.id ? 'selected' : ''}`}
            onClick={() => onChange(job)}
          >
            <span className="job-title">{job.title}</span>
            <span className="job-level">{job.level}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
