'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

export function Header() {
  const [isConnected, setIsConnected] = useState(false)

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900">
                Knowledge Transfer Bot
              </h1>
            </div>
            <div className="ml-4">
              <span className="text-sm text-gray-500">
                AI-Powered ESG Gap Detection
              </span>
            </div>
          </div>

          {/* Status and Actions */}
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                Upload Document
              </Button>
              <Button size="sm">
                Analyze Gaps
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
