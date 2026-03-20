import React from 'react'
import './ExportResults.css'

export default function ExportResults({ profileData, analysis }) {
  const exportAsJSON = () => {
    const data = {
      profile: {
        name: profileData.name,
        current_skills: profileData.current_skills,
        email: profileData.email,
        phone: profileData.phone
      },
      analysis: {
        created_at: new Date().toISOString(),
        matching_skills: analysis.matching_skills,
        missing_skills: analysis.missing_skills,
        proficiency: analysis.proficiency,
        job_match_summary: analysis.proficiency >= 80 ? 'Great' : analysis.proficiency >= 60 ? 'Good' : 'Fair'
      }
    }

    const element = document.createElement('a')
    element.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(data, null, 2)))
    element.setAttribute('download', `skill-analysis-${new Date().toISOString().split('T')[0]}.json`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const exportAsCSV = () => {
    let csv = 'Skill Analysis Report\n'
    csv += `Generated: ${new Date().toLocaleString()}\n\n`
    csv += `Name,${profileData.name}\n`
    csv += `Current Skills Count,${profileData.current_skills?.length || 0}\n`
    csv += `Proficiency,${Math.round(analysis.proficiency)}%\n\n`

    csv += 'MATCHING SKILLS\n'
    csv += 'Skill\n'
    analysis.matching_skills.forEach(skill => {
      csv += `${skill}\n`
    })
    csv += '\n'

    csv += 'MISSING SKILLS\n'
    csv += 'Skill\n'
    analysis.missing_skills.forEach(skill => {
      csv += `${skill}\n`
    })

    const element = document.createElement('a')
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv))
    element.setAttribute('download', `skill-analysis-${new Date().toISOString().split('T')[0]}.csv`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const printResults = () => {
    window.print()
  }

  const shareResults = async () => {
    const text = `Check out my skill gap analysis for ${profileData.name}! I have ${Math.round(analysis.proficiency)}% proficiency for this role. Try Skill-Bridge to get your personalized analysis!`
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Skill-Bridge Analysis',
          text: text,
          url: window.location.href
        })
      } catch (err) {
        console.log('Share cancelled')
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(text)
      alert('Results copied to clipboard!')
    }
  }

  return (
    <div className="export-results">
      <h3>📥 Export Your Results</h3>
      <p className="export-subtitle">Download or share your skill analysis report</p>
      
      <div className="export-buttons">
        <button className="export-btn json-btn" onClick={exportAsJSON} title="Download as JSON">
          <span className="icon">📄</span>
          <span className="label">JSON</span>
        </button>
        <button className="export-btn csv-btn" onClick={exportAsCSV} title="Download as CSV">
          <span className="icon">📊</span>
          <span className="label">CSV</span>
        </button>
        <button className="export-btn print-btn" onClick={printResults} title="Print results">
          <span className="icon">🖨️</span>
          <span className="label">Print</span>
        </button>
        <button className="export-btn share-btn" onClick={shareResults} title="Share results">
          <span className="icon">🔗</span>
          <span className="label">Share</span>
        </button>
      </div>
    </div>
  )
}
