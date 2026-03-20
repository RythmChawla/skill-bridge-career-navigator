import './ResumeViewer.css'
import { replaceResume } from '../api/client'
import { useRef } from 'react'

export default function ResumeViewer({ profile, onUpdateResume }) {
  const fileRef = useRef()

  const handleReplace = () => {
    fileRef.current?.click()
  }

  const onFile = async (e) => {
    if (!e.target.files?.length || !profile) return
    await replaceResume(profile.id, e.target.files[0])
    if (onUpdateResume) onUpdateResume()
  }

  if (!profile || !profile.resume_url) {
    return (
      <div className="resume-viewer">
        <div className="card">
          <h2>Your Resume</h2>
          <p>No resume available.</p>
          <button onClick={handleReplace}>Upload Resume</button>
          <input ref={fileRef} type="file" accept=".pdf" onChange={onFile} hidden />
        </div>
      </div>
    )
  }

  return (
    <div className="resume-viewer">
      <div className="card resume-card">
        <div className="resume-header">
          <h2>Your Resume</h2>
          <button onClick={handleReplace}>Replace PDF</button>
        </div>
        <iframe
          title="resume"
          src={profile.resume_url}
          className="resume-frame"
        />
        <input ref={fileRef} type="file" accept=".pdf" onChange={onFile} hidden />
      </div>
    </div>
  )
}
