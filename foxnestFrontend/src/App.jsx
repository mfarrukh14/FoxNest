import React,{ useState } from 'react'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import UsersManagement from './pages/UsersManagement'
import Repositories from './pages/Repositories'
import Archive from './pages/Archive'
import PendingApprovals from './pages/PendingApprovals'
import PendingRepositories from './pages/PendingRepositories'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'users-management':
        return <UsersManagement />
      case 'repositories':
        return <Repositories />
      case 'pending-approvals':
        return <PendingApprovals />
      case 'pending-repositories':
        return <PendingRepositories />
      case 'archive':
        return <Archive />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800">
      {/* Professional gradient background with subtle animated elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -inset-10 opacity-30">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-blue-900 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob"></div>
          <div className="absolute top-0 -right-4 w-72 h-72 bg-slate-700 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-gray-800 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob animation-delay-4000"></div>
        </div>
      </div>

      <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
        {renderContent()}
      </Layout>
    </div>
  )
}

export default App
