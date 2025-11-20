'use client'

import { motion } from 'framer-motion'
import { Download, TrendingUp } from 'lucide-react'
import type { ExtractionResult, Entity } from '@/types'
import { EntityCard } from './EntityCard'

interface EntityDisplayProps {
  result: ExtractionResult
}

const entityTypeColors: Record<string, { bg: string; border: string; text: string }> = {
  Counterparty: { bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-800', text: 'text-blue-700 dark:text-blue-300' },
  Notional: { bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-200 dark:border-green-800', text: 'text-green-700 dark:text-green-300' },
  ISIN: { bg: 'bg-purple-50 dark:bg-purple-900/20', border: 'border-purple-200 dark:border-purple-800', text: 'text-purple-700 dark:text-purple-300' },
  TradeDate: { bg: 'bg-orange-50 dark:bg-orange-900/20', border: 'border-orange-200 dark:border-orange-800', text: 'text-orange-700 dark:text-orange-300' },
  Underlying: { bg: 'bg-indigo-50 dark:bg-indigo-900/20', border: 'border-indigo-200 dark:border-indigo-800', text: 'text-indigo-700 dark:text-indigo-300' },
  Barrier: { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-800', text: 'text-red-700 dark:text-red-300' },
  Offer: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', border: 'border-yellow-200 dark:border-yellow-800', text: 'text-yellow-700 dark:text-yellow-300' },
  default: { bg: 'bg-gray-50 dark:bg-gray-800', border: 'border-gray-200 dark:border-gray-700', text: 'text-gray-700 dark:text-gray-300' },
}

export function EntityDisplay({ result }: EntityDisplayProps) {
  const downloadJSON = () => {
    const dataStr = JSON.stringify(result, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${result.filename}_entities.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const downloadCSV = () => {
    const headers = ['Entity', 'Raw Value', 'Normalized', 'Confidence', 'Position']
    const rows = result.entities.map(e => [
      e.entity,
      e.raw_value,
      typeof e.normalized === 'object' ? JSON.stringify(e.normalized) : e.normalized,
      e.confidence.toFixed(2),
      `${e.char_start}-${e.char_end}`
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')
    
    const dataBlob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${result.filename}_entities.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  // Group entities by type
  const groupedEntities = result.entities.reduce((acc, entity) => {
    if (!acc[entity.entity]) {
      acc[entity.entity] = []
    }
    acc[entity.entity].push(entity)
    return acc
  }, {} as Record<string, Entity[]>)

  const avgConfidence = result.entities.reduce((sum, e) => sum + e.confidence, 0) / result.entity_count

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-lg"
      >
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
            <span className="text-sm text-gray-600 dark:text-gray-300">
              Avg. Confidence: <span className="font-bold text-gray-900 dark:text-white">{(avgConfidence * 100).toFixed(1)}%</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={downloadJSON}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm font-medium">JSON</span>
          </button>
          <button
            onClick={downloadCSV}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl transition-colors"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm font-medium">CSV</span>
          </button>
        </div>
      </motion.div>

      {/* Entity Groups */}
      <div className="space-y-4">
        {Object.entries(groupedEntities).map(([entityType, entities], groupIndex) => {
          const colors = entityTypeColors[entityType] || entityTypeColors.default
          
          return (
            <motion.div
              key={entityType}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: groupIndex * 0.1 }}
              className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg overflow-hidden"
            >
              <div className={`px-6 py-4 ${colors.bg} border-l-4 ${colors.border}`}>
                <div className="flex items-center justify-between">
                  <h3 className={`text-lg font-bold ${colors.text}`}>
                    {entityType}
                  </h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors.bg} ${colors.text}`}>
                    {entities.length} found
                  </span>
                </div>
              </div>

              <div className="p-6 space-y-3">
                {entities.map((entity, index) => (
                  <EntityCard
                    key={`${entity.entity}-${index}`}
                    entity={entity}
                    index={index}
                    colors={colors}
                  />
                ))}
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Empty State */}
      {result.entity_count === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white dark:bg-slate-800 rounded-2xl p-12 text-center shadow-lg"
        >
          <p className="text-gray-500 dark:text-gray-400 text-lg">
            No entities found in this document.
          </p>
        </motion.div>
      )}
    </div>
  )
}

