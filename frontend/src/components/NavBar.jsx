import './NavBar.css'

export default function NavBar({ currentPage, onNavigate, onLogout }) {
  const isActive = (page) => currentPage === page ? 'active' : ''

  return (
    <div className="nav-bar">
      <div className="nav-left">
        <span className="nav-logo">🎯 Skill-Bridge</span>
      </div>
      <div className="nav-links">
        <button 
          className={`nav-btn ${isActive('profile')}`}
          onClick={() => onNavigate('profile')}
        >
          👤 Profile
        </button>
        <button 
          className={`nav-btn ${isActive('resumeView')}`}
          onClick={() => onNavigate('resumeView')}
        >
          📄 Resume
        </button>
        <button 
          className={`nav-btn ${isActive('results')}`}
          onClick={() => onNavigate('results')}
        >
          📊 Analysis
        </button>
      </div>
      <div className="nav-right">
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </div>
    </div>
  )
}
