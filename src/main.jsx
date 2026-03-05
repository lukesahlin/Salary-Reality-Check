import React from 'react'
import ReactDOM from 'react-dom/client'
import { UserProfileProvider } from './hooks/useUserProfile.jsx'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <UserProfileProvider>
      <App />
    </UserProfileProvider>
  </React.StrictMode>
)
