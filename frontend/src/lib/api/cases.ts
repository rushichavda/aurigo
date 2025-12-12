import api from '../api'

export interface Case {
  case_id: number
  case_name: string
  field?: string
  status: 'uploaded' | 'processing' | 'completed' | 'failed'
  progress: number
  criteria_matched?: number
  created_at: string
  completed_at?: string
  current_step?: string
  total_documents?: number
  total_exhibits?: number
}

export interface CaseUploadResponse {
  success: boolean
  case_id: number
  case_name: string
  validation: {
    valid: boolean
    errors?: string[]
    evidence_folders?: any[]
  }
  message: string
}

export interface CaseStatusResponse {
  case_id: number
  case_name: string
  field?: string
  status: string
  current_step?: string
  progress: number
  criteria_matched?: number
  total_documents?: number
  total_exhibits?: number
  created_at: string
  completed_at?: string
}

export interface ExhibitItem {
  exhibit_id: string
  title: string
  description: string
}

export interface LetterPreviewResponse {
  success: boolean
  case_id: number
  case_name: string
  field?: string
  letter_content: string
  exhibit_index: Record<string, ExhibitItem[]>
  criteria_matched?: number
  total_exhibits?: number
  is_polished: boolean
}

export interface DownloadFilesResponse {
  success: boolean
  files: {
    attorney_letter?: string
    exhibit_index?: string
    metadata?: string
  }
}

export interface CaseListResponse {
  success: boolean
  cases: Case[]
  total: number
}

export const casesApi = {
  /**
   * Upload a case folder for processing
   */
  uploadCase: async (beneficiaryName: string, file: File): Promise<CaseUploadResponse> => {
    const formData = new FormData()
    formData.append('uploaded_folder', file)

    const response = await api.post('/cases/upload', formData, {
      params: {
        beneficiary_name: beneficiaryName,  // Send as query parameter
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Start processing a case
   */
  processCase: async (caseId: number): Promise<{ success: boolean; message: string; case_id: number }> => {
    const response = await api.post(`/cases/${caseId}/process`)
    return response.data
  },

  /**
   * Get case status
   */
  getCaseStatus: async (caseId: number): Promise<CaseStatusResponse> => {
    const response = await api.get(`/cases/${caseId}/status`)
    return response.data
  },

  /**
   * Preview generated letter
   */
  previewLetter: async (caseId: number): Promise<LetterPreviewResponse> => {
    const response = await api.get(`/cases/${caseId}/preview`)
    return response.data
  },

  /**
   * Get download links for generated files
   */
  getDownloadLinks: async (caseId: number): Promise<DownloadFilesResponse> => {
    const response = await api.get(`/cases/${caseId}/download`)
    return response.data
  },

  /**
   * List all cases
   */
  listCases: async (skip = 0, limit = 100): Promise<CaseListResponse> => {
    const response = await api.get('/cases', {
      params: { skip, limit },
    })
    return response.data
  },

  /**
   * Delete a case
   */
  deleteCase: async (caseId: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/cases/${caseId}`)
    return response.data
  },
}
