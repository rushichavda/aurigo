'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { ArrowLeft, Download, FileText, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { casesApi, LetterPreviewResponse, ExhibitItem } from '@/lib/api/cases'

export default function LetterPreviewPage() {
  const router = useRouter()
  const params = useParams()
  const caseId = parseInt(params.id as string)

  const [letterData, setLetterData] = useState<LetterPreviewResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadLetterPreview()
  }, [caseId])

  const loadLetterPreview = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await casesApi.previewLetter(caseId)
      setLetterData(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load letter preview')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    try {
      const response = await casesApi.getDownloadLinks(caseId)
      if (response.files.attorney_letter) {
        alert('Download functionality: ' + JSON.stringify(response.files, null, 2))
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to get download links')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading letter preview...</p>
        </div>
      </div>
    )
  }

  if (error || !letterData) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Button variant="outline" onClick={() => router.back()} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <FileText className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Error Loading Preview
            </h3>
            <p className="text-gray-600 dark:text-gray-400">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  // Sort exhibit groups alphabetically
  const sortedGroups = Object.keys(letterData.exhibit_index).sort()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Case
          </Button>
          <Button onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Download Files
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Letter Content */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
              {/* Letter Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-start justify-between">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                      Attorney Letter Preview
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                      Case: {letterData.case_name}
                    </p>
                    {letterData.field && (
                      <p className="text-sm text-gray-500 dark:text-gray-500">
                        Field: {letterData.field}
                      </p>
                    )}
                  </div>
                  {letterData.is_polished && (
                    <div className="flex items-center gap-2 px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 rounded-full text-sm">
                      <Sparkles className="h-4 w-4" />
                      AI Polished
                    </div>
                  )}
                </div>
              </div>

              {/* Letter Content */}
              <div className="p-8">
                <div className="prose dark:prose-invert max-w-none">
                  <div
                    className="whitespace-pre-wrap text-gray-900 dark:text-gray-100 leading-relaxed"
                    style={{
                      fontFamily: 'Georgia, serif',
                      fontSize: '14px',
                      lineHeight: '1.8',
                    }}
                  >
                    {letterData.letter_content}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar - Exhibits and Stats */}
          <div className="space-y-6">
            {/* Statistics */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Case Statistics
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Criteria Matched
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {letterData.criteria_matched || 0}/10
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Total Exhibits
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {letterData.total_exhibits || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Exhibit Index */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Exhibit Index
              </h2>
              <div className="space-y-4">
                {sortedGroups.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-500">No exhibits found</p>
                ) : (
                  sortedGroups.map((group) => (
                    <div key={group} className="space-y-2">
                      <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                        Group {group}
                      </h3>
                      <div className="space-y-2 pl-2">
                        {letterData.exhibit_index[group].map((exhibit: ExhibitItem) => (
                          <div
                            key={exhibit.exhibit_id}
                            className="p-2 bg-gray-50 dark:bg-gray-900 rounded text-xs"
                          >
                            <div className="font-medium text-primary-600 dark:text-primary-400 mb-1">
                              {exhibit.exhibit_id}
                            </div>
                            <div className="text-gray-900 dark:text-white font-medium mb-1">
                              {exhibit.title}
                            </div>
                            {exhibit.description && (
                              <div className="text-gray-600 dark:text-gray-400 line-clamp-2">
                                {exhibit.description}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Download Section */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Export Documents
              </h2>
              <div className="space-y-3">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Download the complete attorney letter and exhibit index in DOCX format.
                </p>
                <Button onClick={handleDownload} className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Download All Files
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
