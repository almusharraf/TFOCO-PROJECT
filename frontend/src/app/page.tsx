'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileUpload } from '@/components/FileUpload'
import { EntityDisplay } from '@/components/EntityDisplay'
import { Header } from '@/components/Header'
import { Stats } from '@/components/Stats'
import type { ExtractionResult } from '@/types'

export default function Home() {
  const [result, setResult] = useState<ExtractionResult | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleUpload = (data: ExtractionResult) => {
    setResult(data)
  }

  const handleReset = () => {
    setResult(null)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      <Header />
      
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <div className="text-center mb-12">
                <motion.h1 
                  className="text-5xl md:text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  Financial Document Reader
                </motion.h1>
                <motion.p 
                  className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  Extract structured data from term sheets, trade confirmations, and financial documents with AI-powered Named Entity Recognition
                </motion.p>
              </div>

              <FileUpload 
                onUpload={handleUpload} 
                isProcessing={isProcessing}
                setIsProcessing={setIsProcessing}
              />

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6"
              >
                <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Smart Extraction</h3>
                  <p className="text-gray-600 dark:text-gray-300">Automatically identifies counterparties, notionals, ISINs, dates, and more</p>
                </div>
                <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Lightning Fast</h3>
                  <p className="text-gray-600 dark:text-gray-300">Process documents in seconds with real-time entity highlighting</p>
                </div>
                <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Export Ready</h3>
                  <p className="text-gray-600 dark:text-gray-300">Download extracted data as JSON or CSV for further analysis</p>
                </div>
              </motion.div>
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <Stats result={result} onReset={handleReset} />
              <EntityDisplay result={result} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}

