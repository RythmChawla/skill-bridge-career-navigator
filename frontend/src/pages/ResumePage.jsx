import { useState, useEffect } from 'react'
import FileUpload from '../components/FileUpload'
import SkillInput from '../components/SkillInput'
import { createProfile, getJobs } from '../api/client'
import './ResumePage.css'

export default function ResumePage({ onComplete, defaultName }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [jobs, setJobs] = useState([])
  const [profileName, setProfileName] = useState(defaultName || '')
  const [currentRole, setCurrentRole] = useState('')
  const [skills, setSkills] = useState([])
  const [resumeFile, setResumeFile] = useState(null)
  const [parsedMeta, setParsedMeta] = useState({})

  useEffect(() => {
    loadJobs()
  }, [])

  useEffect(() => {
    if (defaultName) setProfileName(defaultName)
  }, [defaultName])

  const loadJobs = async () => {
    try {
      const res = await getJobs()
      setJobs(res.data)
      if (res.data.length > 0) {
        setCurrentRole(res.data[0].title)
      }
    } catch (err) {
      console.error('Failed to load jobs:', err)
    }
  }

  const handleFileUpload = (file) => {
    setResumeFile(file)
  }

  const handleAddSkill = (skill) => {
    if (skill && !skills.includes(skill)) {
      setSkills([...skills, skill])
    }
  }

  const handleRemoveSkill = (skill) => {
    setSkills(skills.filter(s => s !== skill))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!profileName || !currentRole) {
      setError('Please fill in all required fields (name and target role)')
      return
    }

    // Check if at least one skill input method is being used
    if (!resumeFile && (!skills || skills.length === 0)) {
      setError('⚠️ Please provide skills using at least one method:\n1. Upload a text-based resume PDF, OR\n2. Add skills manually (comma-separated)')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Create profile with form data
      const profileRes = await createProfile({
        name: profileName,
        target_role: currentRole,
        current_skills: skills,
        resume: resumeFile  // Include the resume file
      })

      const profileData = profileRes.data
      // Pre-fill manual skills list with extracted skills
      if (profileData.skills) {
        setSkills(profileData.skills)
      }
      const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
      const resume_url = profileData.resume_path ? `${base}/uploads/${profileData.resume_path}` : null
      setParsedMeta({
        email: profileData.email,
        phone: profileData.phone,
        socials: profileData.socials,
        experience: profileData.experience,
        projects: profileData.projects,
        education: profileData.education,
      })
      
      console.log('Profile created successfully:', {
        id: profileData.id,
        name: profileData.name,
        skills: profileData.skills,
        skillCount: profileData.skills ? profileData.skills.length : 0
      })

      // Validate that we got skills
      if (!profileData.skills || profileData.skills.length === 0) {
        setError('⚠️ No skills were extracted from your resume. Please try:\n1. Uploading a text-based (not scanned) PDF, OR\n2. Adding skills manually instead')
        setLoading(false)
        return
      }

      // Pass data to results page
      onComplete({
        id: profileData.id,
        name: profileData.name || profileName,
        current_role: profileData.target_role || currentRole,
        current_skills: profileData.skills || skills,
        resume_url,
        email: profileData.email,
        phone: profileData.phone,
        location: profileData.location,
        socials: profileData.socials,
        experience: profileData.experience,
        projects: profileData.projects,
        education: profileData.education,
        resume_last_updated: profileData.resume_last_updated
      })
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to create profile'
      console.error('Profile creation error:', errorMsg)
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="resume-page">
      <div className="resume-card">
        <h1>📄 Create Your Profile</h1>
        <p className="subtitle">Upload your resume and tell us about your skills</p>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label>Your Name *</label>
            <input
              type="text"
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
              placeholder="e.g., John Doe"
              required
            />
          </div>

          <div className="form-group">
            <label>Target Career Role *</label>
            <select
              value={currentRole}
              onChange={(e) => setCurrentRole(e.target.value)}
              required
            >
              <option value="">-- Select your target role --</option>
              <option value="Student">Student</option>
              {jobs.map(job => (
                <option key={job.id} value={job.title}>{job.title}</option>
              ))}
            </select>
          </div>

          <div className="form-section">
            <h3>🎯 How to Add Your Skills</h3>
            <p className="form-help">Choose one or both methods below:</p>
          </div>

          <div className="form-group">
            <label>Method 1: Upload Resume (PDF) <span className="optional">optional</span></label>
            <p className="form-hint">PDF must be text-based (not scanned). We'll extract skills automatically.</p>
            <FileUpload onFileSelect={handleFileUpload} />
            {resumeFile && (
              <p className="file-selected">✓ {resumeFile.name}</p>
            )}
          </div>

          <div className="form-divider">
            <span>OR</span>
          </div>

          <div className="form-group">
            <label>Method 2: Add Skills Manually <span className="optional">optional</span></label>
            <p className="form-hint">Enter skills like: Python, React, Docker, AWS, etc. (comma-separated or one at a time)</p>
            <SkillInput 
              onAdd={handleAddSkill}
              skills={skills}
              onRemove={handleRemoveSkill}
            />
            {skills.length > 0 && (
              <p className="skills-added">✓ {skills.length} skill{skills.length !== 1 ? 's' : ''} added</p>
            )}
          </div>

          <div className="form-note">
            <strong>⚠️ Note:</strong> You must provide at least one skill using either method above to continue.
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="submit-btn"
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Analyze & Get Feedback →'}
          </button>
        </form>
      </div>
    </div>
  )
}
