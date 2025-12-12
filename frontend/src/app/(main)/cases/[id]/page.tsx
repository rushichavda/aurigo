'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import {
  ArrowLeft,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  Download,
  Eye,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { casesApi, CaseStatusResponse } from '@/lib/api/cases'

export default function CaseDetailPage() {
  const router = useRouter()
  const params = useParams()
  const caseId = parseInt(params.id as string)

  const [caseData, setCaseData] = useState<CaseStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    loadCaseStatus()

    // Poll for updates if processing
    const interval = setInterval(() => {
      if (caseData?.status === 'processing') {
        loadCaseStatus()
      }
    }, 3000) // Poll every 3 seconds

    setPollingInterval(interval)

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [caseId, caseData?.status])

  const loadCaseStatus = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await casesApi.getCaseStatus(caseId)
      setCaseData(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load case')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    try {
      const response = await casesApi.getDownloadLinks(caseId)
      if (response.files.attorney_letter) {
        // In a real app, you'd download these files
        alert('Download functionality: ' + JSON.stringify(response.files, null, 2))
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to get download links')
    }
  }

  const getStatusIcon = () => {
    if (!caseData) return null

    switch (caseData.status) {
      case 'completed':
        return <CheckCircle className="h-12 w-12 text-green-500" />
      case 'processing':
        return <Loader2 className="h-12 w-12 text-blue-500 animate-spin" />
      case 'failed':
        return <XCircle className="h-12 w-12 text-red-500" />
      default:
        return <Clock className="h-12 w-12 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 dark:text-green-400'
      case 'processing':
        return 'text-blue-600 dark:text-blue-400'
      case 'failed':
        return 'text-red-600 dark:text-red-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }

  if (loading && !caseData) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading case details...</p>
        </div>
      </div>
    )
  }

  if (error || !caseData) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Button variant="outline" onClick={() => router.back()} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Error Loading Case
            </h3>
            <p className="text-gray-600 dark:text-gray-400">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Button variant="outline" onClick={() => router.back()} className="mb-6">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Cases
        </Button>

        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              {getStatusIcon()}
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {caseData.case_name}
                </h1>
                {caseData.field && (
                  <p className="text-gray-600 dark:text-gray-400 mt-1">{caseData.field}</p>
                )}
                <div className="mt-2 flex items-center gap-2">
                  <span className={`text-sm font-medium ${getStatusColor(caseData.status)}`}>
                    Status: {caseData.status.toUpperCase()}
                  </span>
                  {caseData.current_step && (
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      • {caseData.current_step}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {caseData.status === 'completed' && (
              <div className="flex gap-2">
                <Button
                  onClick={() => router.push(`/cases/${caseId}/preview`)}
                  variant="outline"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Preview Letter
                </Button>
                <Button onClick={handleDownload}>
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {caseData.status === 'processing' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <div className="mb-2 flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Processing Progress
              </span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {caseData.progress}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
              <div
                className="bg-primary-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${caseData.progress}%` }}
              />
            </div>
            {caseData.current_step && (
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Current step: {caseData.current_step}
              </p>
            )}
          </div>
        )}

        {/* Case Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <StatCard
            label="EB-1A Criteria Met"
            value={caseData.criteria_matched?.toString() || '0'}
            subtext="out of 10 required"
            icon={<FileText className="h-6 w-6 text-primary-600" />}
          />
          <StatCard
            label="Total Documents"
            value={caseData.total_documents?.toString() || '0'}
            subtext="processed"
            icon={<FileText className="h-6 w-6 text-blue-600" />}
          />
          <StatCard
            label="Total Exhibits"
            value={caseData.total_exhibits?.toString() || '0'}
            subtext="organized"
            icon={<FileText className="h-6 w-6 text-green-600" />}
          />
          <StatCard
            label="Created"
            value={new Date(caseData.created_at).toLocaleDateString()}
            subtext={new Date(caseData.created_at).toLocaleTimeString()}
            icon={<Clock className="h-6 w-6 text-gray-600" />}
          />
        </div>

        {/* Processing Steps Info */}
        {caseData.status === 'processing' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Processing Steps
            </h2>
            <div className="space-y-3">
              <ProcessStep
                title="Validating folder structure"
                completed={caseData.progress > 10}
              />
              <ProcessStep
                title="Mapping evidence to EB-1A criteria"
                completed={caseData.progress > 20}
              />
              <ProcessStep
                title="Parsing documents"
                completed={caseData.progress > 40}
              />
              <ProcessStep
                title="Extracting information using AI"
                completed={caseData.progress > 60}
              />
              <ProcessStep
                title="Organizing exhibits"
                completed={caseData.progress > 75}
              />
              <ProcessStep
                title="Generating attorney letter"
                completed={caseData.progress > 90}
              />
              <ProcessStep
                title="Exporting documents"
                completed={caseData.progress >= 100}
              />
            </div>
          </div>
        )}

        {/* Completed Info */}
        {caseData.status === 'completed' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-start gap-4">
              <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Case Processing Completed
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Your EB-1A petition letter has been generated successfully. You can now preview
                  the letter or download the final documents.
                </p>
                <div className="flex gap-3">
                  <Button onClick={() => router.push(`/cases/${caseId}/preview`)}>
                    <Eye className="h-4 w-4 mr-2" />
                    Preview Letter
                  </Button>
                  <Button variant="outline" onClick={handleDownload}>
                    <Download className="h-4 w-4 mr-2" />
                    Download Files
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Failed Info */}
        {caseData.status === 'failed' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-start gap-4">
              <XCircle className="h-6 w-6 text-red-500 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Processing Failed
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  An error occurred while processing your case. Please try uploading again or
                  contact support if the issue persists.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  subtext,
  icon,
}: {
  label: string
  value: string
  subtext: string
  icon: React.ReactNode
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</span>
        {icon}
      </div>
      <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{value}</div>
      <div className="text-xs text-gray-500 dark:text-gray-500">{subtext}</div>
    </div>
  )
}

function ProcessStep({ title, completed }: { title: string; completed: boolean }) {
  return (
    <div className="flex items-center gap-3">
      {completed ? (
        <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
      ) : (
        <div className="h-5 w-5 rounded-full border-2 border-gray-300 dark:border-gray-600 flex-shrink-0" />
      )}
      <span
        className={`text-sm ${
          completed
            ? 'text-gray-900 dark:text-white font-medium'
            : 'text-gray-500 dark:text-gray-400'
        }`}
      >
        {title}
      </span>
    </div>
  )
}
