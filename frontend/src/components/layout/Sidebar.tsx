'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/Card'

const navigation = [
  { name: 'Dashboard', href: '/', icon: '📊', current: true },
  { name: 'Gap Analysis', href: '/gaps', icon: '🔍', current: false },
  { name: 'Questions', href: '/questions', icon: '❓', current: false },
  { name: 'Knowledge Base', href: '/knowledge-base', icon: '📚', current: false },
  { name: 'Analytics', href: '/analytics', icon: '📈', current: false },
]

export function Sidebar() {
  const [activeItem, setActiveItem] = useState('Dashboard')

  return (
    <div className="w-64 bg-white shadow-sm border-r">
      <div className="p-6">
        <nav className="space-y-2">
          {navigation.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                activeItem === item.name
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
              onClick={() => setActiveItem(item.name)}
            >
              <span className="mr-3 text-lg">{item.icon}</span>
              {item.name}
            </a>
          ))}
        </nav>
      </div>

      {/* System Status */}
      <div className="p-6 border-t">
        <h3 className="text-sm font-medium text-gray-900 mb-3">
          System Status
        </h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">LLM Orchestrator</span>
            <span className="text-green-600">✓ Active</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Vector Store</span>
            <span className="text-green-600">✓ Connected</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Database</span>
            <span className="text-green-600">✓ Connected</span>
          </div>
        </div>
      </div>
    </div>
  )
}
