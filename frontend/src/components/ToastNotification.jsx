import React, { useContext, createContext, useState, useCallback } from 'react'
import './ToastNotification.css'

// Context for toast notifications
const ToastContext = createContext()

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now()
    // Convert non-string messages to strings
    let displayMessage = message
    if (typeof message !== 'string') {
      if (Array.isArray(message)) {
        // If it's an array of error objects, extract the message field
        displayMessage = message
          .map(err => typeof err === 'string' ? err : (err.msg || err.message || JSON.stringify(err)))
          .join('; ')
      } else if (typeof message === 'object') {
        // If it's an error object, try to extract a message
        displayMessage = message.msg || message.message || message.detail || JSON.stringify(message)
      } else {
        displayMessage = String(message)
      }
    }
    const toast = { id, message: displayMessage, type }
    
    setToasts(prev => [...prev, toast])
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const success = useCallback((message, duration) => addToast(message, 'success', duration), [addToast])
  const error = useCallback((message, duration) => addToast(message, 'error', duration || 5000), [addToast])
  const warning = useCallback((message, duration) => addToast(message, 'warning', duration || 4000), [addToast])
  const info = useCallback((message, duration) => addToast(message, 'info', duration), [addToast])

  return (
    <ToastContext.Provider value={{ addToast, removeToast, success, error, warning, info }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

function ToastContainer({ toasts, onRemove }) {
  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={() => onRemove(toast.id)}
        />
      ))}
    </div>
  )
}

function Toast({ id, message, type, onClose }) {
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  }

  return (
    <div className={`toast toast-${type}`}>
      <span className="toast-icon">{icons[type]}</span>
      <span className="toast-message">{message}</span>
      <button className="toast-close" onClick={onClose}>
        ×
      </button>
    </div>
  )
}
