'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { GapChart } from '@/components/gaps/GapChart'
import { RecentGaps } from '@/components/gaps/RecentGaps'
import { SystemMetrics } from '@/components/analytics/SystemMetrics'

export function Dashboard() {
  const [isLoading, setIsLoading] = useState(true)
  const [metrics, setMetrics] = useState({
    totalGaps: 0,
    resolvedGaps: 0,
    activeQuestions: 0,
    documentsAnalyzed: 0
  })

  useEffect(() => {
    // Simulate loading metrics
    const timer = setTimeout(() => {
      setMetrics({
        totalGaps: 24,
        resolvedGaps: 8,
        activeQuestions: 12,
        documentsAnalyzed: 5
      })
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          AI-powered ESG knowledge gap detection and resolution
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Gaps</CardTitle>
            <span className="text-2xl">🔍</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totalGaps}</div>
            <p className="text-xs text-muted-foreground">
              +2 from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved</CardTitle>
            <span className="text-2xl">✅</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.resolvedGaps}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((metrics.resolvedGaps / metrics.totalGaps) * 100)}% completion rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Questions</CardTitle>
            <span className="text-2xl">❓</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.activeQuestions}</div>
            <p className="text-xs text-muted-foreground">
              In progress
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <span className="text-2xl">📄</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.documentsAnalyzed}</div>
            <p className="text-xs text-muted-foreground">
              Analyzed this month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Gap Analysis Trends</CardTitle>
            <CardDescription>
              Gap detection and resolution over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <GapChart />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Gaps</CardTitle>
            <CardDescription>
              Latest gaps detected in your documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RecentGaps />
          </CardContent>
        </Card>
      </div>

      {/* System Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>System Performance</CardTitle>
          <CardDescription>
            LLM orchestration and system health metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SystemMetrics />
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button>
              Upload New Document
            </Button>
            <Button variant="outline">
              Analyze All Documents
            </Button>
            <Button variant="outline">
              Generate Questions
            </Button>
            <Button variant="outline">
              View Analytics
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
