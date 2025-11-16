"use client"
import { useState, useEffect, useRef } from "react"
import { ENDPOINTS } from "@/app/api"
import type React from "react"

import { useParams, useRouter } from "next/navigation"
import {
  ArrowLeft,
  Save,
  Edit3,
  AlertTriangle,
  Info,
  Activity,
  Clock,
  Server,
  FileText,
  BarChart3,
  CheckCircle,
  XCircle,
  AlertCircle,
  HelpCircle,
  Plus,
  Trash2,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ReferenceArea } from "recharts"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import type { RelevantState } from "@/lib/shared-types"
import { localDateToUTC, formatDateTime as formatDateTimeDisplay } from "@/lib/timezone-utils"

// Backend API base URL and endpoint
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
// Use the correct endpoint for relevant state edits
const RELEVANT_STATE_ENDPOINT = ENDPOINTS.RELEVANT_STATE
const RELEVANT_STATE_ENDPOINT_TELEMETRY = ENDPOINTS.RELEVANT_STATE_TELEMETRY

type AnnotationBox = {
  id: string
  x1: number
  x2: number
  color: string
}

export default function IncidentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [incident, setIncident] = useState<RelevantState | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [editedIncident, setEditedIncident] = useState<RelevantState | null>(null)

  const [editingSymptomIndex, setEditingSymptomIndex] = useState<number | null>(null)
  const [editedSymptom, setEditedSymptom] = useState<any>(null)
  const [annotations, setAnnotations] = useState<AnnotationBox[]>([])
  const [isDrawing, setIsDrawing] = useState(false)
  const [drawStart, setDrawStart] = useState<number | null>(null)
  const [drawEnd, setDrawEnd] = useState<number | null>(null)
  const chartRef = useRef<any>(null)

  // Extract fetchIncident so it can be reused after PUTs
  const fetchIncident = async () => {
    try {
      setLoading(true)

      try {
        console.log(
          "Attempting to fetch from backend:",
          `${API_BASE_URL}${RELEVANT_STATE_ENDPOINT_TELEMETRY}/${params.id}`,
        )

        const response = await fetch(`${API_BASE_URL}${RELEVANT_STATE_ENDPOINT_TELEMETRY}/${params.id}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (response.ok) {
          const data = await response.json()
          console.log("Successfully fetched from backend:", data)
          setIncident(data)
          setEditedIncident(data)
          setError(null)
          return
        } else {
          console.log("Backend responded with error:", response.status, response.statusText)
          throw new Error(`Backend error: ${response.status}`)
        }
      } catch (backendError) {
        console.error("Backend fetch failed:", backendError)
        throw backendError
      }
    } catch (err) {
      console.log("Error in fetchIncident:", err)
      setError("Failed to load incident data")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (params.id) {
      fetchIncident()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id])

  // Utility to get changed fields according to custom rules
  function getChangedFields(original: any, edited: any) {
    const changed: any = {}
    // Always include id if present
    if (edited.id) {
      changed.id = edited.id
    }
    // Remove publisher and service from payload
    const skipKeys = ["publisher", "service", "id"]
    for (const key in edited) {
      if (skipKeys.includes(key)) continue
      // Special handling for anomaly array (symptoms)
      if (key === "anomaly" && Array.isArray(edited.anomaly) && Array.isArray(original.anomaly)) {
        // Check if any symptoms were modified
        let symptomsModified = false

        // Check for length changes (added/removed symptoms)
        if (original.anomaly.length !== edited.anomaly.length) {
          symptomsModified = true
        }

        // Build map of original symptoms by id for quick lookup
        const originalSymptomMap = new Map()
        original.anomaly.forEach((a: any) => {
          if (a.id) {
            originalSymptomMap.set(a.id.toString(), a)
          }
        })

        // Track which symptoms are modified
        const modifiedSymptomIds = new Set<string>()

        // Check each edited symptom
        for (const editedSymptom of edited.anomaly) {
          if (editedSymptom.id) {
            const originalSymptom = originalSymptomMap.get(editedSymptom.id.toString())
            if (originalSymptom) {
              // Compare symptoms deeply to detect changes
              if (JSON.stringify(originalSymptom) !== JSON.stringify(editedSymptom)) {
                symptomsModified = true
                modifiedSymptomIds.add(editedSymptom.id.toString())
              }
            } else {
              // Symptom with ID not found in original - shouldn't happen but treat as modified
              symptomsModified = true
            }
          } else {
            // New symptom without ID
            symptomsModified = true
          }
        }

        // Check for removed symptoms
        const editedSymptomIds = new Set(edited.anomaly.map((a: any) => a.id?.toString()).filter(Boolean))
        for (const originalSymptom of original.anomaly) {
          if (originalSymptom.id && !editedSymptomIds.has(originalSymptom.id.toString())) {
            symptomsModified = true
            break
          }
        }

        if (symptomsModified) {
          // Build the anomaly array to send
          changed.anomaly = edited.anomaly.map((a: any) => {
            if (a.id && !modifiedSymptomIds.has(a.id.toString())) {
              // Unmodified symptom: send full object including id
              return a
            } else {
              // Modified or new symptom: send all fields except id
              const { id, ...rest } = a
              return rest
            }
          })
        } else {
          // No symptoms modified: set anomaly to null
          changed.anomaly = null
        }
        continue
      }
      // Only send start_time, end_time, confidence_score, concern_score if changed
      if (["start_time", "end_time", "confidence_score", "concern_score"].includes(key)) {
        if (edited[key] !== original[key]) {
          changed[key] = edited[key]
        }
        continue
      }
      // Default: send if changed
      if (typeof edited[key] === "object" && edited[key] !== null && original[key]) {
        const nested = getChangedFields(original[key], edited[key])
        if (Object.keys(nested).length > 0) changed[key] = nested
      } else if (edited[key] !== original[key]) {
        changed[key] = edited[key]
      }
    }
    return changed
  }

  const handleSave = async () => {
    if (!editedIncident || !incident) return

    try {
      setIsSaving(true)

      // Check which fields changed (for anomaly field logic)
      const changedFields = getChangedFields(incident, editedIncident)

      // Build payload with all required fields from RelevantState model
      const payload: any = {
        id: editedIncident.id,
        revision: (incident.revision ?? 0) + 1,
        uri: editedIncident.uri,
        description: editedIncident.description,
        start_time: editedIncident.start_time,
        end_time: editedIncident.end_time,
        state: editedIncident.state,
        confidence_score: editedIncident.confidence_score,
        concern_score: editedIncident.concern_score,
        publisher: editedIncident.publisher,
        service: editedIncident.service,
      }

      // Include anomaly field based on whether symptoms were modified
      if ("anomaly" in changedFields) {
        payload.anomaly = changedFields.anomaly
      } else {
        payload.anomaly = null
      }

      console.log("handleSave - Payload being sent:", JSON.stringify(payload, null, 2))

      const response = await fetch(`${API_BASE_URL}${RELEVANT_STATE_ENDPOINT}/${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error("Failed to save incident")
      }

      // Instead of using the response, always reload from backend
      await fetchIncident()
      setIsEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save changes")
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setEditedIncident(incident)
    setIsEditing(false)
  }

  const handleMarkAsFalsePositive = async () => {
    if (!incident) return

    try {
      setIsSaving(true)

      // Determine if we're working with edited or original data
      const current = isEditing && editedIncident ? editedIncident : incident

      // Check if symptoms were modified using getChangedFields
      const changedFields = isEditing && editedIncident ? getChangedFields(incident, editedIncident) : {}

      // Build payload with all required fields from RelevantState model
      const payload: any = {
        id: current.id,
        revision: (incident.revision ?? 0) + 1,
        uri: current.uri,
        description: current.description,
        start_time: current.start_time,
        end_time: current.end_time,
        state: "discarded",
        confidence_score: current.confidence_score,
        concern_score: current.concern_score,
        publisher: current.publisher,
        service: current.service,
      }

      // Include anomaly field based on whether symptoms were modified
      if ("anomaly" in changedFields) {
        payload.anomaly = changedFields.anomaly
      } else {
        payload.anomaly = null
      }

      console.log("handleMarkAsFalsePositive - Payload being sent:", JSON.stringify(payload, null, 2))

      const response = await fetch(`${API_BASE_URL}${RELEVANT_STATE_ENDPOINT}/${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error("Failed to mark as false positive")
      }

      await fetchIncident()
      setIsEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to mark as false positive")
    } finally {
      setIsSaving(false)
    }
  }

  const handleMarkAsIncident = async () => {
    if (!incident) return

    try {
      setIsSaving(true)

      // Determine if we're working with edited or original data
      const current = isEditing && editedIncident ? editedIncident : incident

      // Check if symptoms were modified using getChangedFields
      const changedFields = isEditing && editedIncident ? getChangedFields(incident, editedIncident) : {}

      // Build payload with all required fields from RelevantState model
      const payload: any = {
        id: current.id,
        revision: (incident.revision ?? 0) + 1,
        uri: current.uri,
        description: current.description,
        start_time: current.start_time,
        end_time: current.end_time,
        state: "confirmed",
        confidence_score: current.confidence_score,
        concern_score: current.concern_score,
        publisher: current.publisher,
        service: current.service,
      }

      // Include anomaly field based on whether symptoms were modified
      if ("anomaly" in changedFields) {
        payload.anomaly = changedFields.anomaly
      } else {
        payload.anomaly = null
      }

      console.log("handleMarkAsIncident - Payload being sent:", JSON.stringify(payload, null, 2))

      const response = await fetch(`${API_BASE_URL}${RELEVANT_STATE_ENDPOINT}/${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error("Failed to mark as incident")
      }

      await fetchIncident()
      setIsEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to mark as incident")
    } finally {
      setIsSaving(false)
    }
  }

  const handleReopenAnalysis = async () => {
    if (!incident) return

    try {
      setIsSaving(true)

      // Determine if we're working with edited or original data
      const current = isEditing && editedIncident ? editedIncident : incident

      // Check if symptoms were modified using getChangedFields
      const changedFields = isEditing && editedIncident ? getChangedFields(incident, editedIncident) : {}

      // Build payload with all required fields from RelevantState model
      const payload: any = {
        id: current.id,
        revision: (incident.revision ?? 0) + 1,
        uri: current.uri,
        description: current.description,
        start_time: current.start_time,
        end_time: current.end_time,
        state: "potential",
        confidence_score: current.confidence_score,
        concern_score: current.concern_score,
        publisher: current.publisher,
        service: current.service,
      }

      // Include anomaly field based on whether symptoms were modified
      if ("anomaly" in changedFields) {
        payload.anomaly = changedFields.anomaly
      } else {
        payload.anomaly = null
      }

      console.log("handleReopenAnalysis - Payload being sent:", JSON.stringify(payload, null, 2))

      const response = await fetch(`${API_BASE_URL}${RELEVANT_STATE_ENDPOINT}/${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error("Failed to reopen analysis")
      }

      await fetchIncident()
      setIsEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reopen analysis")
    } finally {
      setIsSaving(false)
    }
  }

  const handleConcernScoreChange = (value: number[]) => {
    if (!editedIncident) return

    setEditedIncident({
      ...editedIncident,
      concern_score: value[0] / 100,
      confidence_score: 1.0, // Auto-set to 100%
    })
  }

  const handleConcernScoreTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!editedIncident) return

    const value = Number.parseFloat(e.target.value)
    if (!isNaN(value) && value >= 0 && value <= 100) {
      setEditedIncident({
        ...editedIncident,
        concern_score: value / 100,
        confidence_score: 1.0, // Auto-set to 100%
      })
    }
  }

  const handleRemoveSymptom = (indexToRemove: number) => {
    if (!editedIncident) return

    const updatedAnomalies = editedIncident.anomaly?.filter((_, index) => index !== indexToRemove) || []
    setEditedIncident({
      ...editedIncident,
      anomaly: updatedAnomalies,
    })
  }

  const handleEditSymptom = (index: number) => {
    if (!editedIncident?.anomaly) return

    const symptom = editedIncident.anomaly[index]
    setEditingSymptomIndex(index)
    setEditedSymptom({ ...symptom })

    const startTimestamp = dateToTimestamp(symptom.start_time)
    const endTimestamp = dateToTimestamp(symptom.end_time)

    if (startTimestamp && endTimestamp) {
      setAnnotations([
        {
          id: "initial",
          x1: startTimestamp,
          x2: endTimestamp,
          color: getBandColor(symptom.symptom?.concern_score || 0),
        },
      ])
    } else {
      setAnnotations([])
    }
  }

  const handleSaveEditedSymptom = () => {
    if (!editedIncident || editingSymptomIndex === null || !editedSymptom) return

    const updatedSymptom = {
      ...editedSymptom,
      start_time:
        annotations.length > 0 ? localDateToUTC(new Date(annotations[0].x1 * 1000)) : editedSymptom.start_time,
      end_time: annotations.length > 0 ? localDateToUTC(new Date(annotations[0].x2 * 1000)) : editedSymptom.end_time,
    }

    const updatedAnomalies = [...(editedIncident.anomaly || [])]
    updatedAnomalies[editingSymptomIndex] = updatedSymptom

    setEditedIncident({
      ...editedIncident,
      anomaly: updatedAnomalies,
    })

    setEditingSymptomIndex(null)
    setEditedSymptom(null)
    setAnnotations([])
  }

  const handleCancelEditSymptom = () => {
    setEditingSymptomIndex(null)
    setEditedSymptom(null)
    setAnnotations([])
  }

  const handleRemoveAnnotation = (annotationId: string) => {
    setAnnotations(annotations.filter((a) => a.id !== annotationId))
  }

  const handleChartMouseDown = (e: any) => {
    if (!e || !e.activeLabel) return
    const timestamp = e.activeLabel
    setIsDrawing(true)
    setDrawStart(timestamp)
    setDrawEnd(timestamp)
  }

  const handleChartMouseMove = (e: any) => {
    if (!isDrawing || !e || !e.activeLabel) return
    setDrawEnd(e.activeLabel)
  }

  const handleChartMouseUp = () => {
    if (!isDrawing || drawStart === null || drawEnd === null) {
      setIsDrawing(false)
      return
    }

    const x1 = Math.min(drawStart, drawEnd)
    const x2 = Math.max(drawStart, drawEnd)

    if (x2 - x1 > 0) {
      const newAnnotation: AnnotationBox = {
        id: `annotation-${Date.now()}`,
        x1,
        x2,
        color: getBandColor(editedSymptom?.symptom?.concern_score || 0),
      }
      // Replace all annotations with just this one
      setAnnotations([newAnnotation])
    }

    setIsDrawing(false)
    setDrawStart(null)
    setDrawEnd(null)
  }

  const handleAddSymptom = () => {
    if (!editedIncident) return

    const newSymptom = {
      // Do NOT add id for new symptoms
      revision: 1,
      uri: "https://api.example.com/new-symptom",
      state: "potential",
      description: "New symptom description",
      start_time: localDateToUTC(new Date()),
      end_time: null,
      confidence_score: 0.5,
      pattern: "unknown",
      annotator: {
        name: "Manual Entry",
        version: 1,
        annotator_type: "manual",
      },
      symptom: {
        concern_score: 0.5,
      },
    }

    const updatedAnomalies = [...(editedIncident.anomaly || []), newSymptom]
    setEditedIncident({
      ...editedIncident,
      anomaly: updatedAnomalies,
    })
  }

  const getConcernColor = (score: number) => {
    if (score >= 0.8) return "text-red-400"
    if (score >= 0.6) return "text-yellow-400"
    return "text-green-400"
  }

  const getConcernBadgeColor = (score: number) => {
    if (score >= 0.8) return "bg-red-500/20 text-red-400 border-red-500/30"
    if (score >= 0.6) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
    return "bg-green-500/20 text-green-400 border-green-500/30"
  }

  const getBandColor = (score: number) => {
    if (score >= 0.8) return "hsl(0, 84%, 60%)" // Red
    if (score >= 0.6) return "hsl(45, 93%, 47%)" // Yellow
    return "hsl(142, 76%, 36%)" // Green
  }

  const getStateIcon = (state: string) => {
    switch (state) {
      case "unknown":
        return <HelpCircle className="w-4 h-4" />
      case "forecasted":
        return <AlertCircle className="w-4 h-4" />
      case "potential":
        return <AlertTriangle className="w-4 h-4" />
      case "discarded":
        return <XCircle className="w-4 h-4" />
      case "confirmed":
        return <CheckCircle className="w-4 h-4" />
      default:
        return <Info className="w-4 h-4" />
    }
  }

  const getStateColor = (state: string) => {
    switch (state) {
      case "unknown":
        return "bg-gray-500/20 text-gray-400 border-gray-500/30"
      case "forecasted":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30"
      case "potential":
        return "bg-orange-500/20 text-orange-400 border-orange-500/30"
      case "discarded":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      case "confirmed":
        return "bg-green-500/20 text-green-400 border-green-500/30"
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(Number.parseInt(timestamp) * 1000)
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  const calculateGlobalTimeDomain = (anomalies: any[]) => {
    let minTimestamp = Number.POSITIVE_INFINITY
    let maxTimestamp = Number.NEGATIVE_INFINITY

    anomalies.forEach((anom) => {
      if (anom.telemetry_data && Object.keys(anom.telemetry_data).length > 0) {
        const timestamps = Object.keys(anom.telemetry_data).map((ts) => Number.parseInt(ts))
        minTimestamp = Math.min(minTimestamp, ...timestamps)
        maxTimestamp = Math.max(maxTimestamp, ...timestamps)
      }
    })

    return minTimestamp !== Number.POSITIVE_INFINITY && maxTimestamp !== Number.NEGATIVE_INFINITY
      ? { minTimestamp, maxTimestamp }
      : null
  }

  const dateToTimestamp = (dateString: string | null) => {
    if (!dateString) return null
    return Math.floor(new Date(dateString).getTime() / 1000)
  }

  const prepareChartData = (
    telemetryData: Record<string, number>,
    globalDomain: { minTimestamp: number; maxTimestamp: number } | null,
  ) => {
    if (globalDomain) {
      const allTimestamps = new Set<number>()

      // Add all timestamps from telemetry data
      Object.keys(telemetryData).forEach((ts) => allTimestamps.add(Number.parseInt(ts)))

      // Generate timestamps at 60-second intervals within the global domain
      for (let ts = globalDomain.minTimestamp; ts <= globalDomain.maxTimestamp; ts += 60) {
        allTimestamps.add(ts)
      }

      return Array.from(allTimestamps)
        .sort((a, b) => a - b)
        .map((timestamp) => ({
          timestamp: formatTimestamp(timestamp.toString()),
          rawTimestamp: timestamp,
          value: telemetryData[timestamp.toString()] ?? null, // Use null for missing data points
          fullTimestamp: new Date(timestamp * 1000).toLocaleString(),
        }))
    }

    // Fallback to original behavior if no global domain
    return Object.entries(telemetryData)
      .sort(([a], [b]) => Number.parseInt(a) - Number.parseInt(b))
      .map(([timestamp, value]) => ({
        timestamp: formatTimestamp(timestamp),
        rawTimestamp: Number.parseInt(timestamp),
        value: value,
        fullTimestamp: new Date(Number.parseInt(timestamp) * 1000).toLocaleString(),
      }))
  }

  const calculateDuration = (startTime: string, endTime?: string | null) => {
    const start = new Date(startTime)
    const end = endTime ? new Date(endTime) : new Date()
    const diffMs = end.getTime() - start.getTime()

    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))

    if (days > 0) return `${days}d ${hours}h ${minutes}m`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  if (loading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-200">Loading incident details...</div>
        </div>
      </div>
    )
  }

  if (error || !incident) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-red-400 mb-2">Error loading incident</div>
            <div className="text-gray-200">{error || "Incident not found"}</div>
            <Button onClick={() => router.back()} className="mt-4">
              Go Back
            </Button>
          </div>
        </div>
      </div>
    )
  }

  const currentIncident = isEditing ? editedIncident! : incident

  const globalTimeDomain = currentIncident?.anomaly ? calculateGlobalTimeDomain(currentIncident.anomaly) : null

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.back()}
            className="text-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Incidents
          </Button>
          <div className="h-6 w-px bg-border" />
          <div>
            <h1 className="text-3xl font-bold text-foreground">Incident Details</h1>
            <p className="text-muted-foreground font-mono text-sm">URI: {currentIncident.uri}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 justify-end">
          {!isEditing && (
            <>
              {currentIncident.state === "potential" && (
                <>
                  <Button
                    variant="outline"
                    onClick={handleMarkAsFalsePositive}
                    disabled={isSaving}
                    className="border-red-600 text-red-400 hover:bg-red-600/10 hover:text-white bg-transparent"
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    {isSaving ? "Processing..." : "Mark as False Positive"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleMarkAsIncident}
                    disabled={isSaving}
                    className="border-orange-600 text-orange-400 hover:bg-orange-600/10 hover:text-white bg-transparent"
                  >
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    {isSaving ? "Processing..." : "Mark as Incident"}
                  </Button>
                </>
              )}

              {currentIncident.state === "discarded" && (
                <>
                  <Button
                    variant="outline"
                    onClick={handleReopenAnalysis}
                    disabled={isSaving}
                    className="border-blue-600 text-blue-400 hover:bg-blue-600/10 hover:text-white bg-transparent"
                  >
                    <AlertCircle className="w-4 h-4 mr-2" />
                    {isSaving ? "Processing..." : "Reopen Analysis"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleMarkAsIncident}
                    disabled={isSaving}
                    className="border-orange-600 text-orange-400 hover:bg-orange-600/10 hover:text-white bg-transparent"
                  >
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    {isSaving ? "Processing..." : "Mark as Incident"}
                  </Button>
                </>
              )}

              {currentIncident.state === "confirmed" && (
                <Button
                  variant="outline"
                  onClick={handleMarkAsFalsePositive}
                  disabled={isSaving}
                  className="border-red-600 text-red-400 hover:bg-red-600/10 hover:text-white bg-transparent"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  {isSaving ? "Processing..." : "Mark as False Positive"}
                </Button>
              )}
            </>
          )}

          {isEditing ? (
            <>
              <Button
                variant="outline"
                onClick={handleCancel}
                disabled={isSaving}
                className="border-gray-700 bg-transparent hover:text-white"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving}
                className="bg-blue-600 hover:bg-blue-700 hover:text-white"
              >
                <Save className="w-4 h-4 mr-2" />
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
            </>
          ) : (
            <Button onClick={() => setIsEditing(true)} className="bg-blue-600 hover:bg-blue-700 hover:text-white">
              <Edit3 className="w-4 h-4 mr-2" />
              Edit Incident
            </Button>
          )}
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="bg-card border-border">
          <CardContent className="px-2 py-1">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-blue-500/20 flex-shrink-0">
                <BarChart3 className="w-5 h-5 text-blue-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground font-medium">Concern Score</p>
                {isEditing ? (
                  <div className="space-y-2">
                    <p className={`text-xl font-bold ${getConcernColor(editedIncident?.concern_score || 0)}`}>
                      {Math.round((editedIncident?.concern_score || 0) * 100)}%
                    </p>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="1"
                        value={Math.round((editedIncident?.concern_score || 0) * 100)}
                        onChange={handleConcernScoreTextChange}
                        className="w-16 px-2 py-1 text-xs bg-muted border border-border rounded text-foreground"
                      />
                      <span className="text-xs text-muted-foreground">%</span>
                    </div>
                    <Slider
                      value={[(editedIncident?.concern_score || 0) * 100]}
                      onValueChange={handleConcernScoreChange}
                      max={100}
                      step={1}
                      className="w-full"
                    />
                  </div>
                ) : (
                  <p className={`text-xl font-bold ${getConcernColor(currentIncident.concern_score)}`}>
                    {Math.round(currentIncident.concern_score * 100)}%
                  </p>
                )}
                <div className="flex items-center gap-1 mt-1">
                  <CheckCircle className="w-3 h-3 text-green-400" />
                  <span className="text-xs text-muted-foreground">
                    Confidence:{" "}
                    {currentIncident.confidence_score
                      ? `${Math.round(currentIncident.confidence_score * 100)}%`
                      : "N/A"}
                  </span>
                </div>
                <div className="mt-2">
                  <div className="flex items-center gap-2">
                    <p className="text-xs text-muted-foreground">State:</p>
                    <Badge className={`text-xs h-5 px-2 ${getStateColor(currentIncident.state || "unknown")}`}>
                      {getStateIcon(currentIncident.state || "unknown")}
                      <span className="ml-1">{currentIncident.state || "unknown"}</span>
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="px-2 py-1">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-orange-500/20 flex-shrink-0">
                <Clock className="w-5 h-5 text-orange-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground font-medium">Duration</p>
                <p className="text-xl font-bold text-orange-400">
                  {calculateDuration(currentIncident.start_time, currentIncident.end_time)}
                </p>
                <div className="mt-1 space-y-1">
                  <div className="text-xs text-muted-foreground">
                    <span className="font-medium">Start:</span> {formatDateTimeDisplay(currentIncident.start_time)}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    <span className="font-medium">End:</span>{" "}
                    {currentIncident.end_time ? formatDateTimeDisplay(currentIncident.end_time) : "Ongoing"}
                  </div>
                </div>
                <Badge
                  className={`text-xs h-4 px-1.5 mt-1 ${
                    currentIncident.end_time
                      ? "bg-gray-500/20 text-gray-300 border-gray-500/30"
                      : "bg-red-500/20 text-red-400 border-red-500/30"
                  }`}
                >
                  {currentIncident.end_time ? "Past" : "Ongoing"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="px-2 py-1">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-indigo-500/20 flex-shrink-0">
                <Server className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground font-medium mb-2">Publisher</p>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-muted-foreground">Name</p>
                    <p className="text-sm text-foreground font-medium">
                      {currentIncident.publisher?.name || "Unknown"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Version</p>
                    <p className="text-sm text-foreground font-medium">
                      {currentIncident.publisher?.version || "No version"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="px-2 py-1">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-purple-500/20 flex-shrink-0">
                <Server className="w-5 h-5 text-purple-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground font-medium mb-2">Service</p>
                {currentIncident.service ? (
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-muted-foreground">ID</p>
                      <p className="text-xs text-foreground font-mono break-all">
                        {currentIncident.service.id || "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Type</p>
                      <p className="text-sm text-foreground font-medium">{currentIncident.service.type || "N/A"}</p>
                    </div>
                    {/* Display any additional fields from the JSON */}
                    {Object.entries(currentIncident.service)
                      .filter(([key]) => key !== "id" && key !== "type")
                      .map(([key, value]) => (
                        <div key={key}>
                          <p className="text-xs text-muted-foreground capitalize">{key.replace(/_/g, " ")}</p>
                          <p className="text-xs text-foreground break-all">
                            {typeof value === "object" ? JSON.stringify(value) : String(value)}
                          </p>
                        </div>
                      ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">No service information</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      <Card className="bg-card border-border mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Description
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="description" className="text-foreground font-medium">
              Description:
            </Label>
            {isEditing ? (
              <Textarea
                id="description"
                value={editedIncident?.description || ""}
                onChange={(e) =>
                  setEditedIncident((prev: RelevantState | null) =>
                    prev ? { ...prev, description: e.target.value } : null,
                  )
                }
                className="mt-1 bg-card border-border text-foreground"
                rows={3}
              />
            ) : (
              <p className="mt-1 text-sm text-foreground">{currentIncident.description || "No description provided"}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Related Symptoms */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Related Symptoms
              </CardTitle>
              <CardDescription>Symptoms associated with this Incident</CardDescription>
            </div>
            {isEditing && (
              <Button onClick={handleAddSymptom} size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                <Plus className="w-4 h-4 mr-2" />
                Add Symptom
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {currentIncident.anomaly && currentIncident.anomaly.length > 0 ? (
            <div className="space-y-4">
              <div className="text-sm text-muted-foreground text-center mb-4">
                {formatDateTimeDisplay(currentIncident.start_time)} →{" "}
                {currentIncident.end_time ? formatDateTimeDisplay(currentIncident.end_time) : "Ongoing"}
              </div>

              <div className="space-y-4">
                {currentIncident.anomaly
                  .sort((a: any, b: any) => {
                    const aConcern = a.symptom?.concern_score || 0
                    const bConcern = b.symptom?.concern_score || 0
                    return bConcern - aConcern
                  })
                  .map((anom: any, index: number) => {
                    let startTimestamp = dateToTimestamp(anom.start_time)
                    let endTimestamp = dateToTimestamp(anom.end_time)

                    if (globalTimeDomain && startTimestamp) {
                      startTimestamp = Math.max(startTimestamp, globalTimeDomain.minTimestamp)
                    }
                    if (globalTimeDomain && endTimestamp) {
                      endTimestamp = Math.min(endTimestamp, globalTimeDomain.maxTimestamp)
                    }
                    if (!endTimestamp && globalTimeDomain) {
                      endTimestamp = globalTimeDomain.maxTimestamp
                    }

                    return (
                      <div key={index} className="p-3 bg-muted/50 rounded-lg border border-border mb-3">
                        {isEditing && (
                          <div className="flex justify-end gap-2 mt-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditSymptom(index)}
                              className="h-9 px-3 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 flex items-center gap-2"
                            >
                              <Edit3 className="w-4 h-4" />
                              <span className="text-sm font-medium">Edit</span>
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveSymptom(index)}
                              className="h-9 px-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 flex items-center gap-2"
                            >
                              <Trash2 className="w-5 h-5" />
                              <span className="text-sm font-medium">Remove</span>
                            </Button>
                          </div>
                        )}

                        <div className="flex items-center justify-between gap-3 mb-2">
                          <div className="flex-shrink-0">
                            {anom.metric_name && <p className="text-sm text-blue-400 font-mono">{anom.metric_name}</p>}
                            {anom.symptom?.metric && (
                              <p className="text-sm text-blue-400 font-mono">{anom.symptom.metric}</p>
                            )}
                          </div>

                          {anom.dimensions && Object.keys(anom.dimensions).length > 0 && (
                            <div className="flex-1 p-1.5 bg-muted rounded border border-border">
                              <div className="flex flex-wrap gap-x-4 gap-y-1">
                                {Object.entries(anom.dimensions).map(([key, value]) => (
                                  <div key={key} className="flex items-center gap-2">
                                    <span className="text-xs text-muted-foreground">{key}:</span>
                                    <span className="text-xs text-foreground font-mono">{value}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          {anom.symptom?.dimensions && Object.keys(anom.symptom.dimensions).length > 0 && (
                            <div className="flex-1 p-1.5 bg-muted rounded border border-border">
                              <div className="flex flex-wrap gap-x-4 gap-y-1">
                                {Object.entries(anom.symptom.dimensions).map(([key, value]) => (
                                  <div key={key} className="flex items-center gap-2">
                                    <span className="text-xs text-muted-foreground">{key}:</span>
                                    <span className="text-xs text-foreground font-mono">{value}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <div className="flex items-center gap-3 flex-shrink-0">
                            {anom.symptom?.concern_score !== undefined && (
                              <span className={`text-sm font-medium ${getConcernColor(anom.symptom.concern_score)}`}>
                                {Math.round(anom.symptom.concern_score * 100)}% concern
                              </span>
                            )}
                            <span className="text-sm text-blue-400 font-medium">
                              {Math.round(anom.confidence_score * 100)}% confidence
                            </span>
                          </div>
                        </div>

                        {anom.telemetry_data && Object.keys(anom.telemetry_data).length > 0 ? (
                          <div className="space-y-2">
                            <div className="h-[163px] w-full">
                              <ChartContainer
                                config={{
                                  value: {
                                    label: anom.metric_name || "Value",
                                    color: "hsl(217, 91%, 60%)",
                                  },
                                }}
                                className="h-full w-full"
                              >
                                <LineChart data={prepareChartData(anom.telemetry_data, globalTimeDomain)}>
                                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                                  {startTimestamp && endTimestamp && (
                                    <ReferenceArea
                                      x1={startTimestamp}
                                      x2={endTimestamp}
                                      stroke={getBandColor(anom.symptom?.concern_score || 0)}
                                      strokeOpacity={0.8}
                                      fill={getBandColor(anom.symptom?.concern_score || 0)}
                                      fillOpacity={0.3}
                                      strokeWidth={2}
                                    />
                                  )}
                                  <XAxis
                                    dataKey="rawTimestamp"
                                    type="number"
                                    domain={
                                      globalTimeDomain
                                        ? [globalTimeDomain.minTimestamp, globalTimeDomain.maxTimestamp]
                                        : ["auto", "auto"]
                                    }
                                    tickFormatter={(value) => formatTimestamp(value.toString())}
                                    className="text-xs"
                                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                                  />
                                  <YAxis
                                    className="text-xs"
                                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                                  />
                                  <ChartTooltip
                                    content={
                                      <ChartTooltipContent
                                        labelFormatter={(value, payload) => {
                                          return payload?.[0]?.payload?.fullTimestamp || value
                                        }}
                                      />
                                    }
                                  />
                                  <Line
                                    type="monotone"
                                    dataKey="value"
                                    stroke="hsl(217, 91%, 60%)"
                                    strokeWidth={2}
                                    dot={{ fill: "hsl(217, 91%, 60%)", r: 2 }}
                                    activeDot={{ r: 4 }}
                                    connectNulls={false}
                                  />
                                </LineChart>
                              </ChartContainer>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-6 text-muted-foreground">
                            <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p className="text-sm">No telemetry data available</p>
                          </div>
                        )}

                        <div className="flex items-start gap-2 mt-2">
                          {anom.description && (
                            <div className="flex-1 p-1.5 bg-muted rounded border border-border">
                              <p className="text-xs text-foreground">{anom.description}</p>
                            </div>
                          )}
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <Badge className={getStateColor(anom.state)}>
                              {getStateIcon(anom.state)}
                              <span className="ml-2">{anom.state}</span>
                            </Badge>
                            {anom.pattern && (
                              <Badge variant="outline" className="border-border text-muted-foreground">
                                {anom.pattern}
                              </Badge>
                            )}
                            {anom.annotator && (
                              <Badge variant="outline" className="border-purple-600 text-purple-300 text-xs">
                                {anom.annotator.name} v{anom.annotator.version}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-foreground">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No related anomalies found</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Symptom Dialog */}
      <Dialog open={editingSymptomIndex !== null} onOpenChange={(open) => !open && handleCancelEditSymptom()}>
        <DialogContent className="max-w-7xl max-h-[90vh] overflow-y-auto bg-card border-border">
          <DialogHeader>
            <DialogTitle className="text-xl text-foreground">Edit Symptom</DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Modify the symptom's concern score, confidence, description, and time range annotations
            </DialogDescription>
          </DialogHeader>

          {editedSymptom && (
            <div className="space-y-6 py-4">
              {/* Concern Score */}
              <div className="space-y-2">
                <Label className="text-foreground font-medium">Concern Score</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[(editedSymptom.symptom?.concern_score || 0) * 100]}
                    onValueChange={(value) => {
                      setEditedSymptom({
                        ...editedSymptom,
                        symptom: {
                          ...editedSymptom.symptom,
                          concern_score: value[0] / 100,
                        },
                      })
                    }}
                    max={100}
                    step={1}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    value={Math.round((editedSymptom.symptom?.concern_score || 0) * 100)}
                    onChange={(e) => {
                      const value = Number.parseFloat(e.target.value)
                      if (!isNaN(value) && value >= 0 && value <= 100) {
                        setEditedSymptom({
                          ...editedSymptom,
                          symptom: {
                            ...editedSymptom.symptom,
                            concern_score: value / 100,
                          },
                        })
                      }
                    }}
                    className="w-20 px-3 py-2 bg-muted border border-border rounded text-foreground"
                  />
                  <span className="text-muted-foreground">%</span>
                </div>
                <p className={`text-sm font-medium ${getConcernColor(editedSymptom.symptom?.concern_score || 0)}`}>
                  {Math.round((editedSymptom.symptom?.concern_score || 0) * 100)}% concern
                </p>
              </div>

              {/* Confidence Score */}
              <div className="space-y-2">
                <Label className="text-foreground font-medium">Confidence Score</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[(editedSymptom.confidence_score || 0) * 100]}
                    onValueChange={(value) => {
                      setEditedSymptom({
                        ...editedSymptom,
                        confidence_score: value / 100,
                      })
                    }}
                    max={100}
                    step={1}
                    className="flex-1"
                  />
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    value={Math.round((editedSymptom.confidence_score || 0) * 100)}
                    onChange={(e) => {
                      const value = Number.parseFloat(e.target.value)
                      if (!isNaN(value) && value >= 0 && value <= 100) {
                        setEditedSymptom({
                          ...editedSymptom,
                          confidence_score: value / 100,
                        })
                      }
                    }}
                    className="w-20 px-3 py-2 bg-muted border border-border rounded text-foreground"
                  />
                  <span className="text-muted-foreground">%</span>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label className="text-foreground font-medium">Description</Label>
                <Textarea
                  value={editedSymptom.description || ""}
                  onChange={(e) => setEditedSymptom({ ...editedSymptom, description: e.target.value })}
                  className="bg-card border-border text-foreground"
                  rows={3}
                  placeholder="Enter symptom description..."
                />
              </div>

              {/* Chart Annotations */}
              <div className="space-y-2">
                <Label className="text-foreground font-medium">Time Range Annotation</Label>
                <p className="text-sm text-muted-foreground">
                  Drag on the chart to draw the annotation box (colored time range). Only one annotation per symptom is
                  allowed.
                </p>

                {/* Annotations List */}
                {annotations.length > 0 && (
                  <div className="space-y-2 mb-4">
                    {annotations.map((annotation) => (
                      <div
                        key={annotation.id}
                        className="flex items-center justify-between p-2 bg-muted rounded border border-border"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className="w-4 h-4 rounded"
                            style={{ backgroundColor: annotation.color, opacity: 0.5 }}
                          />
                          <span className="text-sm text-muted-foreground">
                            {new Date(annotation.x1 * 1000).toLocaleString()} →{" "}
                            {new Date(annotation.x2 * 1000).toLocaleString()}
                          </span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveAnnotation(annotation.id)}
                          className="h-8 px-2 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Interactive Chart */}
                {editedSymptom.telemetry_data && Object.keys(editedSymptom.telemetry_data).length > 0 && (
                  <div
                    className="h-[250px] w-full border border-border rounded bg-muted cursor-crosshair"
                    onMouseUp={handleChartMouseUp}
                    onMouseLeave={handleChartMouseUp}
                  >
                    <ChartContainer
                      config={{
                        value: {
                          label: editedSymptom.metric_name || "Value",
                          color: "hsl(217, 91%, 60%)",
                        },
                      }}
                      className="h-full w-full"
                    >
                      <LineChart
                        data={prepareChartData(editedSymptom.telemetry_data, globalTimeDomain)}
                        onMouseDown={handleChartMouseDown}
                        onMouseMove={handleChartMouseMove}
                      >
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />

                        {/* Existing annotations */}
                        {annotations.map((annotation) => (
                          <ReferenceArea
                            key={annotation.id}
                            x1={annotation.x1}
                            x2={annotation.x2}
                            stroke={annotation.color}
                            strokeOpacity={0.8}
                            fill={annotation.color}
                            fillOpacity={0.3}
                            strokeWidth={2}
                          />
                        ))}

                        {/* Drawing preview */}
                        {isDrawing && drawStart !== null && drawEnd !== null && (
                          <ReferenceArea
                            x1={Math.min(drawStart, drawEnd)}
                            x2={Math.max(drawStart, drawEnd)}
                            stroke="hsl(217, 91%, 60%)"
                            strokeOpacity={0.5}
                            fill="hsl(217, 91%, 60%)"
                            fillOpacity={0.2}
                            strokeWidth={2}
                            strokeDasharray="5 5"
                          />
                        )}

                        <XAxis
                          dataKey="rawTimestamp"
                          type="number"
                          domain={
                            globalTimeDomain
                              ? [globalTimeDomain.minTimestamp, globalTimeDomain.maxTimestamp]
                              : ["auto", "auto"]
                          }
                          tickFormatter={(value) => formatTimestamp(value.toString())}
                          className="text-xs"
                          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                        />
                        <YAxis className="text-xs" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }} />
                        <ChartTooltip
                          content={
                            <ChartTooltipContent
                              labelFormatter={(value, payload) => {
                                return payload?.[0]?.payload?.fullTimestamp || value
                              }}
                            />
                          }
                        />
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke="hsl(217, 91%, 60%)"
                          strokeWidth={2}
                          dot={{ fill: "hsl(217, 91%, 60%)", r: 2 }}
                          activeDot={{ r: 4 }}
                          connectNulls={false}
                        />
                      </LineChart>
                    </ChartContainer>
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleCancelEditSymptom}
              className="border-border bg-transparent hover:text-foreground"
            >
              Cancel
            </Button>
            <Button onClick={handleSaveEditedSymptom} className="bg-blue-600 hover:bg-blue-700 text-white">
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
