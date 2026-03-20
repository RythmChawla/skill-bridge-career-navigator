import { useEffect, useState } from 'react'
import ResumePage from './pages/ResumePage'
import ResultsPage from './pages/ResultsPage'
import AuthPage from './pages/AuthPage'
import { setAuthToken, getMe, listProfiles, checkHealth, getApiErrorMessage } from './api/client'
import NavBar from './components/NavBar'
import ProfilePage from './pages/ProfilePage'
import ResumeViewer from './pages/ResumeViewer'
import { ToastProvider } from './components/ToastNotification'
import { recommendJobs } from './api/client'
import './App.css'

export default function App() {
  const [currentPage, setCurrentPage] = useState('auth')
  const [profileData, setProfileData] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'))
  const [user, setUser] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [backendError, setBackendError] = useState('')

  useEffect(() => {
    if (token) {
      setAuthToken(token)
      hydrateUserAndProfiles()
    }
  }, [token])

  const hydrateUserAndProfiles = async () => {
    try {
      await checkHealth()
      setBackendError('')
      const meRes = await getMe()
      setUser(meRes.data)
      const profilesRes = await listProfiles()
      if (profilesRes.data && profilesRes.data.length > 0) {
        const first = profilesRes.data[0]
        setProfileData({
          id: first.id,
          name: first.name,
          current_role: first.target_role,
          current_skills: first.skills,
          resume_url: first.resume_path ? `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}/uploads/${first.resume_path}` : null,
          email: first.email,
          phone: first.phone,
          location: first.location,
          socials: first.socials,
          experience: first.experience,
          projects: first.projects,
          education: first.education,
          resume_last_updated: first.resume_last_updated,
        })
        if (first.skills && first.skills.length) {
          try {
            const rec = await recommendJobs(first.skills)
            setRecommendations(rec.data.recommendations || [])
          } catch (e) {
            console.error('Recommendation fetch failed', e)
          }
        }
        setCurrentPage('profile')
        return
      }
      setCurrentPage('resume')
    } catch (err) {
      console.error('Auth hydration failed', err)
      setBackendError(getApiErrorMessage(err, 'Failed to connect to backend'))
      setToken(null)
      setAuthToken(null)
      setCurrentPage('auth')
    }
  }

  const handleStartAnalysis = () => {
    setCurrentPage('resume')
  }

  const handleResumeUploaded = (data) => {
    setProfileData(data)
    setCurrentPage('profile')
  }

  const handleDoAnalysis = () => {
    setCurrentPage('results')
  }

  const handleNewAnalysis = () => {
    setCurrentPage('profile')
  }

  const handleAuthSuccess = (newToken) => {
    setToken(newToken)
  }

  const handleLogout = () => {
    setToken(null)
    setAuthToken(null)
    setUser(null)
    setProfileData(null)
    setRecommendations([])
    setCurrentPage('auth')
  }

  const goEditProfile = () => setCurrentPage('profile')
  const goUpdateResume = () => setCurrentPage('resumeView')
  const refreshProfile = async () => {
    await hydrateUserAndProfiles()
  }

  return (
    <ToastProvider>
      <div className="app">
        {currentPage !== 'auth' && (
          <NavBar
            currentPage={currentPage}
            onNavigate={(view) => setCurrentPage(view)}
            onLogout={handleLogout}
          />
        )}
        <div className="app-body">
          {currentPage === 'auth' && <AuthPage onSuccess={handleAuthSuccess} backendError={backendError} />}
          {currentPage === 'resume' && (
            <ResumePage onComplete={handleResumeUploaded} defaultName={user?.name} />
          )}
          {currentPage === 'profile' && profileData && (
            <ProfilePage
              profile={profileData}
              onDoAnalysis={handleDoAnalysis}
              onEditProfile={goEditProfile}
              onUpdateResume={goUpdateResume}
              refreshProfile={refreshProfile}
              recommendations={recommendations}
            />
          )}
          {currentPage === 'results' && (
            <ResultsPage
              profileData={profileData}
              onNewAnalysis={handleNewAnalysis}
              recommendations={recommendations}
            />
          )}
          {currentPage === 'resumeView' && (
            <ResumeViewer profile={profileData} onUpdateResume={refreshProfile} />
          )}
        </div>
      </div>
    </ToastProvider>
  )
}
