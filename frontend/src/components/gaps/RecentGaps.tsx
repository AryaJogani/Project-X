'use client'

import { Card, CardContent } from '@/components/ui/Card'

const recentGaps = [
  {
    id: 1,
    type: 'Structural',
    severity: 'High',
    description: 'Missing ESG metrics in sustainability report',
    location: 'Section 3.2',
    status: 'open',
    createdAt: '2 hours ago'
  },
  {
    id: 2,
    type: 'Semantic',
    severity: 'Medium',
    description: 'Undefined technical terms in governance section',
    location: 'Section 2.1',
    status: 'in_progress',
    createdAt: '4 hours ago'
  },
  {
    id: 3,
    type: 'ESG Compliance',
    severity: 'Critical',
    description: 'Missing TCFD climate risk disclosures',
    location: 'Section 4.3',
    status: 'open',
    createdAt: '6 hours ago'
  },
  {
    id: 4,
    type: 'Structural',
    severity: 'Low',
    description: 'Incomplete data table in environmental metrics',
    location: 'Table 2.1',
    status: 'resolved',
    createdAt: '1 day ago'
  }
]

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'Critical':
      return 'bg-red-100 text-red-800'
    case 'High':
      return 'bg-orange-100 text-orange-800'
    case 'Medium':
      return 'bg-yellow-100 text-yellow-800'
    case 'Low':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'open':
      return 'bg-red-100 text-red-800'
    case 'in_progress':
      return 'bg-blue-100 text-blue-800'
    case 'resolved':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export function RecentGaps() {
  return (
    <div className="space-y-4">
      {recentGaps.map((gap) => (
        <Card key={gap.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-sm font-medium text-gray-900">
                    {gap.type}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(gap.severity)}`}>
                    {gap.severity}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(gap.status)}`}>
                    {gap.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-1">
                  {gap.description}
                </p>
                <div className="flex items-center text-xs text-gray-500">
                  <span>📍 {gap.location}</span>
                  <span className="mx-2">•</span>
                  <span>🕒 {gap.createdAt}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      
      <div className="text-center pt-4">
        <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
          View all gaps →
        </button>
      </div>
    </div>
  )
}
