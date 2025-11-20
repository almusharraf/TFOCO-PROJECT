'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, FileText, X, Loader2 } from 'lucide-react'
import axios from 'axios'
import type { ExtractionResult } from '@/types'

interface FileUploadProps {
  onUpload: (result: ExtractionResult) => void
  isProcessing: boolean
  setIsProcessing: (value: boolean) => void
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function FileUpload({ onUpload, isProcessing, setIsProcessing }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0])
      setError(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post<ExtractionResult>(
        `${API_URL}/api/v1/extract`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      onUpload(response.data)
    } catch (err: any) {
      console.error('Upload error:', err)
      setError(
        err.response?.data?.detail || 
        'Failed to process document. Please try again.'
      )
    } finally {
      setIsProcessing(false)
    }
  }

  const handleRemove = () => {
    setSelectedFile(null)
    setError(null)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div
          {...getRootProps()}
          className={`
            relative overflow-hidden
            border-2 border-dashed rounded-3xl p-12
            transition-all duration-300 cursor-pointer
            ${isDragActive 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 scale-105' 
              : 'border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600'
            }
            ${selectedFile ? 'bg-white dark:bg-slate-800' : 'bg-white/50 dark:bg-slate-800/50'}
          `}
        >
          <input {...getInputProps()} />
          
          {!selectedFile ? (
            <div className="text-center">
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="inline-block"
              >
                <Upload className="w-16 h-16 mx-auto mb-4 text-blue-600 dark:text-blue-400" />
              </motion.div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                {isDragActive ? 'Drop your file here' : 'Upload a document'}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                Drag & drop or click to browse
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Supports PDF, DOCX, TXT up to 10MB
              </p>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                  <FileText className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleRemove()
                }}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
            </div>
          )}
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl"
          >
            <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
          </motion.div>
        )}

        {selectedFile && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
          >
            <button
              onClick={handleUpload}
              disabled={isProcessing}
              className={`
                w-full py-4 px-6 rounded-2xl font-semibold text-white
                bg-gradient-to-r from-blue-600 to-indigo-600
                hover:from-blue-700 hover:to-indigo-700
                transform transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                ${!isProcessing && 'hover:scale-105 shadow-lg hover:shadow-xl'}
              `}
            >
              {isProcessing ? (
                <span className="flex items-center justify-center space-x-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Processing...</span>
                </span>
              ) : (
                'Extract Entities'
              )}
            </button>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

