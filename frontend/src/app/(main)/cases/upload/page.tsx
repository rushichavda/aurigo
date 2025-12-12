'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, FileArchive, AlertCircle, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { casesApi } from '@/lib/api/cases'

export default function UploadCasePage() {
  const router = useRouter()
  const [beneficiaryName, setBeneficiaryName] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type !== 'application/zip' && !file.name.endsWith('.zip')) {
        setError('Please select a ZIP file')
        setSelectedFile(null)
      } else {
        setSelectedFile(file)
        setError(null)
        setValidationErrors([])
      }
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!beneficiaryName.trim()) {
      setError('Please enter beneficiary name')
      return
    }

    if (!selectedFile) {
      setError('Please select a file')
      return
    }

    try {
      setUploading(true)
      setError(null)
      setValidationErrors([])

      const response = await casesApi.uploadCase(beneficiaryName, selectedFile)

      if (response.success) {
        setSuccess(true)
        // Auto-start processing
        await casesApi.processCase(response.case_id)

        // Navigate to case detail page after 1 second
        setTimeout(() => {
          router.push(`/cases/${response.case_id}`)
        }, 1000)
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'object' && detail.errors) {
        setValidationErrors(detail.errors)
        setError(detail.message || 'Upload failed')
      } else {
        setError(detail || 'Upload failed. Please try again.')
      }
      setSuccess(false)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Button
            variant="outline"
            onClick={() => router.back()}
            className="mb-4"
          >
            ← Back
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Upload Case</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Upload a ZIP file containing the case folder with Case_Overview.docx and Evidence folder
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <form onSubmit={handleUpload} className="space-y-6">
            {/* Beneficiary Name */}
            <div>
              <label htmlFor="beneficiary" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Beneficiary Name *
              </label>
              <Input
                id="beneficiary"
                type="text"
                value={beneficiaryName}
                onChange={(e) => setBeneficiaryName(e.target.value)}
                placeholder="Enter beneficiary full name"
                disabled={uploading || success}
                className="w-full"
              />
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Case Folder (ZIP) *
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg hover:border-primary-500 dark:hover:border-primary-400 transition-colors">
                <div className="space-y-1 text-center">
                  <FileArchive className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
                  <div className="flex text-sm text-gray-600 dark:text-gray-400">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer rounded-md font-medium text-primary-600 dark:text-primary-400 hover:text-primary-500 focus-within:outline-none"
                    >
                      <span>Upload a file</span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        accept=".zip"
                        className="sr-only"
                        onChange={handleFileChange}
                        disabled={uploading || success}
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    ZIP file up to 500MB
                  </p>
                </div>
              </div>
              {selectedFile && (
                <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <FileArchive className="h-4 w-4 mr-2" />
                  {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              )}
            </div>

            {/* Validation Errors */}
            {validationErrors.length > 0 && (
              <div className="rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400 dark:text-red-500" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800 dark:text-red-300">
                      Validation Errors
                    </h3>
                    <div className="mt-2 text-sm text-red-700 dark:text-red-400">
                      <ul className="list-disc pl-5 space-y-1">
                        {validationErrors.map((err, idx) => (
                          <li key={idx}>{err}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* General Error */}
            {error && validationErrors.length === 0 && (
              <div className="rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400 dark:text-red-500" />
                  <div className="ml-3">
                    <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="rounded-md bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 p-4">
                <div className="flex">
                  <CheckCircle className="h-5 w-5 text-green-400 dark:text-green-500" />
                  <div className="ml-3">
                    <p className="text-sm text-green-800 dark:text-green-300">
                      Case uploaded successfully! Processing has started. Redirecting...
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={uploading || success || !beneficiaryName.trim() || !selectedFile}
                className="flex-1"
              >
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload and Process
                  </>
                )}
              </Button>
            </div>
          </form>

          {/* Instructions */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
              Folder Structure Requirements
            </h3>
            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
              <p>Your ZIP file should contain a folder with this structure:</p>
              <pre className="mt-2 p-3 bg-gray-100 dark:bg-gray-900 rounded text-xs overflow-x-auto">
{`Case_Folder/
├── Case_Overview.docx
└── Evidence/
    ├── 1. Awards and Prizes/
    ├── 2. Membership/
    ├── 3. Critical Role/
    └── ...`}
              </pre>
              <p className="mt-2">
                Supported formats: PDF, DOCX, JPG, PNG, TIFF, PPTX, HTML, MD
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
