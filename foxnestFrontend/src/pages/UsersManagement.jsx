import React, { useState, useEffect } from 'react'
import { FiUser, FiGitCommit, FiFolder, FiCalendar, FiMail, FiWifi, FiWifiOff, FiEdit3, FiTrash2, FiPlus, FiSave, FiX, FiShield, FiUserPlus } from 'react-icons/fi'
import GlassCard from '../components/ui/GlassCard'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import api from '../utils/api'

const UsersManagement = () => {
  const [users, setUsers] = useState([])
  const [repositories, setRepositories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedUser, setSelectedUser] = useState(null)
  const [showAddUserModal, setShowAddUserModal] = useState(false)
  const [showPermissionModal, setShowPermissionModal] = useState(false)
  const [showEditPermissionModal, setShowEditPermissionModal] = useState(false)
  const [newUser, setNewUser] = useState({ 
    username: '', 
    email: '', 
    full_name: '', 
    role: 'developer',
    team_lead_id: null 
  })
  const [permissionForm, setPermissionForm] = useState({
    username: '',
    repo_id: '',
    permission_level: 'read'
  })
  const [editPermissionForm, setEditPermissionForm] = useState({
    username: '',
    repo_id: '',
    permission_level: 'read'
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch users
      const usersResponse = await fetch('http://192.168.0.11:5000/api/users')
      const usersData = await usersResponse.json()

      // Fetch repositories
      const reposResponse = await api.listAllRepositories()

      if (usersData.success) {
        setUsers(usersData.users)
      }

      if (reposResponse.success) {
        setRepositories(reposResponse.repositories)
      }
    } catch (err) {
      setError(`Error connecting to server: ${err.message}`)
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = async () => {
    try {
      // Validate required fields
      if (!newUser.username) {
        alert('Username is required')
        return
      }

      
      if (newUser.role === 'developer' && !newUser.team_lead_id) {
        alert('Please select a team lead for this developer')
        return
      }

      const response = await fetch('http://192.168.0.11:5000/api/users/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser)
      })

      if (response.ok) {
        await fetchData()
        setShowAddUserModal(false)
        setNewUser({ 
          username: '', 
          email: '', 
          full_name: '', 
          role: 'developer',
          team_lead_id: null 
        })
      } else {
        const errorData = await response.json()
        alert(`Error: ${errorData.detail || 'Failed to create user'}`)
      }
    } catch (error) {
      console.error('Error adding user:', error)
      alert('Failed to add user. Please try again.')
    }
  }

  const handleAddPermission = async () => {
    try {
      const response = await fetch('http://192.168.0.11:5000/api/permissions/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(permissionForm)
      })

      if (response.ok) {
        alert('Permission granted successfully!')
        setShowPermissionModal(false)
        setPermissionForm({ username: '', repo_id: '', permission_level: 'read' })
      }
    } catch (error) {
      console.error('Error adding permission:', error)
    }
  }

  const handleRevokePermission = async (username, repoId) => {
    if (!confirm('Are you sure you want to revoke this permission?')) return

    try {
      const response = await fetch(
        `http://192.168.0.11:5000/api/permissions/revoke?username=${username}&repo_id=${repoId}`,
        { method: 'DELETE' }
      )

      if (response.ok) {
        alert('Permission revoked successfully!')
        if (selectedUser) {
          await fetchUserPermissions(selectedUser.username)
        }
      }
    } catch (error) {
      console.error('Error revoking permission:', error)
    }
  }

  const handleEditPermission = (permission) => {
    setEditPermissionForm({
      username: selectedUser.username,
      repo_id: permission.repository_id,
      permission_level: permission.permission_level
    })
    setShowEditPermissionModal(true)
  }

  const handleUpdatePermission = async () => {
    try {
      const response = await fetch('http://192.168.0.11:5000/api/permissions/update', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editPermissionForm)
      })

      if (response.ok) {
        alert('Permission updated successfully!')
        setShowEditPermissionModal(false)
        if (selectedUser) {
          await fetchUserPermissions(selectedUser.username)
        }
      }
    } catch (error) {
      console.error('Error updating permission:', error)
    }
  }

  const handleDeleteUser = async (username) => {
    if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) return

    try {
      const response = await fetch(`http://192.168.0.11:5000/api/users/${username}`, {
        method: 'DELETE'
      })

      const data = await response.json()

      if (response.ok) {
        alert('User deleted successfully!')
        await fetchData()
        if (selectedUser?.username === username) {
          setSelectedUser(null)
        }
      } else {
        alert(data.detail || 'Failed to delete user')
      }
    } catch (error) {
      console.error('Error deleting user:', error)
      alert('Error deleting user')
    }
  }

  const fetchUserPermissions = async (username) => {
    try {
      const response = await fetch(`http://192.168.0.11:5000/api/permissions/user/${username}`)
      const data = await response.json()

      if (data.success) {
        setSelectedUser({
          ...users.find(u => u.username === username),
          permissions: data.permissions
        })
      }
    } catch (error) {
      console.error('Error fetching user permissions:', error)
    }
  }

  const handleUserClick = (user) => {
    if (selectedUser?.username === user.username) {
      setSelectedUser(null)
    } else {
      fetchUserPermissions(user.username)
    }
  }

  const getPermissionBadgeVariant = (level) => {
    switch (level) {
      case 'admin': return 'danger'
      case 'team_lead': return 'warning'
      case 'write': return 'info'
      case 'read': return 'secondary'
      default: return 'default'
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <FiUser className="w-8 h-8 animate-pulse text-blue-400" />
          <span className="ml-2 text-gray-300">Loading users...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Users Management</h1>
          <p className="text-white/70">Manage users and their repository permissions</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="primary"
            onClick={() => setShowAddUserModal(true)}
            className="flex items-center space-x-2"
          >
            <FiUserPlus className="w-4 h-4" />
            <span>Add User</span>
          </Button>
          <Button
            variant="secondary"
            onClick={() => setShowPermissionModal(true)}
            className="flex items-center space-x-2"
          >
            <FiShield className="w-4 h-4" />
            <span>Grant Permission</span>
          </Button>
        </div>
      </div>

      {/* Connection Status */}
      {error && (
        <GlassCard className="p-4 border-red-500/30 bg-red-500/10">
          <div className="flex items-center space-x-2 text-red-400">
            <FiWifiOff className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </GlassCard>
      )}

      {/* Users Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {users.map((user) => (
          <GlassCard
            key={user.id}
            className={`p-6 transition-all duration-300 ${
              selectedUser?.username === user.username
                ? 'border-blue-500/50 bg-blue-500/10'
                : 'hover:border-blue-500/30'
            }`}
          >
            <div className="space-y-4">
              {/* User Header */}
              <div className="flex items-center space-x-4">
                <div 
                  className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0 cursor-pointer"
                  onClick={() => handleUserClick(user)}
                >
                  <span className="text-white font-semibold text-lg">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0 cursor-pointer" onClick={() => handleUserClick(user)}>
                  <h3 className="font-semibold text-white truncate">{user.full_name || user.username}</h3>
                  <p className="text-sm text-white/70 truncate">@{user.username}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteUser(user.username)
                  }}
                  className="text-red-400 hover:text-red-300"
                  title="Delete user"
                >
                  <FiTrash2 className="w-4 h-4" />
                </Button>
              </div>

              {/* User Info */}
              <div className="space-y-2 text-sm text-white/70">
                {user.email && (
                  <div className="flex items-center">
                    <FiMail className="w-4 h-4 mr-2" />
                    <span className="truncate">{user.email}</span>
                  </div>
                )}
                <div className="flex items-center">
                  <FiCalendar className="w-4 h-4 mr-2" />
                  <span>Joined {new Date(user.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center">
                  <FiShield className="w-4 h-4 mr-2" />
                  <Badge variant={user.role === 'team_lead' ? 'warning' : 'info'}>
                    {user.role === 'team_lead' ? 'Team Lead' : 'Developer'}
                  </Badge>
                </div>
                {user.role === 'developer' && user.team_lead_name && (
                  <div className="flex items-center">
                    <FiUser className="w-4 h-4 mr-2" />
                    <span className="truncate">Team Lead: {user.team_lead_name}</span>
                  </div>
                )}
              </div>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* User Permissions Panel */}
      {selectedUser && (
        <GlassCard className="p-6 border-blue-500/30">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">
                {selectedUser.full_name || selectedUser.username}'s Permissions
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedUser(null)}
                className="text-gray-400 hover:text-white"
              >
                <FiX className="w-5 h-5" />
              </Button>
            </div>

            {selectedUser.permissions && selectedUser.permissions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedUser.permissions.map((perm, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-xl bg-white/10 border border-white/10"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h4 className="font-medium text-white text-sm mb-1">
                          {perm.repository_name}
                        </h4>
                        <Badge variant={getPermissionBadgeVariant(perm.permission_level)}>
                          {perm.permission_level}
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditPermission(perm)}
                          className="text-blue-400 hover:text-blue-300 -mt-2"
                          title="Edit permission"
                        >
                          <FiEdit3 className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRevokePermission(selectedUser.username, perm.repository_id)}
                          className="text-red-400 hover:text-red-300 -mt-2"
                          title="Revoke permission"
                        >
                          <FiTrash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="space-y-1 text-xs text-white/70">
                      {perm.granted_by && (
                        <p>Granted by: {perm.granted_by}</p>
                      )}
                      <p>Date: {new Date(perm.granted_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-white/70">
                <FiShield className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No permissions granted yet</p>
              </div>
            )}
          </div>
        </GlassCard>
      )}

      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <GlassCard className="max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Add New User</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAddUserModal(false)}
              >
                <FiX className="w-5 h-5" />
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Username *
                </label>
                <input
                  type="text"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                  placeholder="johndoe"
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  placeholder="john@example.com"
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                  placeholder="John Doe"
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Role *
                </label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value, team_lead_id: null })}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="developer">Developer</option>
                  <option value="team_lead">Team Lead</option>
                </select>
              </div>

              {newUser.role === 'developer' && (
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-2">
                    Assign Team Lead *
                  </label>
                  <select
                    value={newUser.team_lead_id || ''}
                    onChange={(e) => setNewUser({ ...newUser, team_lead_id: parseInt(e.target.value) || null })}
                    className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="">Select a team lead</option>
                    {users.filter(user => user.role === 'team_lead').map(user => (
                      <option key={user.id} value={user.id}>{user.username} - {user.full_name || 'No name'}</option>
                    ))}
                  </select>
                  {users.filter(user => user.role === 'team_lead').length === 0 && (
                    <p className="text-xs text-yellow-400 mt-1">
                      No team leads available. Please create a team lead user first.
                    </p>
                  )}
                </div>
              )}

              <div className="flex items-center space-x-3 pt-2">
                <Button
                  variant="primary"
                  onClick={handleAddUser}
                  disabled={!newUser.username || (newUser.role === 'developer' && !newUser.team_lead_id)}
                  className="flex-1"
                >
                  <FiSave className="w-4 h-4 mr-2" />
                  Add User
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setShowAddUserModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Grant Permission Modal */}
      {showPermissionModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <GlassCard className="max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Grant Repository Permission</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowPermissionModal(false)}
              >
                <FiX className="w-5 h-5" />
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Username *
                </label>
                <select
                  value={permissionForm.username}
                  onChange={(e) => setPermissionForm({ ...permissionForm, username: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select a user</option>
                  {users.map(user => (
                    <option key={user.id} value={user.username}>{user.username}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Repository *
                </label>
                <select
                  value={permissionForm.repo_id}
                  onChange={(e) => setPermissionForm({ ...permissionForm, repo_id: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select a repository</option>
                  {repositories.map(repo => (
                    <option key={repo.id} value={repo.id}>{repo.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Permission Level *
                </label>
                <select
                  value={permissionForm.permission_level}
                  onChange={(e) => setPermissionForm({ ...permissionForm, permission_level: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="read">Read - View only</option>
                  <option value="write">Write - Can push changes (requires approval)</option>
                  <option value="team_lead">Team Lead - Can approve changes</option>
                  <option value="admin">Admin - Full access</option>
                </select>
              </div>

              <div className="flex items-center space-x-3 pt-2">
                <Button
                  variant="primary"
                  onClick={handleAddPermission}
                  disabled={!permissionForm.username || !permissionForm.repo_id}
                  className="flex-1"
                >
                  <FiShield className="w-4 h-4 mr-2" />
                  Grant Permission
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setShowPermissionModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Edit Permission Modal */}
      {showEditPermissionModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <GlassCard className="max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Edit Permission</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowEditPermissionModal(false)}
              >
                <FiX className="w-5 h-5" />
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  User
                </label>
                <input
                  type="text"
                  value={editPermissionForm.username}
                  disabled
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white/50 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Repository
                </label>
                <input
                  type="text"
                  value={repositories.find(r => r.id === editPermissionForm.repo_id)?.name || ''}
                  disabled
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white/50 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Permission Level *
                </label>
                <select
                  value={editPermissionForm.permission_level}
                  onChange={(e) => setEditPermissionForm({ ...editPermissionForm, permission_level: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="read">Read - View only</option>
                  <option value="write">Write - Can push changes (requires approval)</option>
                  <option value="team_lead">Team Lead - Can approve changes</option>
                  <option value="admin">Admin - Full access</option>
                </select>
              </div>

              <div className="flex items-center space-x-3 pt-2">
                <Button
                  variant="primary"
                  onClick={handleUpdatePermission}
                  className="flex-1"
                >
                  <FiSave className="w-4 h-4 mr-2" />
                  Update Permission
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setShowEditPermissionModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  )
}

export default UsersManagement
