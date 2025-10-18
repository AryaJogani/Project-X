'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { name: 'Week 1', gaps: 12, resolved: 3 },
  { name: 'Week 2', gaps: 18, resolved: 8 },
  { name: 'Week 3', gaps: 22, resolved: 12 },
  { name: 'Week 4', gaps: 24, resolved: 18 },
  { name: 'Week 5', gaps: 20, resolved: 15 },
  { name: 'Week 6', gaps: 24, resolved: 8 },
]

export function GapChart() {
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="gaps" 
            stroke="#3b82f6" 
            strokeWidth={2}
            name="Gaps Detected"
          />
          <Line 
            type="monotone" 
            dataKey="resolved" 
            stroke="#10b981" 
            strokeWidth={2}
            name="Gaps Resolved"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
