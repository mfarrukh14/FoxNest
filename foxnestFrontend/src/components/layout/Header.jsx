import { FiMenu, FiBell, FiSearch, FiSettings } from 'react-icons/fi'
import React from 'react'

const Header = ({ sidebarOpen, setSidebarOpen }) => {
  return (
    <header className="sticky top-0 z-10 bg-white/10 backdrop-blur-xl border-b border-white/20">
      <div className="flex items-center justify-between h-16 px-6">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors lg:hidden"
          >
            <FiMenu className="w-5 h-5" />
          </button>
          
          {/* Search */}
          <div className="relative hidden md:block">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FiSearch className="h-4 w-4 text-white/50" />
            </div>
            <input
              type="text"
              placeholder="Search repositories, users..."
              className="block w-64 pl-10 pr-3 py-2 border border-white/20 rounded-xl bg-white/10 backdrop-blur-sm text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Search for mobile */}
          <button className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors md:hidden">
            <FiSearch className="w-5 h-5" />
          </button>

          {/* Notifications */}
          <button className="relative p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors">
            <FiBell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-400 rounded-full"></span>
          </button>

          {/* Settings */}
          <button className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors">
            <FiSettings className="w-5 h-5" />
          </button>

          {/* User Avatar */}
          <div className="relative">
            <button className="flex items-center space-x-3 p-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">U</span>
              </div>
              <span className="hidden sm:block text-white font-medium">User</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
