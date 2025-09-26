const API_BASE_URL = 'http://192.168.15.237:5000/api'

class FoxNestAPI {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Network error' }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error(`API Request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Repository endpoints
  async createRepository(username, repoName) {
    return this.request('/repository/create', {
      method: 'POST',
      body: { username, repo_name: repoName },
    })
  }

  async listRepositories(username, repoName = null) {
    const params = new URLSearchParams({ username })
    if (repoName) params.append('repo_name', repoName)
    
    return this.request(`/repository/list?${params}`)
  }

  async listAllRepositories() {
    return this.request('/repositories/all')
  }

  async getRepository(repoId) {
    return this.request(`/repository/${repoId}`)
  }

  async getCommits(repoId, full = false) {
    return this.request(`/repository/${repoId}/commits?full=${full}`)
  }

  async pushCommit(repoId, commit) {
    return this.request(`/repository/${repoId}/push`, {
      method: 'POST',
      body: { commit },
    })
  }

  async pullCommits(repoId, sinceCommit = null) {
    const params = sinceCommit ? `?since_commit=${sinceCommit}` : ''
    return this.request(`/repository/${repoId}/pull${params}`)
  }

  // Health check
  async healthCheck() {
    return this.request('/', { method: 'GET' })
  }

  // Helper methods for data transformation
  transformRepositoryData(repositories) {
    return repositories.map(repo => ({
      id: repo.id,
      name: repo.name,
      description: `Repository owned by ${repo.owner}`,
      language: 'Unknown', // You might want to detect this from files
      languageColor: '#6c757d',
      commits: repo.commits?.length || 0,
      contributors: 1, // For now, just the owner
      stars: 0, // Not implemented in server yet
      watchers: 0, // Not implemented in server yet
      branches: 1, // Not implemented in server yet
      size: '0 KB', // Calculate from actual data
      lastUpdate: this.formatDate(repo.created_at),
      status: 'active',
      visibility: 'public', // Default for now
      tags: [],
      owner: repo.owner,
      createdAt: repo.created_at,
      head: repo.head
    }))
  }

  transformCommitData(commits) {
    return commits.map(commit => ({
      id: commit.id,
      message: commit.message,
      author: commit.author,
      timestamp: commit.timestamp,
      parent: commit.parent,
      files: Array.isArray(commit.files) ? commit.files : Object.keys(commit.files || {})
    }))
  }

  formatDate(dateString) {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 1) return 'just now'
    if (diffHours < 24) return `${diffHours} hours ago`
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return date.toLocaleDateString()
  }

  // Get user statistics
  async getUserStats(username) {
    try {
      const reposResponse = await this.listRepositories(username)
      const repositories = reposResponse.repositories || []
      
      let totalCommits = 0
      const repoDetails = []

      for (const repo of repositories) {
        try {
          const commitsResponse = await this.getCommits(repo.id, false)
          const commits = commitsResponse.commits || []
          totalCommits += commits.length
          
          repoDetails.push({
            name: repo.name,
            commits: commits.length,
            lastCommit: commits.length > 0 ? this.formatDate(commits[0].timestamp) : 'No commits',
            language: 'Unknown' // You might want to detect this
          })
        } catch (error) {
          console.error(`Error fetching commits for repo ${repo.id}:`, error)
        }
      }

      return {
        totalCommits,
        activeRepos: repositories.length,
        repositories: repoDetails
      }
    } catch (error) {
      console.error('Error fetching user stats:', error)
      return {
        totalCommits: 0,
        activeRepos: 0,
        repositories: []
      }
    }
  }

  // Get dashboard statistics
  async getDashboardStats() {
    try {
      // For now, we'll need to aggregate data from all repositories
      // This is a simplified version - in a real app, you'd have dedicated endpoints
      const allUsers = ['john_doe', 'jane_smith', 'mike_wilson', 'sarah_connor'] // You'd get this from a users endpoint
      
      let totalUsers = allUsers.length
      let totalRepos = 0
      let totalCommits = 0
      let recentActivity = []

      for (const username of allUsers) {
        try {
          const userStats = await this.getUserStats(username)
          totalRepos += userStats.activeRepos
          totalCommits += userStats.totalCommits
        } catch (error) {
          console.error(`Error fetching stats for user ${username}:`, error)
        }
      }

      return {
        totalUsers,
        totalRepos,
        totalCommits,
        archivedProjects: 0, // Not implemented yet
        recentActivity // You'd implement this based on recent commits
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
      return {
        totalUsers: 0,
        totalRepos: 0,
        totalCommits: 0,
        archivedProjects: 0,
        recentActivity: []
      }
    }
  }

  // Update repository details (G1 coordinator, tested status)
  async updateRepositoryDetails(repoId, details) {
    try {
      const response = await this.request(`/repository/${repoId}/details`, {
        method: 'PUT',
        body: details
      })
      
      return response
    } catch (error) {
      console.error('Error updating repository details:', error)
      throw error
    }
  }

  // Upload instruction manual PDF
  async uploadInstructionManual(repoId, file) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch(`${this.baseURL}/repository/${repoId}/upload-manual`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error uploading instruction manual:', error)
      throw error
    }
  }

  // Download instruction manual PDF
  async downloadInstructionManual(repoId) {
    try {
      const response = await fetch(`${this.baseURL}/repository/${repoId}/download-manual`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Return the blob for download
      const blob = await response.blob()
      return blob
    } catch (error) {
      console.error('Error downloading instruction manual:', error)
      throw error
    }
  }
}

export default new FoxNestAPI()
