import { useEffect, useState } from 'react'
import { analyzeSkillGap, getJobs, recommendJobs, generateFeedbackOnly, generateRoadmapOnly } from '../api/client'
import { useToast } from '../components/ToastNotification'
import SkillGapVisualization from '../components/SkillGapVisualization'
import ExportResults from '../components/ExportResults'
import './ResultsPage.css'

export default function ResultsPage({ profileData, onNewAnalysis, recommendations: initialRecs }) {
  const toast = useToast()
  const [analysis, setAnalysis] = useState(null)
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [recommendations, setRecommendations] = useState(initialRecs || [])
  
  // New state for on-demand feedback and roadmap
  const [feedback, setFeedback] = useState(null)
  const [roadmap, setRoadmap] = useState(null)
  const [feedbackLoading, setFeedbackLoading] = useState(false)
  const [roadmapLoading, setRoadmapLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Get available jobs
      const jobsRes = await getJobs()
      setJobs(jobsRes.data)
      
      if (jobsRes.data.length > 0) {
        const firstJob = jobsRes.data[0]
        setSelectedJob(firstJob)
        await analyzeGap(firstJob)
        // recommendations based on user skills
        fetchRecommendations()
      }
    } catch (err) {
      setError('Failed to load data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const analyzeGap = async (job) => {
    try {
      setLoading(true)
      setError(null)
      const res = await analyzeSkillGap({
        job_role: job.title,
        user_skills: profileData.current_skills || [],
        user_name: profileData.name
      })

      setAnalysis(res.data)
      setFeedback(null)
      setRoadmap(null)
      toast.info('Skill analysis updated')
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to analyze skills'
      setError(errorMsg)
      toast.error(errorMsg)
      console.error('Analysis error:', errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleJobChange = (job) => {
    setSelectedJob(job)
    analyzeGap(job)
  }

  const fetchRecommendations = async () => {
    try {
      if (!profileData?.current_skills) return
      const res = await recommendJobs(profileData.current_skills)
      setRecommendations(res.data.recommendations || [])
    } catch (err) {
      console.error('Recommendation error', err)
    }
  }

  // Generate feedback on-demand
  const handleGenerateFeedback = async () => {
    try {
      setFeedbackLoading(true)
      toast.info('Generating personalized feedback...')
      const res = await generateFeedbackOnly({
        job_role: selectedJob.title,
        current_skills: profileData.current_skills || [],
        user_name: profileData.name
      })
      setFeedback(res.data)
      toast.success('Feedback generated successfully!')
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to generate feedback'
      toast.error(errorMsg)
      console.error('Feedback error:', err)
    } finally {
      setFeedbackLoading(false)
    }
  }

  // Generate roadmap on-demand
  const handleGenerateRoadmap = async () => {
    try {
      setRoadmapLoading(true)
      toast.info('Generating learning roadmap...')
      const res = await generateRoadmapOnly({
        job_role: selectedJob.title,
        current_skills: profileData.current_skills || [],
        user_name: profileData.name
      })
      setRoadmap(res.data)
      toast.success('Roadmap generated successfully!')
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to generate roadmap'
      toast.error(errorMsg)
      console.error('Roadmap error:', err)
    } finally {
      setRoadmapLoading(false)
    }
  }

  if (error) {
    return (
      <div className="results-page">
        <div className="error-box">
          <h2>⚠️ Error</h2>
          <p>{error}</p>
          <button onClick={onNewAnalysis} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="results-page">
      <div className="results-container">
        <h1>📊 Your Skill Gap Analysis</h1>
        <p className="profile-info">
          Profile: <strong>{profileData.name}</strong> | Target Role: <strong>{selectedJob?.title || 'Select a role'}</strong>
        </p>

        {recommendations.length > 0 && (
          <div className="recommend-card">
            <div className="card-head">
              <h3>Top Matches for You</h3>
              <span className="hint">Based on your current skills</span>
            </div>
            <div className="topmatch-grid">
              {recommendations.slice(0, 3).map((rec) => (
                <div key={rec.role} className="topmatch-card">
                  <div className="topmatch-row">
                    <span className="topmatch-role">{rec.role}</span>
                    <span className="topmatch-badge">{(rec.score * 100).toFixed(0)}% match</span>
                  </div>
                  <div className="topmatch-sub">
                    <span>Have: {rec.matching_skills.length}</span>
                    <span>Need: {rec.missing_skills.length}</span>
                  </div>
                  <div className="topmatch-skills">
                    <p>Strong: {rec.matching_skills.join(', ') || '—'}</p>
                    <p>Gap: {rec.missing_skills.join(', ') || '—'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {jobs.length > 0 && (
          <div className="job-selector">
            <label>Change Target Role:</label>
            <select 
              value={selectedJob?.id || ''} 
              onChange={(e) => handleJobChange(jobs.find(j => j.id == e.target.value))}
            >
              {jobs.map(job => (
                <option key={job.id} value={job.id}>{job.title}</option>
              ))}
            </select>
          </div>
        )}

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Analyzing your skills...</p>
          </div>
        ) : analysis ? (
          <div className="results-content">
            {/* Skill Gap Visualization */}
            <SkillGapVisualization 
              analysis={analysis}
              jobTitle={selectedJob?.title}
            />

            {/* AI Feedback Section */}
            <div className="ai-feedback-section">
              <h3>🤖 Personalized Feedback</h3>
              <p className="section-hint">Get motivating insights about your strengths and learning priorities</p>
              {feedbackLoading ? (
                <div className="loading-small">
                  <div className="spinner-small"></div>
                  <p>Generating personalized feedback...</p>
                </div>
              ) : feedback ? (
                <div className="feedback-box">
                  <p className="feedback-text">"{feedback.feedback}"</p>
                  <div className="feedback-stats">
                    <span>Proficiency: {feedback.proficiency.toFixed(1)}%</span>
                    <span>Matching: {feedback.matching_skills.length} skills</span>
                    <span>Missing: {feedback.missing_skills.length} skills</span>
                  </div>
                </div>
              ) : (
                <button 
                  onClick={handleGenerateFeedback} 
                  className="generate-btn feedback-btn"
                  disabled={feedbackLoading}
                >
                  ✨ Generate Feedback
                </button>
              )}
            </div>

            {/* Learning Roadmap Section */}
            <div className="roadmap-section">
              <h3>🗺️ Your Learning Roadmap</h3>
              <p className="section-hint">Progressive learning path from what you know to your goal</p>
              {roadmapLoading ? (
                <div className="loading-small">
                  <div className="spinner-small"></div>
                  <p>Creating your personalized roadmap...</p>
                </div>
              ) : roadmap ? (
                <div className="roadmap-box">
                  <p className="roadmap-start">Starting from: <strong>{roadmap.current_skills.join(', ')}</strong></p>
                  <div className="roadmap-steps">
                    {roadmap.roadmap.map((step, idx) => (
                      <div key={idx} className="roadmap-step">
                        <div className="step-header">
                          <span className="step-number">Step {step.step}</span>
                          <h4>{step.title}</h4>
                          {step.timeframe && <span className="timeframe">⏱️ {step.timeframe}</span>}
                        </div>
                        <div className="step-details">
                          {step.goal && <p><strong>Goal:</strong> {step.goal}</p>}
                          {step.why_this_now && <p><strong>Why this now:</strong> {step.why_this_now}</p>}
                          {step.what && <p><strong>What:</strong> {step.what}</p>}
                          {step.how && <p><strong>How:</strong> {step.how}</p>}
                          {step.practice && <p><strong>Practice:</strong> {step.practice}</p>}
                          {step.what_to_learn && Array.isArray(step.what_to_learn) && (
                            <p><strong>What to learn:</strong> {step.what_to_learn.join(', ')}</p>
                          )}
                          {step.teacher_explanation && <p><strong>Teacher note:</strong> {step.teacher_explanation}</p>}
                          {step.practice_tasks && Array.isArray(step.practice_tasks) && (
                            <p><strong>Practice tasks:</strong> {step.practice_tasks.join(' | ')}</p>
                          )}
                          {step.success_signal && <p><strong>Success signal:</strong> {step.success_signal}</p>}
                          {step.resources && Array.isArray(step.resources) && step.resources.length > 0 && (
                            <div className="resource-list">
                              <strong>Resources:</strong>
                              <ul>
                                {step.resources.map((resource, resourceIndex) => (
                                  <li key={resourceIndex}>
                                    {resource.url ? (
                                      <a href={resource.url} target="_blank" rel="noreferrer">
                                        {resource.name || resource.url}
                                      </a>
                                    ) : (
                                      <span>{resource.name}</span>
                                    )}
                                    {resource.type ? ` (${resource.type})` : ''}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {step.description && <p>{step.description}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <button 
                  onClick={handleGenerateRoadmap} 
                  className="generate-btn roadmap-btn"
                  disabled={roadmapLoading}
                >
                  📚 Generate Roadmap
                </button>
              )}
            </div>

            {/* Export Results */}
            {analysis && (
              <ExportResults
                profileData={profileData}
                analysis={analysis}
              />
            )}

            {/* Action Button */}
            <button onClick={onNewAnalysis} className="new-analysis-btn">
              ← Start New Analysis
            </button>
          </div>
        ) : (
          <div className="empty-state">
            <p>No analysis available</p>
            <button onClick={onNewAnalysis} className="new-analysis-btn">
              Start Over
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
