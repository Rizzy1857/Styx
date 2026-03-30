import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Inventory from './pages/Inventory'
import APIDetail from './pages/APIDetail'
import Security from './pages/Security'
import Graph from './pages/Graph'
import Simulator from './pages/Simulator'
import Alerts from './pages/Alerts'
import './index.css'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Router>
      <div className="flex h-screen bg-dark-navy">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? 'w-64' : 'w-20'
          } bg-navy border-r border-light-navy transition-all duration-300 overflow-hidden`}
        >
          <div className="p-6 border-b border-light-navy">
            <h1 className={`text-2xl font-bold text-ice-blue ${!sidebarOpen && 'text-center'}`}>
              {sidebarOpen ? 'STYX' : 'S'}
            </h1>
          </div>
          <nav className="mt-8 space-y-2">
            <NavLink to="/inventory" label="Inventory" icon="📦" open={sidebarOpen} />
            <NavLink to="/security" label="Security" icon="🔒" open={sidebarOpen} />
            <NavLink to="/graph" label="Dependencies" icon="🔗" open={sidebarOpen} />
            <NavLink to="/simulator" label="Simulator" icon="⚡" open={sidebarOpen} />
            <NavLink to="/alerts" label="Alerts" icon="🚨" open={sidebarOpen} />
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {/* Top Bar */}
          <div className="bg-light-navy border-b border-ice-blue/20 px-6 py-4 flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-ice-blue hover:text-ice-blue/80 transition"
            >
              ☰
            </button>
            <h2 className="text-lg font-semibold text-ice-blue">API Lifecycle Intelligence</h2>
            <div className="w-8" />
          </div>

          {/* Page Content */}
          <div className="p-6">
            <Routes>
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/inventory/:id" element={<APIDetail />} />
              <Route path="/security" element={<Security />} />
              <Route path="/graph" element={<Graph />} />
              <Route path="/simulator" element={<Simulator />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/" element={<Inventory />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

function NavLink({ to, label, icon, open }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-3 px-6 py-3 text-ice-blue hover:bg-light-navy/50 transition rounded-lg mx-2"
    >
      <span className="text-xl">{icon}</span>
      {open && <span className="font-medium">{label}</span>}
    </Link>
  )
}
