'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/lib/store/auth'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { useRouter } from 'next/navigation'
import { FileText, Upload, FolderOpen, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { casesApi, Case } from '@/lib/api/cases'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const router = useRouter()
  const [recentCases, setRecentCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    processing: 0,
    failed: 0,
  })

  useEffect(() => {
    loadRecentCases()
  }, [])

  const loadRecentCases = async () => {
    try {
      setLoading(true)
      const response = await casesApi.listCases(0, 5)
      setRecentCases(response.cases)

      // Calculate stats
      const stats = response.cases.reduce(
        (acc, c) => {
          acc.total++
          if (c.status === 'completed') acc.completed++
          if (c.status === 'processing') acc.processing++
          if (c.status === 'failed') acc.failed++
          return acc
        },
        { total: 0, completed: 0, processing: 0, failed: 0 }
      )
      setStats(stats)
    } catch (err) {
      console.error('Failed to load cases:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Aurigo</h1>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <span className="text-sm text-gray-600 dark:text-gray-400 hidden sm:inline">
                Welcome, {user?.full_name || user?.username}!
              </span>
              <Button variant="outline" onClick={handleLogout} size="sm">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Welcome to Aurigo EB-1A Assistant
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Your intelligent assistant for generating professional EB-1A petition letters. Upload
            case folders, and let AI create attorney letters with auto-organized exhibits.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={<FolderOpen className="h-5 w-5" />}
            label="Total Cases"
            value={stats.total}
            color="blue"
          />
          <StatCard
            icon={<CheckCircle className="h-5 w-5" />}
            label="Completed"
            value={stats.completed}
            color="green"
          />
          <StatCard
            icon={<Clock className="h-5 w-5" />}
            label="Processing"
            value={stats.processing}
            color="yellow"
          />
          <StatCard
            icon={<AlertCircle className="h-5 w-5" />}
            label="Failed"
            value={stats.failed}
            color="red"
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <ActionCard
            icon={<Upload className="h-8 w-8 text-primary-600 dark:text-primary-400" />}
            title="Upload New Case"
            description="Upload a case folder to generate an attorney letter"
            onClick={() => router.push('/cases/upload')}
          />
          <ActionCard
            icon={<FolderOpen className="h-8 w-8 text-primary-600 dark:text-primary-400" />}
            title="My Cases"
            description="View and manage all your cases"
            onClick={() => router.push('/cases')}
          />
          <ActionCard
            icon={<FileText className="h-8 w-8 text-primary-600 dark:text-primary-400" />}
            title="Documentation"
            description="Learn how to use Aurigo effectively"
            onClick={() => window.open('https://github.com/yourusername/aurigo', '_blank')}
          />
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Cases</h3>
            {recentCases.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/cases')}
              >
                View All
              </Button>
            )}
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading cases...</p>
            </div>
          ) : recentCases.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 dark:text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                No cases yet. Start by uploading your first case!
              </p>
              <Button onClick={() => router.push('/cases/upload')}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Case
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {recentCases.map((caseItem) => (
                <div
                  key={caseItem.case_id}
                  onClick={() => router.push(`/cases/${caseItem.case_id}`)}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {caseItem.case_name}
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(caseItem.created_at).toLocaleDateString()} •{' '}
                      {caseItem.status}
                      {caseItem.criteria_matched ? ` • ${caseItem.criteria_matched} criteria` : ''}
                    </p>
                  </div>
                  <div className="ml-4">
                    {caseItem.status === 'completed' && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    {caseItem.status === 'processing' && (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
                    )}
                    {caseItem.status === 'failed' && (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: number
  color: 'blue' | 'green' | 'yellow' | 'red'
}) {
  const colorClasses = {
    blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    yellow: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
    red: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div className={`inline-flex p-2 rounded-lg mb-2 ${colorClasses[color]}`}>
        {icon}
      </div>
      <div className="text-2xl font-bold text-gray-900 dark:text-white">{value}</div>
      <div className="text-sm text-gray-600 dark:text-gray-400">{label}</div>
    </div>
  )
}

function ActionCard({
  icon,
  title,
  description,
  onClick,
}: {
  icon: React.ReactNode
  title: string
  description: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left"
    >
      <div className="mb-4">{icon}</div>
      <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{title}</h3>
      <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
    </button>
  )
}
