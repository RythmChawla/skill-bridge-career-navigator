import { useState } from 'react'
import './SkillInput.css'

export default function SkillInput({ onAdd, skills, onRemove }) {
  const [input, setInput] = useState('')

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && input.trim()) {
      e.preventDefault()
      onAdd(input.trim())
      setInput('')
    }
  }

  const handleAdd = () => {
    if (input.trim()) {
      onAdd(input.trim())
      setInput('')
    }
  }

  return (
    <div className="skill-input-container">
      <div className="input-wrapper">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="e.g., Python, React... (press Enter)"
        />
        <button onClick={handleAdd} type="button" className="add-btn">
          +
        </button>
      </div>

      {skills.length > 0 && (
        <div className="skills-list">
          {skills.map(skill => (
            <div key={skill} className="skill-tag">
              <span>{skill}</span>
              <button
                onClick={() => onRemove(skill)}
                type="button"
                className="remove-btn"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
