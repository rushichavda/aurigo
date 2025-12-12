'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { FileText, Upload, Clock, CheckCircle, XCircle, Trash2, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { casesApi, Case } from '@/lib/api/cases'

export default function CasesPage() {
  const router = useRouter()
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadCases()
  }, [])

  const loadCases = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await casesApi.listCases()
      setCases(response.cases)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load cases')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (caseId: number) => {
    if (!confirm('Are you sure you want to delete this case? This action cannot be undone.')) {
      return
    }

    try {
      await casesApi.deleteCase(caseId)
      loadCases() // Reload the list
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete case')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'processing':
        return (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
        )
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
      case 'processing':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300'
      case 'failed':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading cases...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Cases</h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Manage your EB-1A petition cases
            </p>
          </div>
          <Button onClick={() => router.push('/cases/upload')}>
            <Upload className="h-4 w-4 mr-2" />
            Upload New Case
          </Button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-300">{error}</p>
          </div>
        )}

        {cases.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <FileText className="h-16 w-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No cases yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Get started by uploading your first case
            </p>
            <Button onClick={() => router.push('/cases/upload')}>
              <Upload className="h-4 w-4 mr-2" />
              Upload Case
            </Button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {cases.map((caseItem) => (
              <div
                key={caseItem.case_id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(caseItem.status)}
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {caseItem.case_name}
                      </h3>
                      {caseItem.field && (
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {caseItem.field}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Status</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(caseItem.status)}`}>
                      {caseItem.status}
                    </span>
                  </div>

                  {caseItem.status === 'processing' && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Progress</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {caseItem.progress}%
                      </span>
                    </div>
                  )}

                  {caseItem.criteria_matched !== undefined && caseItem.criteria_matched > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Criteria</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {caseItem.criteria_matched}/10
                      </span>
                    </div>
                  )}

                  {caseItem.total_exhibits !== undefined && caseItem.total_exhibits > 0 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Exhibits</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {caseItem.total_exhibits}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Created</span>
                    <span className="text-gray-900 dark:text-white">
                      {new Date(caseItem.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/cases/${caseItem.case_id}`)}
                    className="flex-1"
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(caseItem.case_id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/20"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
