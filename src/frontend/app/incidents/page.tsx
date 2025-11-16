"use client"

import type React from "react"
import { useState, useEffect, useRef, useCallback, useMemo } from "react"
import {
  Search,
  Eye,
  Calendar,
  Sliders,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { ENDPOINTS } from "@/app/api"
import { API_BASE_URL } from "@/app/api"
import { useRouter } from "next/navigation"

interface Publisher {
  name?: string
  version?: string
}

interface Service {
  id?: string
}

interface Anomaly {
  state: string
  description?: string
  confidence_score: number
  pattern?: string
}

interface RelevantState {
  id?: string
  uri?: string
  description?: string
  start_time: string
  end_time?: string
  confidence_score: number
  concern_score: number
  publisher: Publisher
  service?: Service
  anomaly?: Anomaly[]
  state: string // Added the 'state' property
}

const formatTimeRangeDisplay = (startTime: Date, endTime: Date) => {
  const now = new Date()
  const duration = endTime.getTime() - startTime.getTime()

  // Check if it matches common presets
  const presets = [
    { label: "Last 5m", duration: 5 * 60 * 1000 },
    { label: "Last 15m", duration: 15 * 60 * 1000 },
    { label: "Last 30m", duration: 30 * 60 * 1000 },
    { label: "Last 1h", duration: 60 * 60 * 1000 },
    { label: "Last 3h", duration: 3 * 60 * 60 * 1000 },
    { label: "Last 6h", duration: 6 * 60 * 60 * 1000 },
    { label: "Last 12h", duration: 12 * 60 * 60 * 1000 },
    { label: "Last 24h", duration: 24 * 60 * 60 * 1000 },
    { label: "Last 2d", duration: 2 * 24 * 60 * 60 * 1000 },
    { label: "Last 7d", duration: 7 * 24 * 60 * 60 * 1000 },
    { label: "Last 30d", duration: 30 * 24 * 60 * 60 * 1000 },
  ]

  // Check if end time is close to now (within 1 minute) and duration matches a preset
  const isRecentEnd = Math.abs(endTime.getTime() - now.getTime()) < 60 * 1000
  if (isRecentEnd) {
    const matchingPreset = presets.find((preset) => Math.abs(preset.duration - duration) < 60 * 1000)
    if (matchingPreset) {
      return matchingPreset.label
    }
  }

  // For custom ranges, show a concise format
  const isSameDay = startTime.toDateString() === endTime.toDateString()
  if (isSameDay) {
    return `${startTime.toLocaleDateString()} ${startTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} - ${endTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
  } else {
    return `${startTime.toLocaleDateString()} - ${endTime.toLocaleDateString()}`
  }
}

interface TimelineFilterProps {
  annotations: RelevantState[]
  onTimeRangeChange: (startTime: Date, endTime: Date) => void
  selectedStartTime: Date
  selectedEndTime: Date
}

function TimelineFilter({ annotations, onTimeRangeChange, selectedStartTime, selectedEndTime }: TimelineFilterProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState<number | null>(null)
  const [dragEnd, setDragEnd] = useState<number | null>(null)
  const [editingStartDate, setEditingStartDate] = useState(false)
  const [editingEndDate, setEditingEndDate] = useState(false)
  const [timelineWindowStart, setTimelineWindowStart] = useState(() => {
    const now = new Date()
    return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000) // Default to 1 day ago
  })
  const [timelineWindowEnd, setTimelineWindowEnd] = useState(() => new Date())
  const [currentPreset, setCurrentPreset] = useState("Last 30d")

  const timePresets = [
    { label: "Last 5m", duration: 5 * 60 * 1000 },
    { label: "Last 15m", duration: 15 * 60 * 1000 },
    { label: "Last 30m", duration: 30 * 60 * 1000 },
    { label: "Last 1h", duration: 60 * 60 * 1000 },
    { label: "Last 3h", duration: 3 * 60 * 60 * 1000 },
    { label: "Last 6h", duration: 6 * 60 * 60 * 1000 },
    { label: "Last 12h", duration: 12 * 60 * 60 * 1000 },
    { label: "Last 24h", duration: 24 * 60 * 60 * 1000 },
    { label: "Last 2d", duration: 2 * 24 * 60 * 60 * 1000 },
    { label: "Last 7d", duration: 7 * 24 * 60 * 60 * 1000 },
    { label: "Last 30d", duration: 30 * 24 * 60 * 60 * 1000 },
  ]

  const timelineStart = timelineWindowStart
  const timelineEnd = timelineWindowEnd
  const timelineDuration = timelineEnd.getTime() - timelineStart.getTime()

  const navigateBackward = () => {
    const duration = timelineDuration
    setTimelineWindowStart(new Date(timelineWindowStart.getTime() - duration))
    setTimelineWindowEnd(new Date(timelineWindowEnd.getTime() - duration))
    setCurrentPreset("Custom")
  }

  const navigateForward = () => {
    const duration = timelineDuration
    const now = new Date()
    const newEnd = new Date(timelineWindowEnd.getTime() + duration)

    if (newEnd.getTime() <= now.getTime()) {
      setTimelineWindowStart(new Date(timelineWindowStart.getTime() + duration))
      setTimelineWindowEnd(newEnd)
    } else {
      setTimelineWindowEnd(now)
      setTimelineWindowStart(new Date(now.getTime() - duration))
    }
    setCurrentPreset("Custom")
  }

  const jumpToNow = () => {
    const duration = timelineDuration
    const now = new Date()
    setTimelineWindowEnd(now)
    setTimelineWindowStart(new Date(now.getTime() - duration))
    setCurrentPreset("Custom")
  }

  const applyPreset = (preset: { label: string; duration: number }) => {
    const now = new Date()
    setTimelineWindowEnd(now)
    setTimelineWindowStart(new Date(now.getTime() - preset.duration))
    setCurrentPreset(preset.label)
  }

  const refresh = () => {
    if (currentPreset !== "Custom") {
      const preset = timePresets.find((p) => p.label === currentPreset)
      if (preset) {
        applyPreset(preset)
      }
    }
  }

  const zoomIn = () => {
    const currentDuration = timelineWindowEnd.getTime() - timelineWindowStart.getTime()
    const newDuration = currentDuration / 2 // Zoom in by halving the duration
    const center = new Date((timelineWindowStart.getTime() + timelineWindowEnd.getTime()) / 2)

    setTimelineWindowStart(new Date(center.getTime() - newDuration / 2))
    setTimelineWindowEnd(new Date(center.getTime() + newDuration / 2))
    setCurrentPreset("Custom")
  }

  const zoomOut = () => {
    const currentDuration = timelineWindowEnd.getTime() - timelineWindowStart.getTime()
    const newDuration = currentDuration * 2 // Zoom out by doubling the duration
    const center = new Date((timelineWindowStart.getTime() + timelineWindowEnd.getTime()) / 2)

    setTimelineWindowStart(new Date(center.getTime() - newDuration / 2))
    setTimelineWindowEnd(new Date(center.getTime() + newDuration / 2))
    setCurrentPreset("Custom")
  }

  const drawTimeline = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    const dpr = window.devicePixelRatio || 1
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    const { width, height } = { width: rect.width, height: rect.height }
    ctx.clearRect(0, 0, width, height)

    ctx.fillStyle = "#0f172a"
    ctx.fillRect(0, 0, width, height)

    ctx.strokeStyle = "#374151"
    ctx.lineWidth = 1

    // Draw 8 vertical grid lines
    for (let i = 0; i <= 7; i++) {
      const x = (i / 7) * width
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height - 30)
      ctx.stroke()
    }

    ctx.fillStyle = "#e2e8f0"
    ctx.font = "12px system-ui"
    ctx.textAlign = "center"

    for (let i = 0; i <= 7; i++) {
      const x = (i / 7) * width
      const timeAtPosition = new Date(timelineStart.getTime() + (i / 7) * timelineDuration)

      const timeLabel = timeAtPosition.toLocaleString("en-US", {
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })

      const textWidth = ctx.measureText(timeLabel).width
      ctx.fillStyle = "#1e293b"
      ctx.fillRect(x - textWidth / 2 - 4, height - 22, textWidth + 8, 16)

      ctx.fillStyle = "#e2e8f0"
      ctx.fillText(timeLabel, x, height - 10)
    }

    ctx.fillStyle = "#1e293b"
    ctx.fillRect(0, height - 30, width, 30)

    const selectionStartX = Math.max(
      0,
      ((selectedStartTime.getTime() - timelineStart.getTime()) / timelineDuration) * width,
    )
    const selectionEndX = Math.min(
      width,
      ((selectedEndTime.getTime() - timelineStart.getTime()) / timelineDuration) * width,
    )

    if (selectionEndX > selectionStartX && selectionStartX < width && selectionEndX > 0) {
      ctx.fillStyle = "rgba(59, 130, 246, 0.3)"
      ctx.fillRect(selectionStartX, 0, selectionEndX - selectionStartX, height - 30)

      ctx.fillStyle = "#3b82f6"
      ctx.fillRect(selectionStartX, height - 30, selectionEndX - selectionStartX, 30)

      ctx.strokeStyle = "#3b82f6"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(selectionStartX, 0)
      ctx.lineTo(selectionStartX, height - 30)
      ctx.moveTo(selectionEndX, 0)
      ctx.lineTo(selectionEndX, height - 30)
      ctx.stroke()
    }

    if (isDragging && dragStart !== null && dragEnd !== null) {
      const startX = Math.min(dragStart, dragEnd)
      const endX = Math.max(dragStart, dragEnd)
      ctx.fillStyle = "rgba(59, 130, 246, 0.4)"
      ctx.fillRect(startX, 0, endX - startX, height - 30)

      ctx.strokeStyle = "#60a5fa"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(startX, 0)
      ctx.lineTo(startX, height - 30)
      ctx.moveTo(endX, 0)
      ctx.lineTo(endX, height - 30)
      ctx.stroke()
    }

    // Group annotations by concern level for proper z-order rendering
    const redAnnotations = annotations.filter((a) => a.concern_score >= 0.8)
    const yellowAnnotations = annotations.filter((a) => a.concern_score >= 0.6 && a.concern_score < 0.8)
    const greenAnnotations = annotations.filter((a) => a.concern_score < 0.6)

    // Draw red bars first (back layer) - tallest
    redAnnotations.forEach((annotation) => {
      const startTime = new Date(annotation.start_time).getTime()
      const endTime = annotation.end_time ? new Date(annotation.end_time).getTime() : Date.now()

      if (startTime <= timelineEnd.getTime() && endTime >= timelineStart.getTime()) {
        const x = Math.max(0, ((startTime - timelineStart.getTime()) / timelineDuration) * width)
        const endX = Math.min(width, ((endTime - timelineStart.getTime()) / timelineDuration) * width)
        const stripeWidth = Math.max(2, endX - x)
        const barHeight = height - 50 // Full height for red (highest concern)

        ctx.fillStyle = "#ef4444"
        ctx.fillRect(x, 10, stripeWidth, barHeight)

        if (!annotation.end_time) {
          ctx.shadowColor = "#ef4444"
          ctx.shadowBlur = 6
          ctx.fillRect(x, 10, stripeWidth, barHeight)
          ctx.shadowBlur = 0
        }

        ctx.strokeStyle = "#ef4444"
        ctx.lineWidth = 1
        ctx.strokeRect(x, 10, stripeWidth, barHeight)
      }
    })

    // Draw yellow bars second (middle layer) - medium height
    yellowAnnotations.forEach((annotation) => {
      const startTime = new Date(annotation.start_time).getTime()
      const endTime = annotation.end_time ? new Date(annotation.end_time).getTime() : Date.now()

      if (startTime <= timelineEnd.getTime() && endTime >= timelineStart.getTime()) {
        const x = Math.max(0, ((startTime - timelineStart.getTime()) / timelineDuration) * width)
        const endX = Math.min(width, ((endTime - timelineStart.getTime()) / timelineDuration) * width)
        const stripeWidth = Math.max(2, endX - x)
        const barHeight = (height - 50) * 0.7 // 70% height for yellow (medium concern)
        const yOffset = 10 + (height - 50) * 0.3 // Start lower to align bottom

        ctx.fillStyle = "#f59e0b"
        ctx.fillRect(x, yOffset, stripeWidth, barHeight)

        if (!annotation.end_time) {
          ctx.shadowColor = "#f59e0b"
          ctx.shadowBlur = 6
          ctx.fillRect(x, yOffset, stripeWidth, barHeight)
          ctx.shadowBlur = 0
        }

        ctx.strokeStyle = "#f59e0b"
        ctx.lineWidth = 1
        ctx.strokeRect(x, yOffset, stripeWidth, barHeight)
      }
    })

    // Draw green bars last (front layer) - shortest height
    greenAnnotations.forEach((annotation) => {
      const startTime = new Date(annotation.start_time).getTime()
      const endTime = annotation.end_time ? new Date(annotation.end_time).getTime() : Date.now()

      if (startTime <= timelineEnd.getTime() && endTime >= timelineStart.getTime()) {
        const x = Math.max(0, ((startTime - timelineStart.getTime()) / timelineDuration) * width)
        const endX = Math.min(width, ((endTime - timelineStart.getTime()) / timelineDuration) * width)
        const stripeWidth = Math.max(2, endX - x)
        const barHeight = (height - 50) * 0.4 // 40% height for green (low concern)
        const yOffset = 10 + (height - 50) * 0.6 // Start much lower to align bottom

        ctx.fillStyle = "#10b981"
        ctx.fillRect(x, yOffset, stripeWidth, barHeight)

        if (!annotation.end_time) {
          ctx.shadowColor = "#10b981"
          ctx.shadowBlur = 6
          ctx.fillRect(x, yOffset, stripeWidth, barHeight)
          ctx.shadowBlur = 0
        }

        ctx.strokeStyle = "#10b981"
        ctx.lineWidth = 1
        ctx.strokeRect(x, yOffset, stripeWidth, barHeight)
      }
    })
  }, [
    annotations,
    timelineStart,
    timelineEnd,
    timelineDuration,
    isDragging,
    dragStart,
    dragEnd,
    selectedStartTime,
    selectedEndTime,
  ])

  useEffect(() => {
    drawTimeline()
  }, [drawTimeline])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const resizeObserver = new ResizeObserver(() => {
      drawTimeline()
    })

    resizeObserver.observe(canvas)
    return () => resizeObserver.disconnect()
  }, [drawTimeline])

  const handleStartDateEdit = (newDate: string) => {
    try {
      const date = new Date(newDate)
      if (!isNaN(date.getTime()) && date < selectedEndTime) {
        onTimeRangeChange(date, selectedEndTime)
      }
    } catch (error) {
      console.error("Invalid date format")
    }
    setEditingStartDate(false)
  }

  const handleEndDateEdit = (newDate: string) => {
    try {
      const date = new Date(newDate)
      if (!isNaN(date.getTime()) && date > selectedStartTime) {
        onTimeRangeChange(selectedStartTime, date)
      }
    } catch (error) {
      console.error("Invalid date format")
    }
    setEditingEndDate(false)
  }

  const formatDateTimeForInput = (date: Date) => {
    return date.toISOString().slice(0, 16)
  }

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    setDragStart(x)
    setIsDragging(true)
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging) return
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    setDragEnd(x)
  }

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging) return
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    setDragEnd(x)
    setIsDragging(false)

    const clampedDragStart = Math.max(0, Math.min(rect.width, dragStart as number))
    const clampedX = Math.max(0, Math.min(rect.width, x))

    const duration = timelineEnd.getTime() - timelineStart.getTime()
    const newStartTime = new Date(timelineStart.getTime() + clampedDragStart * (duration / rect.width))
    const newEndTime = new Date(timelineStart.getTime() + clampedX * (duration / rect.width))
    onTimeRangeChange(newStartTime, newEndTime)
  }

  return (
    <div className="bg-slate-900 rounded-lg border border-slate-700">
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-200">Time Range</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded border border-slate-600">
            <span className="text-sm text-slate-300 font-mono">
              {timelineWindowStart.toLocaleDateString([], { month: "short", day: "numeric" })}{" "}
              {timelineWindowStart.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              {" → "}
              {timelineWindowEnd.toLocaleDateString([], { month: "short", day: "numeric" })}{" "}
              {timelineWindowEnd.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </span>
            <Badge variant="secondary" className="text-xs bg-slate-700 text-slate-300">
              {currentPreset}
            </Badge>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={navigateBackward} className="h-8 w-8 p-0">
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={navigateForward} className="h-8 w-8 p-0">
            <ChevronRight className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={zoomIn} className="h-8 w-8 p-0" title="Zoom in">
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={zoomOut} className="h-8 w-8 p-0" title="Zoom out">
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={jumpToNow} className="h-8 w-8 p-0" title="Jump to now">
            <RotateCcw className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={refresh} className="h-8 w-8 p-0" title="Refresh">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="p-4 border-b border-slate-700">
        <div className="flex flex-wrap gap-2">
          {timePresets.map((preset) => (
            <Button
              key={preset.label}
              variant={currentPreset === preset.label ? "default" : "ghost"}
              size="sm"
              onClick={() => applyPreset(preset)}
              className="text-xs h-7 px-3"
            >
              {preset.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="p-4">
        <div className="text-sm text-slate-400 mb-3">
          Click and drag to select a time range. Vertical bars represent annotation events.
        </div>

        <canvas
          ref={canvasRef}
          className="w-full h-[100px] border border-slate-600 rounded cursor-crosshair bg-slate-950"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        />

        <div className="flex justify-between items-center mt-2 px-1">
          {Array.from({ length: 8 }, (_, i) => {
            const timeAtPosition = new Date(timelineStart.getTime() + (i / 7) * timelineDuration)
            return (
              <div key={i} className="text-xs text-slate-400 text-center flex-1">
                <div className="font-medium">
                  {timeAtPosition.toLocaleDateString("en-US", { month: "short", day: "2-digit" })}
                </div>
                <div className="text-slate-500">
                  {timeAtPosition.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false })}
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex justify-between items-center mt-3 text-xs">
          <div className="text-slate-400">
            Selected:
            {editingStartDate ? (
              <input
                type="datetime-local"
                value={formatDateTimeForInput(selectedStartTime)}
                onChange={(e) => handleStartDateEdit(e.target.value)}
                onBlur={() => setEditingStartDate(false)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleStartDateEdit(e.currentTarget.value)
                  if (e.key === "Escape") setEditingStartDate(false)
                }}
                className="bg-slate-800 border border-slate-600 rounded px-2 py-1 text-slate-200 font-mono text-xs ml-1"
                autoFocus
              />
            ) : (
              <span
                className="text-slate-200 font-mono cursor-pointer hover:text-blue-400 hover:underline ml-1"
                onClick={() => setEditingStartDate(true)}
              >
                {selectedStartTime.toLocaleString()}
              </span>
            )}
          </div>
          <div className="text-slate-400">
            to
            {editingEndDate ? (
              <input
                type="datetime-local"
                value={formatDateTimeForInput(selectedEndTime)}
                onChange={(e) => handleEndDateEdit(e.target.value)}
                onBlur={() => setEditingEndDate(false)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleEndDateEdit(e.currentTarget.value)
                  if (e.key === "Escape") setEditingEndDate(false)
                }}
                className="bg-slate-800 border border-slate-600 rounded px-2 py-1 text-slate-200 font-mono text-xs ml-1"
                autoFocus
              />
            ) : (
              <span
                className="text-slate-200 font-mono cursor-pointer hover:text-blue-400 hover:underline ml-1"
                onClick={() => setEditingEndDate(true)}
              >
                {selectedEndTime.toLocaleString()}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-center gap-6 mt-4 pt-3 border-t border-slate-700">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-sm"></div>
            <span className="text-xs text-slate-400">Low Concern</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-sm"></div>
            <span className="text-xs text-slate-400">Medium Concern</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
            <span className="text-xs text-slate-400">High Concern</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AnnotationsPage() {
  const router = useRouter()
  const [annotations, setAnnotations] = useState<RelevantState[]>([])
  const [filteredAnnotations, setFilteredAnnotations] = useState<RelevantState[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [stateFilter, setStateFilter] = useState("all")

  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  const [sortConfig, setSortConfig] = useState<{
    key: string
    direction: "asc" | "desc"
  } | null>(null)

  const [timelineStartTime, setTimelineStartTime] = useState(() => {
    const now = new Date()
    return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  })
  const [timelineEndTime, setTimelineEndTime] = useState(() => new Date())
  const [concernScoreRange, setConcernScoreRange] = useState<number[]>([0, 1])
  const [confidenceScoreRange, setConfidenceScoreRange] = useState<number[]>([0, 1])
  const [serviceId, setServiceId] = useState("")
  const [annotationId, setAnnotationId] = useState("")
  const [showTimelineFilter, setShowTimelineFilter] = useState(false)
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [editingTopDate, setEditingTopDate] = useState<"start" | "end" | null>(null)
  const [tempTopStartDate, setTempTopStartDate] = useState("")
  const [tempTopEndDate, setTempTopEndDate] = useState("")

  useEffect(
    () => {
      const fetchAnnotations = async () => {
        try {
          setLoading(true)

          const params = new URLSearchParams({
            state: "incident",
            start_time: timelineStartTime.toISOString().slice(0, 10), // Only YYYY-MM-DD
            end_time: timelineEndTime.toISOString().slice(0, 10),
          })

          const response = await fetch(`${API_BASE_URL}${ENDPOINTS.RELEVANT_STATE}?${params.toString()}`, {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          })

          if (!response.ok) {
            throw new Error("Failed to fetch incidents")
          }

          const data = await response.json()
          setAnnotations(data)
          setFilteredAnnotations(data)
          setError(null)
        } catch (err) {
          console.error("API fetch failed:", err)
          setAnnotations([])
          setFilteredAnnotations([])
          setError(err instanceof Error ? err.message : "An error occurred")
        } finally {
          setLoading(false)
        }
      }

      fetchAnnotations()
    },
    [], //, [timelineStartTime, timelineEndTime]
  )

  useEffect(() => {
    let filtered = annotations

    filtered = filtered.filter((annotation) =>
      ["unknown", "forecasted", "potential", "discarded"].includes(annotation.state),
    )

    filtered = filtered.filter((annotation) => {
      const startTime = new Date(annotation.start_time).getTime()
      const endTime = annotation.end_time ? new Date(annotation.end_time).getTime() : Date.now()

      return (
        (startTime >= timelineStartTime.getTime() && startTime <= timelineEndTime.getTime()) ||
        (endTime >= timelineStartTime.getTime() && endTime <= timelineEndTime.getTime()) ||
        (startTime <= timelineStartTime.getTime() && endTime >= timelineEndTime.getTime())
      )
    })

    setFilteredAnnotations(filtered)
  }, [annotations, timelineStartTime, timelineEndTime])

  useEffect(() => {
    let filtered = annotations

    if (searchTerm) {
      filtered = filtered.filter(
        (annotation) =>
          annotation.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          annotation.publisher.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          annotation.uri?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          annotation.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          annotation.service?.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          annotation.anomaly?.some(
            (a) =>
              a.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
              a.pattern?.toLowerCase().includes(searchTerm.toLowerCase()),
          ),
      )
    }

    if (statusFilter === "past") {
      filtered = filtered.filter((annotation) => annotation.end_time !== null && annotation.end_time !== undefined)
    } else if (statusFilter === "ongoing") {
      filtered = filtered.filter((annotation) => annotation.end_time === null || annotation.end_time === undefined)
    }

    if (stateFilter === "confirmed") {
      filtered = filtered.filter((annotation) => annotation.state === "confirmed")
    } else if (stateFilter === "analyzed") {
      filtered = filtered.filter((annotation) => annotation.state === "analyzed")
    } else if (stateFilter === "adjusted") {
      filtered = filtered.filter((annotation) => annotation.state === "adjusted")
    }
    // If stateFilter is "all", no additional filtering is applied

    filtered = filtered.filter((annotation) => {
      const startTime = new Date(annotation.start_time).getTime()
      const endTime = annotation.end_time ? new Date(annotation.end_time).getTime() : Date.now()

      return (
        (startTime >= timelineStartTime.getTime() && startTime <= timelineEndTime.getTime()) ||
        (endTime >= timelineStartTime.getTime() && endTime <= timelineEndTime.getTime()) ||
        (startTime <= timelineStartTime.getTime() && endTime >= timelineEndTime.getTime())
      )
    })

    filtered = filtered.filter(
      (annotation) =>
        annotation.concern_score >= concernScoreRange[0] && annotation.concern_score <= concernScoreRange[1],
    )

    filtered = filtered.filter(
      (annotation) =>
        !annotation.confidence_score ||
        (annotation.confidence_score >= confidenceScoreRange[0] &&
          annotation.confidence_score <= confidenceScoreRange[1]),
    )

    if (serviceId) {
      filtered = filtered.filter((annotation) =>
        annotation.service?.id?.toLowerCase().includes(serviceId.toLowerCase()),
      )
    }

    if (annotationId) {
      filtered = filtered.filter((annotation) => annotation.id?.toLowerCase().includes(annotationId.toLowerCase()))
    }

    setFilteredAnnotations(filtered)
  }, [
    searchTerm,
    statusFilter,
    stateFilter,
    annotations,
    timelineStartTime,
    timelineEndTime,
    concernScoreRange,
    confidenceScoreRange,
    serviceId,
    annotationId,
  ])

  const getConcernColor = (score: number) => {
    if (score >= 0.8) return "text-red-400"
    if (score >= 0.6) return "text-yellow-400"
    return "text-green-400"
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const clearTimelineFilters = () => {
    const now = new Date()
    const dayAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    setTimelineStartTime(dayAgo)
    setTimelineEndTime(now)
  }

  const clearAllFilters = () => {
    clearTimelineFilters()
    setConcernScoreRange([0, 1])
    setConfidenceScoreRange([0, 1])
    setServiceId("")
    setAnnotationId("")
    setStateFilter("all")
  }

  const handleTimeRangeChange = (startTime: Date, endTime: Date) => {
    setTimelineStartTime(startTime)
    setTimelineEndTime(endTime)
  }

  const handleTopDateEdit = (type: "start" | "end") => {
    if (type === "start") {
      setTempTopStartDate(timelineStartTime.toISOString().slice(0, 16))
    } else {
      setTempTopEndDate(timelineEndTime.toISOString().slice(0, 16))
    }
    setEditingTopDate(type)
  }

  const handleTopDateSave = () => {
    if (editingTopDate === "start" && tempTopStartDate) {
      const newStart = new Date(tempTopStartDate)
      if (newStart < timelineEndTime) {
        setTimelineStartTime(newStart)
      }
    } else if (editingTopDate === "end" && tempTopEndDate) {
      const newEnd = new Date(tempTopEndDate)
      if (newEnd > timelineStartTime) {
        setTimelineEndTime(newEnd)
      }
    }
    setEditingTopDate(null)
  }

  const handleTopDateCancel = () => {
    setEditingTopDate(null)
    setTempTopStartDate("")
    setTempTopEndDate("")
  }

  const getActiveFiltersCount = () => {
    let count = 0
    const now = new Date()
    const dayAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

    // Only count timeline as active if it's significantly different from default (more than 5 minutes)
    const timeDiffStart = Math.abs(timelineStartTime.getTime() - dayAgo.getTime())
    const timeDiffEnd = Math.abs(timelineEndTime.getTime() - now.getTime())
    if (timeDiffStart > 5 * 60 * 1000 || timeDiffEnd > 5 * 60 * 1000) count++

    if (concernScoreRange[0] !== 0 || concernScoreRange[1] !== 1) count++
    if (confidenceScoreRange[0] !== 0 || confidenceScoreRange[1] !== 1) count++
    if (serviceId) count++
    if (annotationId) count++
    return count
  }

  const handleSort = (key: string) => {
    let direction: "asc" | "desc" = "asc"
    if (sortConfig && sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc"
    }
    setSortConfig({ key, direction })
  }

  const sortedAnnotations = useMemo(() => {
    if (!sortConfig) return filteredAnnotations

    return [...filteredAnnotations].sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortConfig.key) {
        case "description":
          aValue = a.description || ""
          bValue = b.description || ""
          break
        case "concern_score":
          aValue = a.concern_score
          bValue = b.concern_score
          break
        case "confidence_score":
          aValue = a.confidence_score || 0
          bValue = b.confidence_score || 0
          break
        case "publisher":
          aValue = a.publisher.name || ""
          bValue = b.publisher.name || ""
          break
        case "service":
          aValue = a.service?.id || ""
          bValue = b.service?.id || ""
          break
        case "state":
          aValue = a.state || ""
          bValue = b.state || ""
          break
        case "start_time":
          aValue = new Date(a.start_time)
          bValue = new Date(b.start_time)
          break
        case "end_time":
          aValue = a.end_time ? new Date(a.end_time) : new Date(0)
          bValue = b.end_time ? new Date(b.end_time) : new Date(0)
          break
        default:
          return 0
      }

      if (aValue < bValue) {
        return sortConfig.direction === "asc" ? -1 : 1
      }
      if (aValue > bValue) {
        return sortConfig.direction === "asc" ? 1 : -1
      }
      return 0
    })
  }, [filteredAnnotations, sortConfig])

  const totalPages = Math.ceil(sortedAnnotations.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedAnnotations = sortedAnnotations.slice(startIndex, endIndex)

  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, statusFilter, stateFilter, concernScoreRange, confidenceScoreRange, serviceId, annotationId])

  const SortIcon = ({ column }: { column: string }) => {
    if (!sortConfig || sortConfig.key !== column) {
      return <ArrowUpDown className="w-4 h-4 ml-1 text-gray-500" />
    }
    return sortConfig.direction === "asc" ? (
      <ArrowUp className="w-4 h-4 ml-1 text-blue-400" />
    ) : (
      <ArrowDown className="w-4 h-4 ml-1 text-blue-400" />
    )
  }

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(totalPages, page)))
  }

  const goToPreviousPage = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1))
  }

  const goToNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages, prev + 1))
  }

  if (loading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading incidents...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Incidents</h1>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search incidents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-card border-border"
          />
        </div>
        <Button
          variant="outline"
          className="border-border bg-card"
          onClick={() => setShowTimelineFilter(!showTimelineFilter)}
        >
          <Calendar className="w-4 h-4 mr-2" />
          Timeline Filter
          <span className="ml-2 text-xs text-muted-foreground font-mono">
            ({formatTimeRangeDisplay(timelineStartTime, timelineEndTime)})
          </span>
        </Button>
        <Button
          variant="outline"
          className="border-border bg-card relative"
          onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
        >
          <Sliders className="w-4 h-4 mr-2" />
          Advanced Filters
          {getActiveFiltersCount() > 0 && (
            <Badge className="ml-2 bg-blue-600 text-white text-xs px-1.5 py-0.5 min-w-[1.25rem] h-5">
              {getActiveFiltersCount()}
            </Badge>
          )}
        </Button>
      </div>

      {showTimelineFilter && (
        <div className="mb-6">
          <TimelineFilter
            annotations={annotations}
            onTimeRangeChange={handleTimeRangeChange}
            selectedStartTime={timelineStartTime}
            selectedEndTime={timelineEndTime}
          />
        </div>
      )}

      {showAdvancedFilters && (
        <div className="bg-card rounded-lg p-4 mb-6 border border-border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium flex items-center gap-2">
              <Sliders className="w-4 h-4" />
              Advanced Filters
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllFilters}
              className="text-muted-foreground hover:text-foreground"
            >
              Clear All Filters
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground">Concern Score Range</h4>
              <div className="space-y-3">
                <div className="px-2">
                  <Slider
                    value={concernScoreRange}
                    onValueChange={setConcernScoreRange}
                    max={1}
                    min={0}
                    step={0.01}
                    className="w-full [&_[role=slider]]:bg-white [&_[role=slider]]:border-white [&_.slider-track]:bg-gray-600 [&_.slider-range]:bg-white [&>span:first-child]:bg-gray-600 [&>span:last-child]:bg-gray-600 [&>span:nth-child(2)]:bg-white"
                  />
                </div>
                <div className="flex gap-2 items-center">
                  <div className="flex-1">
                    <Label className="text-xs text-muted-foreground mb-1 block">Min</Label>
                    <Input
                      type="number"
                      min={0}
                      max={1}
                      step={0.01}
                      value={concernScoreRange[0]}
                      onChange={(e) => {
                        const value = Math.max(0, Math.min(1, Number.parseFloat(e.target.value) || 0))
                        setConcernScoreRange([value, Math.max(value, concernScoreRange[1])])
                      }}
                      className="bg-muted border-border text-sm h-8"
                    />
                  </div>
                  <div className="flex-1">
                    <Label className="text-xs text-muted-foreground mb-1 block">Max</Label>
                    <Input
                      type="number"
                      min={0}
                      max={1}
                      step={0.01}
                      value={concernScoreRange[1]}
                      onChange={(e) => {
                        const value = Math.max(0, Math.min(1, Number.parseFloat(e.target.value) || 0))
                        setConcernScoreRange([Math.min(concernScoreRange[0], value), value])
                      }}
                      className="bg-muted border-border text-sm h-8"
                    />
                  </div>
                </div>
                <div className="text-xs text-center text-muted-foreground">
                  {(concernScoreRange[0] * 100).toFixed(0)}% - {(concernScoreRange[1] * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground">Confidence Score Range</h4>
              <div className="space-y-3">
                <div className="px-2">
                  <Slider
                    value={confidenceScoreRange}
                    onValueChange={setConfidenceScoreRange}
                    max={1}
                    min={0}
                    step={0.01}
                    className="w-full [&_[role=slider]]:bg-white [&_[role=slider]]:border-white [&_.slider-track]:bg-gray-600 [&_.slider-range]:bg-white [&>span:first-child]:bg-gray-600 [&>span:last-child]:bg-gray-600 [&>span:nth-child(2)]:bg-white"
                  />
                </div>
                <div className="flex gap-2 items-center">
                  <div className="flex-1">
                    <Label className="text-xs text-muted-foreground mb-1 block">Min</Label>
                    <Input
                      type="number"
                      min={0}
                      max={1}
                      step={0.01}
                      value={confidenceScoreRange[0]}
                      onChange={(e) => {
                        const value = Math.max(0, Math.min(1, Number.parseFloat(e.target.value) || 0))
                        setConfidenceScoreRange([value, Math.max(value, confidenceScoreRange[1])])
                      }}
                      className="bg-muted border-border text-sm h-8"
                    />
                  </div>
                  <div className="flex-1">
                    <Label className="text-xs text-muted-foreground mb-1 block">Max</Label>
                    <Input
                      type="number"
                      min={0}
                      max={1}
                      step={0.01}
                      value={confidenceScoreRange[1]}
                      onChange={(e) => {
                        const value = Math.max(0, Math.min(1, Number.parseFloat(e.target.value) || 0))
                        setConfidenceScoreRange([Math.min(confidenceScoreRange[0], value), value])
                      }}
                      className="bg-muted border-border text-sm h-8"
                    />
                  </div>
                </div>
                <div className="text-xs text-center text-muted-foreground">
                  {(confidenceScoreRange[0] * 100).toFixed(0)}% - {(confidenceScoreRange[1] * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">Identifiers</h4>
              <div className="space-y-2">
                <div>
                  <Label className="text-xs text-muted-foreground mb-1 block">Incident ID</Label>
                  <Input
                    placeholder="Filter by Incident ID..."
                    value={annotationId}
                    onChange={(e) => setAnnotationId(e.target.value)}
                    className="bg-muted border-border text-sm"
                  />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground mb-1 block">Service ID</Label>
                  <Input
                    placeholder="Filter by service ID..."
                    value={serviceId}
                    onChange={(e) => setServiceId(e.target.value)}
                    className="bg-muted border-border text-sm"
                  />
                </div>
              </div>
            </div>
          </div>

          {(concernScoreRange[0] !== 0 ||
            concernScoreRange[1] !== 1 ||
            confidenceScoreRange[0] !== 0 ||
            confidenceScoreRange[1] !== 1 ||
            serviceId ||
            annotationId) && (
            <div className="mt-4 pt-3 border-t border-border">
              <div className="flex flex-wrap gap-2">
                {(concernScoreRange[0] !== 0 || concernScoreRange[1] !== 1) && (
                  <Badge variant="secondary" className="text-xs">
                    Concern: {(concernScoreRange[0] * 100).toFixed(0)}% - {(concernScoreRange[1] * 100).toFixed(0)}%
                  </Badge>
                )}
                {(confidenceScoreRange[0] !== 0 || confidenceScoreRange[1] !== 1) && (
                  <Badge variant="secondary" className="text-xs">
                    Confidence: {(confidenceScoreRange[0] * 100).toFixed(0)}% -{" "}
                    {(confidenceScoreRange[1] * 100).toFixed(0)}%
                  </Badge>
                )}
                {serviceId && (
                  <Badge variant="secondary" className="text-xs">
                    Service: {serviceId}
                  </Badge>
                )}
                {annotationId && (
                  <Badge variant="secondary" className="text-xs">
                    ID: {annotationId}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex items-center gap-6 mb-6">
        {/* Time-based filters */}
        <div className="flex gap-2">
          <Button
            variant={statusFilter === "all" ? "default" : "ghost"}
            onClick={() => setStatusFilter("all")}
            className="text-sm"
          >
            All
          </Button>
          <Button
            variant={statusFilter === "past" ? "default" : "ghost"}
            onClick={() => setStatusFilter("past")}
            className="text-sm"
          >
            Past
          </Button>
          <Button
            variant={statusFilter === "ongoing" ? "default" : "ghost"}
            onClick={() => setStatusFilter("ongoing")}
            className="text-sm"
          >
            Still ongoing
          </Button>
        </div>

        {/* State-based filters */}
        <div className="flex items-center gap-2">
          <div className="text-sm text-muted-foreground">State:</div>
          <Button
            variant={stateFilter === "all" ? "default" : "ghost"}
            onClick={() => setStateFilter("all")}
            className="text-sm"
          >
            All States
          </Button>
          <Button
            variant={stateFilter === "confirmed" ? "default" : "ghost"}
            onClick={() => setStateFilter("confirmed")}
            className="text-sm"
          >
            Confirmed
          </Button>
          <Button
            variant={stateFilter === "analyzed" ? "default" : "ghost"}
            onClick={() => setStateFilter("analyzed")}
            className="text-sm"
          >
            Analyzed
          </Button>
          <Button
            variant={stateFilter === "adjusted" ? "default" : "ghost"}
            onClick={() => setStateFilter("adjusted")}
            className="text-sm"
          >
            Adjusted
          </Button>
        </div>
      </div>

      <div className="bg-card rounded-lg p-6 border border-border">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-foreground mb-2">Incident Management</h2>
          <p className="text-muted-foreground">View and manage detected incidents</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900/20 border border-red-800 rounded text-red-400">
            {error}
          </div>
        )}

        <div className="border border-border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-border hover:bg-muted/50">
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("description")}
                  >
                    <div className="flex items-center">
                      Description
                      <SortIcon column="description" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("concern_score")}
                  >
                    <div className="flex items-center">
                      Concern Score
                      <SortIcon column="concern_score" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("confidence_score")}
                  >
                    <div className="flex items-center">
                      Confidence
                      <SortIcon column="confidence_score" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("publisher")}
                  >
                    <div className="flex items-center">
                      Publisher
                      <SortIcon column="publisher" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("service")}
                  >
                    <div className="flex items-center">
                      Service
                      <SortIcon column="service" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("state")}
                  >
                    <div className="flex items-center">
                      State
                      <SortIcon column="state" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("start_time")}
                  >
                    <div className="flex items-center">
                      Start time
                      <SortIcon column="start_time" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleSort("end_time")}
                  >
                    <div className="flex items-center">
                      End time
                      <SortIcon column="end_time" />
                    </div>
                  </TableHead>
                  <TableHead className="text-muted-foreground sticky right-0 bg-card border-l border-border min-w-[120px]">
                    Actions
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedAnnotations.map((annotation) => (
                  <TableRow key={annotation.id} className="border-border hover:bg-muted/30">
                    <TableCell className="font-medium max-w-xs truncate text-foreground">
                      {annotation.description || "No description"}
                    </TableCell>
                    <TableCell>
                      <span className={`font-medium ${getConcernColor(annotation.concern_score)}`}>
                        {(annotation.concern_score * 100).toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell>
                      {annotation.confidence_score ? (
                        <span className="font-medium text-blue-400">
                          {(annotation.confidence_score * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-medium text-foreground">{annotation.publisher.name || "Unknown"}</span>
                        <span className="text-xs text-muted-foreground">
                          {annotation.publisher.version || "No version"}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {annotation.service?.id ? (
                        <Badge variant="secondary" className="text-xs">
                          {annotation.service.id}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className="font-medium text-foreground">{annotation.state}</span>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDateTime(annotation.start_time)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {annotation.end_time ? formatDateTime(annotation.end_time) : "Ongoing"}
                    </TableCell>
                    <TableCell className="sticky right-0 bg-card border-l border-border">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-8 px-2"
                          onClick={() => router.push(`/incidents/${annotation.id}`)}
                        >
                          <Eye className="w-3 h-3 mr-1" />
                          View
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-6 py-4 border-t border-border">
              <div className="text-sm text-muted-foreground">
                Showing {startIndex + 1} to {Math.min(endIndex, sortedAnnotations.length)} of {sortedAnnotations.length}{" "}
                results
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={goToPreviousPage}
                  disabled={currentPage === 1}
                  className="border-border bg-transparent"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNumber
                    if (totalPages <= 5) {
                      pageNumber = i + 1
                    } else if (currentPage <= 3) {
                      pageNumber = i + 1
                    } else if (currentPage >= totalPages - 2) {
                      pageNumber = totalPages - 4 + i
                    } else {
                      pageNumber = currentPage - 2 + i
                    }

                    return (
                      <Button
                        key={pageNumber}
                        variant={currentPage === pageNumber ? "default" : "ghost"}
                        size="sm"
                        onClick={() => goToPage(pageNumber)}
                        className="w-8 h-8 p-0"
                      >
                        {pageNumber}
                      </Button>
                    )
                  })}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={goToNextPage}
                  disabled={currentPage === totalPages}
                  className="border-border bg-transparent"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {filteredAnnotations.length === 0 && !loading && (
          <div className="text-center py-8 text-muted-foreground">No incidents found matching your criteria.</div>
        )}
      </div>
    </div>
  )
}
