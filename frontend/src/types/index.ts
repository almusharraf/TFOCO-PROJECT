export interface Entity {
  entity: string
  raw_value: string
  normalized: any
  confidence: number
  char_start: number
  char_end: number
  source: string
  unit?: string | null
}

export interface ExtractionResult {
  filename: string
  file_size: number
  entities: Entity[]
  processing_time_ms: number
  entity_count: number
}

export interface UploadResponse {
  filename: string
  file_size: number
  entities: Entity[]
  processing_time_ms: number
  entity_count: number
}

