import axios from 'axios'
import { API_BASE_URL } from './constants'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ---- Auth helpers ----
export const setAuthToken = (token) => {
  if (token) {
    client.defaults.headers.common['Authorization'] = `Bearer ${token}`
    localStorage.setItem('auth_token', token)
  } else {
    delete client.defaults.headers.common['Authorization']
    localStorage.removeItem('auth_token')
  }
}

const storedToken = localStorage.getItem('auth_token')
if (storedToken) {
  setAuthToken(storedToken)
}

export const signup = (data) => {
  return client.post('/auth/signup', {
    email: data.email,
    password: data.password,
    name: data.name || ''
  })
}

export const login = async (data) => {
  const form = new URLSearchParams()
  form.append('username', data.email)
  form.append('password', data.password)
  form.append('grant_type', 'password')
  const res = await axios.post(`${API_BASE_URL}/auth/login`, form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  return res
}

export const getMe = () => client.get('/auth/me')
export const checkHealth = () => client.get('/health')

// Profiles (list for current user)
// Use trailing slash to avoid 307 redirect that can drop CORS headers
export const listProfiles = () => client.get('/profile/')

// ---- Profile endpoints ----
export const createProfile = (data) => {
  const formData = new FormData()
  formData.append('name', data.name)
  formData.append('target_role', data.target_role || data.current_role)
  if (data.resume) {
    formData.append('resume', data.resume)
  }
  if (data.current_skills && data.current_skills.length > 0) {
    // Send skills as comma-separated string, not JSON
    formData.append('skills', data.current_skills.join(','))
  }
  return client.post('/profile', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getProfile = (profileId) => {
  return client.get(`/profile/${profileId}`)
}

export const updateProfile = (profileId, data) => {
  return client.put(`/profile/${profileId}`, data)
}

export const patchProfile = (profileId, data) => {
  return client.patch(`/profile/${profileId}`, data)
}

export const replaceResume = (profileId, file) => {
  const form = file instanceof FormData ? file : new FormData()
  if (!(file instanceof FormData)) {
    form.append('resume', file)
  }
  return client.post(`/profile/${profileId}/resume`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// Resume upload
export const uploadResume = (formData) => {
  return client.post('/profile/resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// Job endpoints
export const getJobs = () => {
  return client.get('/jobs')
}

export const getJobById = (jobId) => {
  return client.get(`/jobs/${jobId}`)
}

// Analysis endpoints
export const analyzeSkillGap = (data) => {
  const skills =
    data.user_skills !== undefined
      ? data.user_skills
      : data.current_skills || []

  return client.post('/analyze/gap', {
    job_role: data.job_role,
    user_skills: skills,
    user_name: data.user_name || 'User'
  })
}

export const recommendJobs = (skills) =>
  client.post('/jobs/recommend', { user_skills: skills || [] })

export const generateFeedback = (data) => {
  return client.post('/analyze/feedback', data)
}

export const generateRoadmap = (data) => {
  return client.post('/analyze/roadmap', data)
}

// On-demand endpoints (triggered by buttons)
export const generateFeedbackOnly = (data) => {
  const skills =
    data.user_skills !== undefined
      ? data.user_skills
      : data.current_skills || []

  return client.post('/analyze/feedback-only', {
    job_role: data.job_role,
    user_skills: skills,
    user_name: data.user_name || 'User'
  })
}

export const generateRoadmapOnly = (data) => {
  const skills =
    data.user_skills !== undefined
      ? data.user_skills
      : data.current_skills || []

  return client.post('/analyze/roadmap-only', {
    job_role: data.job_role,
    user_skills: skills,
    user_name: data.user_name || 'User'
  })
}

// Error handling
client.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      console.error('Unauthorized')
      // clear bad token so app can re-auth
      setAuthToken(null)
    }
    return Promise.reject(error)
  }
)

export const getApiErrorMessage = (error, fallback = 'Request failed') => {
  if (!error.response) {
    return 'Backend is not running. Start the API server on http://127.0.0.1:8000 and try again.'
  }
  return error.response?.data?.detail || error.message || fallback
}

export default client
