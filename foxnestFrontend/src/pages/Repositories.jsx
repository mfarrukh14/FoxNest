import React,{ useState } from 'react'
import { FiFolder, FiGitCommit, FiUsers, FiStar, FiEye, FiGitBranch, FiClock, FiArchive, FiEdit3, FiTrash2, FiWifi, FiWifiOff } from 'react-icons/fi'
import GlassCard from '../components/ui/GlassCard'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import { useRepositories, useServerHealth } from '../hooks/useApi'

const Repositories = () => {
  const [selectedRepo, setSelectedRepo] = useState(null)
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'

  const repositories = [
    {
      id: 1,
      name: 'react-dashboard',
      description: 'Modern React dashboard with TypeScript and advanced data visualization components',
      language: 'TypeScript',
      languageColor: '#3178c6',
      commits: 156,
      contributors: 4,
      stars: 23,
      watchers: 8,
      branches: 6,
      size: '2.4 MB',
      lastUpdate: '2 hours ago',
      status: 'active',
      visibility: 'public',
      tags: ['react', 'typescript', 'dashboard'],
      files: [
        { name: 'src/components', type: 'folder', files: 12 },
        { name: 'src/pages', type: 'folder', files: 8 },
        { name: 'src/utils', type: 'folder', files: 5 },
        { name: 'package.json', type: 'file', size: '2.1 KB' },
        { name: 'README.md', type: 'file', size: '3.4 KB' },
        { name: 'tsconfig.json', type: 'file', size: '1.2 KB' }
      ]
    },
    {
      id: 2,
      name: 'api-server',
      description: 'RESTful API server built with Node.js and Express, featuring authentication and database integration',
      language: 'JavaScript',
      languageColor: '#f1e05a',
      commits: 89,
      contributors: 3,
      stars: 15,
      watchers: 5,
      branches: 4,
      size: '1.8 MB',
      lastUpdate: '1 day ago',
      status: 'active',
      visibility: 'private',
      tags: ['nodejs', 'express', 'api'],
      files: [
        { name: 'src/routes', type: 'folder', files: 8 },
        { name: 'src/models', type: 'folder', files: 5 },
        { name: 'src/middleware', type: 'folder', files: 3 },
        { name: 'server.js', type: 'file', size: '1.5 KB' },
        { name: 'package.json', type: 'file', size: '1.8 KB' }
      ]
    },
    {
      id: 3,
      name: 'mobile-app',
      description: 'Cross-platform mobile application built with React Native',
      language: 'React Native',
      languageColor: '#61dafb',
      commits: 67,
      contributors: 2,
      stars: 8,
      watchers: 3,
      branches: 3,
      size: '3.2 MB',
      lastUpdate: '3 days ago',
      status: 'active',
      visibility: 'public',
      tags: ['react-native', 'mobile'],
      files: [
        { name: 'src/screens', type: 'folder', files: 10 },
        { name: 'src/components', type: 'folder', files: 15 },
        { name: 'App.js', type: 'file', size: '2.1 KB' }
      ]
    },
    {
      id: 4,
      name: 'legacy-system',
      description: 'Legacy system components and utilities - no longer actively maintained',
      language: 'Python',
      languageColor: '#3572A5',
      commits: 234,
      contributors: 6,
      stars: 45,
      watchers: 12,
      branches: 8,
      size: '5.6 MB',
      lastUpdate: '6 months ago',
      status: 'archived',
      visibility: 'public',
      tags: ['python', 'legacy'],
      files: []
    }
  ]

  const handleArchive = (repoId) => {
    // Handle archiving logic here
    console.log('Archiving repository:', repoId)
  }

  const handleRepoClick = (repo) => {
    setSelectedRepo(selectedRepo?.id === repo.id ? null : repo)
  }

  const filteredRepos = repositories.filter(repo => repo.status === 'active')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Repositories</h1>
          <p className="text-white/70">Browse and manage all your repositories</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="secondary" size="sm">
            <FiFolder className="w-4 h-4 mr-2" />
            New Repository
          </Button>
          <div className="flex items-center space-x-1 bg-white/10 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded text-sm transition-colors ${
                viewMode === 'grid' ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded text-sm transition-colors ${
                viewMode === 'list' ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white'
              }`}
            >
              List
            </button>
          </div>
        </div>
      </div>

      {/* Repository Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard className="p-4">
          <div className="flex items-center">
            <FiFolder className="w-8 h-8 text-blue-400 mr-3" />
            <div>
              <p className="text-2xl font-semibold text-white">{filteredRepos.length}</p>
              <p className="text-sm text-white/70">Active Repos</p>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4">
          <div className="flex items-center">
            <FiGitCommit className="w-8 h-8 text-green-400 mr-3" />
            <div>
              <p className="text-2xl font-semibold text-white">
                {repositories.reduce((sum, repo) => sum + repo.commits, 0)}
              </p>
              <p className="text-sm text-white/70">Total Commits</p>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4">
          <div className="flex items-center">
            <FiUsers className="w-8 h-8 text-purple-400 mr-3" />
            <div>
              <p className="text-2xl font-semibold text-white">
                {Math.max(...repositories.map(repo => repo.contributors))}
              </p>
              <p className="text-sm text-white/70">Max Contributors</p>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4">
          <div className="flex items-center">
            <FiStar className="w-8 h-8 text-yellow-400 mr-3" />
            <div>
              <p className="text-2xl font-semibold text-white">
                {repositories.reduce((sum, repo) => sum + repo.stars, 0)}
              </p>
              <p className="text-sm text-white/70">Total Stars</p>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Repositories Grid/List */}
      <div className={viewMode === 'grid' ? 'grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6' : 'space-y-4'}>
        {filteredRepos.map((repo) => (
          <GlassCard
            key={repo.id}
            className={`p-6 cursor-pointer transition-all duration-300 ${
              selectedRepo?.id === repo.id ? 'ring-2 ring-purple-400 bg-white/15' : ''
            }`}
            onClick={() => handleRepoClick(repo)}
          >
            {/* Repository Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="font-semibold text-white truncate">{repo.name}</h3>
                  <Badge variant={repo.visibility === 'public' ? 'success' : 'warning'}>
                    {repo.visibility}
                  </Badge>
                </div>
                <p className="text-sm text-white/70 line-clamp-2">{repo.description}</p>
              </div>
              <div className="flex items-center space-x-1 ml-4">
                <Button variant="ghost" size="sm" onClick={(e) => {
                  e.stopPropagation()
                  // Handle edit
                }}>
                  <FiEdit3 className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" onClick={(e) => {
                  e.stopPropagation()
                  handleArchive(repo.id)
                }}>
                  <FiArchive className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Language and Tags */}
            <div className="flex items-center space-x-2 mb-4">
              <div className="flex items-center space-x-1">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: repo.languageColor }}
                ></div>
                <span className="text-sm text-white/70">{repo.language}</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {repo.tags.slice(0, 2).map((tag, index) => (
                  <Badge key={index} variant="default" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Repository Stats */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="flex items-center space-x-2 text-sm text-white/70">
                <FiGitCommit className="w-4 h-4" />
                <span>{repo.commits}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-white/70">
                <FiUsers className="w-4 h-4" />
                <span>{repo.contributors}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-white/70">
                <FiStar className="w-4 h-4" />
                <span>{repo.stars}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-white/70">
                <FiGitBranch className="w-4 h-4" />
                <span>{repo.branches}</span>
              </div>
            </div>

            {/* Last Update */}
            <div className="flex items-center justify-between text-xs text-white/50">
              <div className="flex items-center space-x-1">
                <FiClock className="w-3 h-3" />
                <span>Updated {repo.lastUpdate}</span>
              </div>
              <span>{repo.size}</span>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Repository Details Modal */}
      {selectedRepo && (
        <GlassCard className="p-6 mt-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white flex items-center">
              <FiFolder className="w-5 h-5 mr-2" />
              {selectedRepo.name}
            </h2>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setSelectedRepo(null)}
            >
              Close
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Repository Info */}
            <div>
              <h3 className="text-lg font-medium text-white mb-4">Repository Information</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-white/70">Language:</span>
                  <div className="flex items-center space-x-1">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: selectedRepo.languageColor }}
                    ></div>
                    <span className="text-white">{selectedRepo.language}</span>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Size:</span>
                  <span className="text-white">{selectedRepo.size}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Visibility:</span>
                  <Badge variant={selectedRepo.visibility === 'public' ? 'success' : 'warning'}>
                    {selectedRepo.visibility}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70">Last Update:</span>
                  <span className="text-white">{selectedRepo.lastUpdate}</span>
                </div>
              </div>
            </div>

            {/* Files Structure */}
            <div>
              <h3 className="text-lg font-medium text-white mb-4">Files & Folders</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {selectedRepo.files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-white/10 hover:bg-white/15 transition-colors">
                    <div className="flex items-center space-x-2">
                      {file.type === 'folder' ? (
                        <FiFolder className="w-4 h-4 text-blue-400" />
                      ) : (
                        <div className="w-4 h-4 bg-white/30 rounded"></div>
                      )}
                      <span className="text-white text-sm">{file.name}</span>
                    </div>
                    <span className="text-white/50 text-xs">
                      {file.type === 'folder' ? `${file.files} files` : file.size}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  )
}

export default Repositories
