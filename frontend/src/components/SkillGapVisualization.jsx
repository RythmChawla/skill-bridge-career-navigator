import './SkillGapVisualization.css'

export default function SkillGapVisualization({ analysis, jobTitle }) {
  if (!analysis) return null

  return (
    <div className="skill-gap-section">
      <h2>🎯 Skills Comparison for {jobTitle}</h2>

      <div className="skills-grid">
        {/* You Have - Matching Skills */}
        <div className="skills-box matching">
          <div className="skills-header">
            <h3>✅ You Have ({analysis.matching_skills_count})</h3>
            <span className="skill-count">{analysis.current_skills_count} total skills</span>
          </div>
          <div className="skills-list">
            {analysis.matching_skills.length > 0 ? (
              analysis.matching_skills.map((skill, idx) => (
                <div key={idx} className="skill-badge matching-badge">
                  {skill}
                </div>
              ))
            ) : (
              <p className="no-skills">No matching skills yet</p>
            )}
          </div>
        </div>

        {/* You Need - Missing Skills */}
        <div className="skills-box missing">
          <div className="skills-header">
            <h3>📚 You Need to Learn ({analysis.missing_skills.length})</h3>
            <span className="skill-count">{analysis.required_skills_count} required skills</span>
          </div>
          <div className="skills-list">
            {analysis.missing_skills.length > 0 ? (
              analysis.missing_skills.map((skill, idx) => (
                <div key={idx} className="skill-badge missing-badge">
                  {skill}
                </div>
              ))
            ) : (
              <p className="no-skills">Perfect! You have all required skills</p>
            )}
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="summary-stats">
        <div className="stat-card">
          <div className="stat-label">Current Skills</div>
          <div className="stat-value">{analysis.current_skills_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Skills to Learn</div>
          <div className="stat-value">{analysis.missing_skills.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Proficiency</div>
          <div className="stat-value">{analysis.proficiency}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Job Match</div>
          <div className="stat-value">
            {analysis.proficiency >= 80 ? '🟢 Great' : 
             analysis.proficiency >= 60 ? '🟡 Good' : 
             analysis.proficiency >= 40 ? '🟠 Fair' : 
             '🔴 Room to Grow'}
          </div>
        </div>
      </div>
    </div>
  )
}
