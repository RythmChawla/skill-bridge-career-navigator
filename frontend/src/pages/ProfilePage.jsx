import { useState } from 'react'
import { patchProfile } from '../api/client'
import './ProfilePage.css'

function ActionButton({ children, onClick, type = 'button', variant = 'soft' }) {
  return (
    <button type={type} className={`action-btn ${variant}`} onClick={onClick}>
      {children}
    </button>
  )
}

function EditableTextField({ label, value, onSave, placeholder = '' }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value || '')

  const handleSave = async () => {
    await onSave(draft)
    setEditing(false)
  }

  return (
    <div className="field-card">
      <div className="field-card-head">
        <div>
          <p className="field-label">{label}</p>
          {!editing && <p className="field-value">{value || 'Not added yet'}</p>}
        </div>
        {!editing && <ActionButton onClick={() => setEditing(true)}>Edit</ActionButton>}
      </div>
      {editing && (
        <div className="field-editor">
          <input value={draft} placeholder={placeholder} onChange={(e) => setDraft(e.target.value)} />
          <div className="field-actions">
            <ActionButton variant="primary" onClick={handleSave}>Save</ActionButton>
            <ActionButton onClick={() => { setDraft(value || ''); setEditing(false) }}>Cancel</ActionButton>
          </div>
        </div>
      )}
    </div>
  )
}

function EditableSkills({ skills, onSave }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(skills || [])
  const [input, setInput] = useState('')

  const addSkill = () => {
    const next = input.trim()
    if (next && !draft.includes(next)) {
      setDraft([...draft, next])
      setInput('')
    }
  }

  const removeSkill = (skill) => setDraft(draft.filter((item) => item !== skill))

  const handleSave = async () => {
    await onSave(draft)
    setEditing(false)
  }

  return (
    <div className="section-card">
      <div className="section-card-head">
        <div>
          <h3>Skills</h3>
          <p>Technical and domain skills extracted from your resume or added manually.</p>
        </div>
        {!editing && <ActionButton onClick={() => setEditing(true)}>Edit</ActionButton>}
      </div>
      {editing && (
        <div className="skills-editor">
          <div className="inline-add">
            <input value={input} placeholder="Add a skill" onChange={(e) => setInput(e.target.value)} />
            <ActionButton onClick={addSkill}>Add</ActionButton>
          </div>
          <div className="chip-row">
            {draft.map((skill) => (
              <span key={skill} className="chip">
                {skill}
                <button type="button" onClick={() => removeSkill(skill)}>x</button>
              </span>
            ))}
          </div>
          <div className="field-actions">
            <ActionButton variant="primary" onClick={handleSave}>Save</ActionButton>
            <ActionButton onClick={() => { setDraft(skills || []); setEditing(false) }}>Cancel</ActionButton>
          </div>
        </div>
      )}
      {!editing && (
        <div className="chip-row">
          {(skills || []).length > 0
            ? skills.map((skill) => <span key={skill} className="chip static">{skill}</span>)
            : <p className="empty-note">No skills added yet.</p>}
        </div>
      )}
    </div>
  )
}

function StructuredListEditor({ title, subtitle, items, emptyLabel, fields, onSave, addTemplate }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(items || [])

  const updateItem = (index, key, value) => {
    setDraft(draft.map((item, idx) => idx === index ? { ...item, [key]: value } : item))
  }

  const addItem = () => setDraft([...draft, { ...addTemplate }])
  const removeItem = (index) => setDraft(draft.filter((_, idx) => idx !== index))

  const handleSave = async () => {
    const cleaned = draft.filter((item) => Object.values(item).some((value) => {
      if (Array.isArray(value)) return value.length > 0
      return String(value || '').trim() !== ''
    }))
    await onSave(cleaned)
    setEditing(false)
  }

  return (
    <div className="section-card">
      <div className="section-card-head">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        {!editing && <ActionButton onClick={() => setEditing(true)}>Edit</ActionButton>}
      </div>

      {editing ? (
        <div className="stack-list">
          {draft.map((item, index) => (
            <div key={index} className="structured-item editor">
              <div className="structured-item-head">
                <span>{title} #{index + 1}</span>
                <ActionButton onClick={() => removeItem(index)}>Remove</ActionButton>
              </div>
              {fields.map((field) => (
                <div key={field.key} className="structured-field">
                  <label>{field.label}</label>
                  {field.type === 'textarea' ? (
                    <textarea
                      value={item[field.key] || ''}
                      placeholder={field.placeholder || ''}
                      onChange={(e) => updateItem(index, field.key, e.target.value)}
                    />
                  ) : (
                    <input
                      value={item[field.key] || ''}
                      placeholder={field.placeholder || ''}
                      onChange={(e) => updateItem(index, field.key, e.target.value)}
                    />
                  )}
                </div>
              ))}
            </div>
          ))}
          <div className="field-actions">
            <ActionButton onClick={addItem}>Add {title.slice(0, -1)}</ActionButton>
            <ActionButton variant="primary" onClick={handleSave}>Save</ActionButton>
            <ActionButton onClick={() => { setDraft(items || []); setEditing(false) }}>Cancel</ActionButton>
          </div>
        </div>
      ) : (
        <div className="stack-list">
          {(items || []).length === 0 && <p className="empty-note">{emptyLabel}</p>}
          {(items || []).map((item, index) => (
            <div key={index} className="structured-item">
              <div className="structured-title">
                {item.project_name || item.job_title || item.degree || item.school || `Entry ${index + 1}`}
              </div>
              {item.company && <p><strong>Company:</strong> {item.company}</p>}
              {item.school && <p><strong>School:</strong> {item.school}</p>}
              {item.field && <p><strong>Field:</strong> {item.field}</p>}
              {item.duration && <p><strong>Duration:</strong> {item.duration}</p>}
              {item.timeline && <p><strong>Timeline:</strong> {item.timeline}</p>}
              {item.description && <p><strong>Description:</strong> {Array.isArray(item.description) ? item.description.join(' ') : item.description}</p>}
              {item.technologies && <p><strong>Skills used:</strong> {Array.isArray(item.technologies) ? item.technologies.join(', ') : item.technologies}</p>}
              {item.percentage_or_gpa && <p><strong>GPA / Score:</strong> {item.percentage_or_gpa}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ProfilePage({ profile, onDoAnalysis, onUpdateResume, refreshProfile, recommendations = [] }) {
  if (!profile) return <div className="profile-page">No profile found.</div>

  const patch = async (payload) => {
    await patchProfile(profile.id, payload)
    if (refreshProfile) {
      await refreshProfile()
    }
  }

  return (
    <div className="profile-page">
      <div className="profile-shell">
        <div className="profile-hero">
          <div>
            <p className="eyebrow">Career profile</p>
            <h1>{profile.name || 'Your profile'}</h1>
            <p className="subtitle">{profile.current_role || 'Target role not set yet'}</p>
          </div>
          <div className="hero-actions">
            <ActionButton variant="primary" onClick={onDoAnalysis}>Run analysis</ActionButton>
            <ActionButton onClick={onUpdateResume}>Update resume</ActionButton>
          </div>
        </div>

        <div className="profile-grid">
          <div className="main-column">
            <div className="section-card">
              <div className="section-card-head">
                <div>
                  <h3>Basics</h3>
                  <p>Keep the key identity and contact details clean and current.</p>
                </div>
              </div>
              <div className="field-grid">
                <EditableTextField label="Name" value={profile.name} onSave={(value) => patch({ name: value })} placeholder="Your full name" />
                <EditableTextField label="Target role" value={profile.current_role} onSave={(value) => patch({ target_role: value })} placeholder="Backend Engineer" />
                <EditableTextField label="Email" value={profile.email} onSave={(value) => patch({ email: value })} placeholder="you@example.com" />
                <EditableTextField label="Phone" value={profile.phone} onSave={(value) => patch({ phone: value })} placeholder="+91..." />
                <EditableTextField label="Location" value={profile.location} onSave={(value) => patch({ location: value })} placeholder="City, Country" />
              </div>
            </div>

            <div className="section-card">
              <div className="section-card-head">
                <div>
                  <h3>Links</h3>
                  <p>Professional links that usually appear on resumes.</p>
                </div>
              </div>
              <div className="field-grid">
                <EditableTextField
                  label="LinkedIn"
                  value={profile.socials?.linkedin}
                  onSave={(value) => patch({ socials: { ...(profile.socials || {}), linkedin: value } })}
                  placeholder="https://linkedin.com/in/..."
                />
                <EditableTextField
                  label="GitHub"
                  value={profile.socials?.github}
                  onSave={(value) => patch({ socials: { ...(profile.socials || {}), github: value } })}
                  placeholder="https://github.com/..."
                />
                <EditableTextField
                  label="Portfolio"
                  value={profile.socials?.portfolio}
                  onSave={(value) => patch({ socials: { ...(profile.socials || {}), portfolio: value } })}
                  placeholder="https://your-portfolio.com"
                />
              </div>
            </div>

            <EditableSkills skills={profile.current_skills || []} onSave={(value) => patch({ skills: value })} />

            <StructuredListEditor
              title="Experience"
              subtitle="Internships and work history in resume-style structure."
              items={profile.experience || []}
              emptyLabel="No experience added yet."
              onSave={(value) => patch({ experience: value })}
              addTemplate={{ job_title: '', company: '', duration: '', description: '' }}
              fields={[
                { key: 'job_title', label: 'Role title', placeholder: 'Software Engineering Intern' },
                { key: 'company', label: 'Company', placeholder: 'Acme Corp' },
                { key: 'duration', label: 'Duration', placeholder: 'May 2025 - Jul 2025' },
                { key: 'description', label: 'What you did', type: 'textarea', placeholder: 'Built..., improved..., collaborated on...' }
              ]}
            />

            <StructuredListEditor
              title="Projects"
              subtitle="Each project keeps topic, explanation, and skills used."
              items={profile.projects || []}
              emptyLabel="No projects added yet."
              onSave={(value) => patch({ projects: value })}
              addTemplate={{ project_name: '', description: '', technologies: '', duration: '' }}
              fields={[
                { key: 'project_name', label: 'Project topic', placeholder: 'Skill Gap Analyzer' },
                { key: 'description', label: 'Explanation', type: 'textarea', placeholder: 'What the project does and what you built' },
                { key: 'technologies', label: 'Skills / tech used', placeholder: 'React, FastAPI, SQLite' },
                { key: 'duration', label: 'Duration', placeholder: 'Jan 2026 - Feb 2026' }
              ]}
            />

            <StructuredListEditor
              title="Education"
              subtitle="Academic entries in a clear resume structure."
              items={profile.education || []}
              emptyLabel="No education added yet."
              onSave={(value) => patch({ education: value })}
              addTemplate={{ school: '', degree: '', field: '', timeline: '', percentage_or_gpa: '' }}
              fields={[
                { key: 'school', label: 'Institution', placeholder: 'ABC University' },
                { key: 'degree', label: 'Degree', placeholder: 'B.Tech' },
                { key: 'field', label: 'Field', placeholder: 'Computer Science' },
                { key: 'timeline', label: 'Timeline', placeholder: '2022 - 2026' },
                { key: 'percentage_or_gpa', label: 'GPA / score', placeholder: '8.6 CGPA' }
              ]}
            />
          </div>

          <aside className="side-column">
            <div className="section-card accent">
              <div className="section-card-head">
                <div>
                  <h3>Resume status</h3>
                  <p>Resume information is extracted once when you upload or replace the PDF.</p>
                </div>
              </div>
              <div className="status-list">
                <div>
                  <span className="status-label">Last uploaded</span>
                  <strong>{profile.resume_last_updated ? new Date(profile.resume_last_updated).toLocaleString() : 'Not uploaded yet'}</strong>
                </div>
                <div>
                  <span className="status-label">Stored fields</span>
                  <strong>{[
                    profile.email,
                    profile.phone,
                    profile.location,
                    ...(profile.current_skills || []),
                    ...(profile.education || []),
                    ...(profile.experience || []),
                    ...(profile.projects || [])
                  ].filter(Boolean).length}</strong>
                </div>
              </div>
            </div>

            <div className="section-card">
              <div className="section-card-head">
                <div>
                  <h3>Top role matches</h3>
                  <p>Best-fit roles from your saved skill profile.</p>
                </div>
              </div>
              <div className="match-stack">
                {(recommendations || []).slice(0, 3).map((rec) => (
                  <div key={rec.role} className="match-item">
                    <div className="match-head">
                      <strong>{rec.role}</strong>
                      <span>{(rec.score * 100).toFixed(0)}%</span>
                    </div>
                    <p>Strong in {rec.matching_skills.slice(0, 3).join(', ') || 'core areas'}.</p>
                    <p>Needs {rec.missing_skills.slice(0, 3).join(', ') || 'little additional work'}.</p>
                  </div>
                ))}
                {(!recommendations || recommendations.length === 0) && <p className="empty-note">No recommendations yet.</p>}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  )
}
