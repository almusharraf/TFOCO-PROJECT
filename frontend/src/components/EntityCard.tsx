'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, MapPin } from 'lucide-react'
import type { Entity } from '@/types'

interface EntityCardProps {
  entity: Entity
  index: number
  colors: { bg: string; border: string; text: string }
}

export function EntityCard({ entity, index, colors }: EntityCardProps) {
  const formatNormalized = (normalized: any) => {
    if (normalized === null || normalized === undefined) return entity.raw_value
    
    if (typeof normalized === 'object') {
      return (
        <div className="space-y-1">
          {Object.entries(normalized).map(([key, value]) => (
            <div key={key} className="flex items-center space-x-2 text-sm">
              <span className="text-gray-500 dark:text-gray-400">{key}:</span>
              <span className="font-mono text-gray-900 dark:text-white">
                {typeof value === 'number' ? value.toLocaleString() : String(value)}
              </span>
            </div>
          ))}
        </div>
      )
    }
    
    return String(normalized)
  }

  const confidenceColor = entity.confidence >= 0.9 
    ? 'text-green-600 dark:text-green-400' 
    : entity.confidence >= 0.7 
    ? 'text-yellow-600 dark:text-yellow-400' 
    : 'text-red-600 dark:text-red-400'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:shadow-md transition-shadow bg-gray-50 dark:bg-slate-900/50"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {/* Raw Value */}
          <div className="mb-3">
            <span className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Raw Value</span>
            <p className="text-lg font-semibold text-gray-900 dark:text-white mt-1">
              "{entity.raw_value}"
            </p>
          </div>

          {/* Normalized Value */}
          {entity.normalized && entity.normalized !== entity.raw_value && (
            <div className="mb-3">
              <span className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Normalized</span>
              <div className="mt-1 text-gray-700 dark:text-gray-200">
                {formatNormalized(entity.normalized)}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <MapPin className="w-3 h-3" />
              <span>Position: {entity.char_start}-{entity.char_end}</span>
            </div>
            {entity.unit && (
              <div>
                <span className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded">
                  {entity.unit}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Confidence Badge */}
        <div className="ml-4 flex flex-col items-end space-y-2">
          <div className={`flex items-center space-x-1 ${confidenceColor}`}>
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-sm font-bold">
              {(entity.confidence * 100).toFixed(0)}%
            </span>
          </div>
          
          {/* Confidence Bar */}
          <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${entity.confidence * 100}%` }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className={`h-full ${
                entity.confidence >= 0.9 
                  ? 'bg-green-500' 
                  : entity.confidence >= 0.7 
                  ? 'bg-yellow-500' 
                  : 'bg-red-500'
              }`}
            />
          </div>
        </div>
      </div>
    </motion.div>
  )
}

