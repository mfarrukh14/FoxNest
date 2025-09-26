import { FiGitCommit, FiUsers, FiFolder, FiArchive, FiTrendingUp, FiActivity, FiWifi, FiWifiOff } from 'react-icons/fi'
import GlassCard from '../components/ui/GlassCard'
import Badge from '../components/ui/Badge'
import { useDashboardStats, useRepositories, useServerHealth } from '../hooks/useApi'
import React from 'react'

const Dashboard = () => {
  const { data: dashboardData, loading: dashboardLoading, error: dashboardError } = useDashboardStats()
  const { data: repositories, loading: reposLoading } = useRepositories()
  const { data: serverHealth } = useServerHealth()

  // Loading state
  if (dashboardLoading) {
    return (
      <div className="space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome to FoxNest</h1>
          <p className="text-white/70">Loading your development activity...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <GlassCard key={i} className="p-6 animate-pulse">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-white/20 rounded-xl mr-4"></div>
                <div className="flex-1">
                  <div className="h-4 bg-white/20 rounded mb-2"></div>
                  <div className="h-6 bg-white/20 rounded"></div>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    )
  }

  // Error state
  if (dashboardError) {
    return (
      <div className="space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome to FoxNest</h1>
          <div className="flex items-center space-x-2">
            <FiWifiOff className="w-5 h-5 text-red-400" />
            <p className="text-red-300">Error connecting to server: {dashboardError}</p>
          </div>
        </div>
      </div>
    )
  }

  const stats = dashboardData?.stats || []
  const iconMap = {
    FiUsers,
    FiFolder,
    FiGitCommit,
    FiArchive
  }

  // Get top repositories (first 3)
  const topRepositories = repositories?.slice(0, 3) || []

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Welcome to FoxNest</h1>
            <p className="text-white/70">Your central hub for managing repositories and tracking development activity.</p>
          </div>
          {/* Server Status */}
          <div className="flex items-center space-x-2">
            {serverHealth?.status === 'connected' ? (
              <>
                <FiWifi className="w-5 h-5 text-green-400" />
                <Badge variant="success">Connected</Badge>
              </>
            ) : (
              <>
                <FiWifiOff className="w-5 h-5 text-red-400" />
                <Badge variant="danger">Disconnected</Badge>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = iconMap[stat.icon] || FiFolder
          return (
            <GlassCard key={stat.name} className="p-6">
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-3 rounded-xl bg-gradient-to-r ${stat.color}`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-white/70">{stat.name}</p>
                  <div className="flex items-baseline">
                    <p className="text-2xl font-semibold text-white">{stat.value}</p>
                    {stat.change !== '+0' && (
                      <span className="ml-2 text-sm font-medium text-green-400">
                        {stat.change}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </GlassCard>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Server Status Card */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <FiActivity className="w-5 h-5 mr-2" />
              Server Status
            </h3>
            <Badge variant={serverHealth?.status === 'connected' ? 'success' : 'danger'}>
              {serverHealth?.status === 'connected' ? 'Online' : 'Offline'}
            </Badge>
          </div>
          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-3 rounded-xl bg-white/5">
              {serverHealth?.status === 'connected' ? (
                <FiWifi className="w-8 h-8 text-green-400" />
              ) : (
                <FiWifiOff className="w-8 h-8 text-red-400" />
              )}
              <div className="flex-1">
                <p className="text-sm text-white">
                  {serverHealth?.status === 'connected' ? 'Connected to FoxNest Server' : 'Unable to connect to server'}
                </p>
                <p className="text-xs text-white/50 mt-1">{serverHealth?.message}</p>
              </div>
            </div>
            {serverHealth?.status !== 'connected' && (
              <div className="text-sm text-orange-300 bg-orange-500/10 p-3 rounded-lg border border-orange-400/20">
                <strong>Note:</strong> Please ensure the FoxNest server is running on localhost:5000
              </div>
            )}
          </div>
        </GlassCard>

        {/* Top Repositories */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <FiTrendingUp className="w-5 h-5 mr-2" />
              Top Repositories
            </h3>
            {reposLoading && <Badge variant="info">Loading...</Badge>}
          </div>
          <div className="space-y-4">
            {topRepositories.length > 0 ? (
              topRepositories.map((repo, index) => (
                <div key={index} className="p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors cursor-pointer">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-white mb-1">{repo.name}</h4>
                      <p className="text-sm text-white/70 mb-2">{repo.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-white/50">
                        <span className="flex items-center">
                          <div className="w-2 h-2 bg-blue-400 rounded-full mr-1"></div>
                          {repo.language}
                        </span>
                        <span>{repo.commits} commits</span>
                        <span>{repo.contributors} contributors</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="success">Active</Badge>
                      <p className="text-xs text-white/50 mt-1">{repo.lastUpdate}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-white/70">
                <FiFolder className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No repositories found</p>
                <p className="text-sm text-white/50 mt-1">
                  {serverHealth?.status !== 'connected' 
                    ? 'Connect to server to view repositories' 
                    : 'Create your first repository to get started'
                  }
                </p>
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  )
}

export default Dashboard
