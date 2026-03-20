import { useState } from 'react'
import './FileUpload.css'

export default function FileUpload({ onFileSelect }) {
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      if (files[0].type === 'application/pdf') {
        onFileSelect(files[0])
      }
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0])
    }
  }

  return (
    <div
      className={`file-upload ${dragActive ? 'active' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        id="pdf-input"
        accept=".pdf"
        onChange={handleChange}
        style={{ display: 'none' }}
      />
      <label htmlFor="pdf-input" className="upload-label">
        <div className="upload-icon">📄</div>
        <div className="upload-text">
          <p className="main">Drop your PDF resume here</p>
          <p className="sub">or click to browse</p>
        </div>
      </label>
    </div>
  )
}
