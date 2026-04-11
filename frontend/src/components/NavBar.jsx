import { useEffect, useState } from 'react'
import './NavBar.css'

export default function NavBar({ currentPage, onNavigate, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const isActive = (page) => currentPage === page ? 'active' : ''

  const handleNavigate = (page) => {
    onNavigate(page)
    setMenuOpen(false)
  }

  const handleLogout = () => {
    setMenuOpen(false)
    onLogout()
  }

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 900) {
        setMenuOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className={`nav-bar ${menuOpen ? 'menu-open' : ''}`}>
      <div className="nav-left">
        <span className="nav-logo">Skill-Bridge</span>
      </div>

      <button
        type="button"
        className={`nav-toggle ${menuOpen ? 'open' : ''}`}
        aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <div className="nav-links">
        <button
          className={`nav-btn ${isActive('profile')}`}
          onClick={() => handleNavigate('profile')}
        >
          Profile
        </button>
        <button
          className={`nav-btn ${isActive('resumeView')}`}
          onClick={() => handleNavigate('resumeView')}
        >
          Resume
        </button>
        <button
          className={`nav-btn ${isActive('results')}`}
          onClick={() => handleNavigate('results')}
        >
          Analysis
        </button>
      </div>

      <div className="nav-right">
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </div>
    </div>
  )
}
