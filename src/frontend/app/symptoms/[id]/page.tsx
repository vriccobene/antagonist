"use client"
import { useState, useEffect } from "react"
import { ENDPOINTS } from "@/app/api"
import type React from "react"

import { useParams, useRouter } from "next/navigation"
import {
  ArrowLeft,
  Save,
  Edit3,
  Info,
  Activity,
  Clock,
  FileText,
  BarChart3,
  CheckCircle,
  XCircle,
  AlertCircle,
  HelpCircle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ReferenceArea } from "recharts"
import { formatDateTime } from "@/lib/utils"

// Backend API base URL and endpoint
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
const SYMPTOM_ENDPOINT = ENDPOINTS.ANOMALY

interface Symptom {
  id?: string
  concern_score: number
  metric?: string
  dimensions?: Record<string, string | number>
}

interface Annotator {
  name: string
  version?: number
  annotator_type: string
}

interface AnomalyPattern {
  drop?: string
  spike?: string
  trend?: string
  mean_shift?: string
  seasonality_shift?: string
  other?: string
}

interface SymptomDetail {
  id?: string
  revision?: number
  uri?: string
  state: string
  description?: string
  start_time: string
  end_time?: string | null
  confidence_score: number
  pattern?: string
  annotator: Annotator
  symptom?: Symptom
  telemetry_data?: Record<string, number>
}

export default function SymptomDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [symptom, setSymptom] = useState<SymptomDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [editedSymptom, setEditedSymptom] = useState<SymptomDetail | null>(null)

  const fetchSymptom = async () => {
    try {
      setLoading(true)

      try {
        console.log("Attempting to fetch symptom from backend:", `${API_BASE_URL}${SYMPTOM_ENDPOINT}/${params.id}`)

        const response = await fetch(`${API_BASE_URL}${SYMPTOM_ENDPOINT}/${params.id}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (response.ok) {
          const data = await response.json()
          console.log("Successfully fetched symptom from backend:", data)
          setSymptom(data)
          setEditedSymptom(data)
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
      console.log("Error in fetchSymptom:", err)
      setError("Failed to load symptom data")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (params.id) {
      fetchSymptom()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id])

  const handleSave = async () => {
    if (!editedSymptom || !symptom) return

    try {
      setIsSaving(true)

      const payload = {
        id: editedSymptom.id,
        description: editedSymptom.description,
        confidence_score: editedSymptom.confidence_score,
        symptom: editedSymptom.symptom,
        revision: (symptom.revision ?? 0) + 1,
      }

      const response = await fetch(`${API_BASE_URL}${SYMPTOM_ENDPOINT}/${params.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error("Failed to save symptom")
      }

      await fetchSymptom()
      setIsEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save changes")
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setEditedSymptom(symptom)
    setIsEditing(false)
  }

  const handleConcernScoreChange = (value: number[]) => {
    if (!editedSymptom) return

    setEditedSymptom({
      ...editedSymptom,
      symptom: {
        ...editedSymptom.symptom!,
        concern_score: value[0] / 100,
      },
      confidence_score: 1.0,
    })
  }

  const handleConcernScoreTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!editedSymptom) return

    const value = Number.parseFloat(e.target.value)
    if (!isNaN(value) && value >= 0 && value <= 100) {
      setEditedSymptom({
        ...editedSymptom,
        symptom: {
          ...editedSymptom.symptom!,
          concern_score: value / 100,
        },
        confidence_score: 1.0,
      })
    }
  }

  const getConcernColor = (score: number) => {
    if (score >= 0.8) return "text-red-400"
    if (score >= 0.6) return "text-yellow-400"
    return "text-green-400"
  }

  const getBandColor = (score: number) => {
    if (score >= 0.8) return "hsl(0, 84%, 60%)"
    if (score >= 0.6) return "hsl(45, 93%, 47%)"
    return "hsl(142, 76%, 36%)"
  }

  const getStateIcon = (state: string) => {
    switch (state) {
      case "unknown":
        return <HelpCircle className="w-4 h-4" />
      case "forecasted":
        return <AlertCircle className="w-4 h-4" />
      case "potential":
        return <AlertCircle className="w-4 h-4" />
      case "discarded":
        return <XCircle className="w-4 h-4" />
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
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(Number.parseInt(timestamp) * 1000)
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  const dateToTimestamp = (dateString: string | null) => {
    if (!dateString) return null
    return Math.floor(new Date(dateString).getTime() / 1000)
  }

  const prepareChartData = (telemetryData: Record<string, number>) => {
    return Object.entries(telemetryData)
      .sort(([a], [b]) => Number.parseInt(a) - Number.parseInt(b))
      .map(([timestamp, value]) => ({
        timestamp: formatTimestamp(timestamp),
        rawTimestamp: Number.parseInt(timestamp), // Ensure this is a number
        value: value,
        fullTimestamp: new Date(Number.parseInt(timestamp) * 1000).toLocaleString(),
      }))
  }

  const getTelemetryTimeRange = (telemetryData: Record<string, number>) => {
    const timestamps = Object.keys(telemetryData).map((ts) => Number.parseInt(ts))
    if (timestamps.length === 0) return null
    return {
      min: Math.min(...timestamps),
      max: Math.max(...timestamps),
    }
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
          <div className="text-gray-200">Loading symptom details...</div>
        </div>
      </div>
    )
  }

  if (error || !symptom) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-red-400 mb-2">Error loading symptom</div>
            <div className="text-gray-200">{error || "Symptom not found"}</div>
            <Button onClick={() => router.back()} className="mt-4">
              Go Back
            </Button>
          </div>
        </div>
      </div>
    )
  }

  const currentSymptom = isEditing ? editedSymptom! : symptom

  const startTimestamp = dateToTimestamp(currentSymptom.start_time)
  const endTimestamp = dateToTimestamp(currentSymptom.end_time)

  const telemetryRange = currentSymptom.telemetry_data ? getTelemetryTimeRange(currentSymptom.telemetry_data) : null

  let clampedStartTimestamp = startTimestamp
  let clampedEndTimestamp = endTimestamp

  if (telemetryRange) {
    if (clampedStartTimestamp) {
      clampedStartTimestamp = Math.max(clampedStartTimestamp, telemetryRange.min)
    }
    if (clampedEndTimestamp) {
      clampedEndTimestamp = Math.min(clampedEndTimestamp, telemetryRange.max)
    } else {
      clampedEndTimestamp = telemetryRange.max
    }
  }

  console.log(" Symptom timestamps:", {
    startTimestamp,
    endTimestamp,
    clampedStartTimestamp,
    clampedEndTimestamp,
    telemetryRange,
  })

  console.log("Chart Data:", prepareChartData(currentSymptom.telemetry_data))

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()} className="text-gray-200 hover:text-white">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Symptoms
          </Button>
          <div className="h-6 w-px bg-border" />
          <div>
            <h1 className="text-3xl font-bold">Symptom Details</h1>
            <p className="text-gray-300 font-mono text-sm">URI: {currentSymptom.uri}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 justify-end">
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
              Edit Symptom
            </Button>
          )}
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Concern Score and Confidence */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="px-2 py-1">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-blue-500/20 flex-shrink-0">
                <BarChart3 className="w-5 h-5 text-blue-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white font-medium">Concern Score</p>
                {isEditing ? (
                  <div className="space-y-2">
                    <p className={`text-xl font-bold ${getConcernColor(editedSymptom?.symptom?.concern_score || 0)}`}>
                      {Math.round((editedSymptom?.symptom?.concern_score || 0) * 100)}%
                    </p>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="1"
                        value={Math.round((editedSymptom?.symptom?.concern_score || 0) * 100)}
                        onChange={handleConcernScoreTextChange}
                        className="w-16 px-2 py-1 text-xs bg-gray-900 border border-gray-600 rounded text-white"
                      />
                      <span className="text-xs text-gray-300">%</span>
                    </div>
                    <Slider
                      value={[(editedSymptom?.symptom?.concern_score || 0) * 100]}
                      onValueChange={handleConcernScoreChange}
                      max={100}
                      step={1}
                      className="w-full"
                    />
                  </div>
                ) : (
                  <p className={`text-xl font-bold ${getConcernColor(currentSymptom.symptom?.concern_score || 0)}`}>
                    {Math.round((currentSymptom.symptom?.concern_score || 0) * 100)}%
                  </p>
                )}
                <div className="flex items-center gap-1 mt-1">
                  <CheckCircle className="w-3 h-3 text-green-400" />
                  <span className="text-xs text-gray-300">
                    Confidence: {Math.round(currentSymptom.confidence_score * 100)}%
                  </span>
                </div>
                <div className="mt-2">
                  <div className="flex items-center gap-2">
                    <p className="text-xs text-gray-300">State:</p>
                    <Badge className={`text-xs h-5 px-2 ${getStateColor(currentSymptom.state)}`}>
                      {getStateIcon(currentSymptom.state)}
                      <span className="ml-1">{currentSymptom.state}</span>
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Duration */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="px-2 py-1">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-orange-500/20 flex-shrink-0">
                <Clock className="w-5 h-5 text-orange-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white font-medium">Duration</p>
                <p className="text-xl font-bold text-orange-400">
                  {calculateDuration(currentSymptom.start_time, currentSymptom.end_time)}
                </p>
                <div className="mt-1 space-y-1">
                  <div className="text-xs text-gray-300">
                    <span className="font-medium">Start:</span> {formatDateTime(currentSymptom.start_time)}
                  </div>
                  <div className="text-xs text-gray-300">
                    <span className="font-medium">End:</span>{" "}
                    {currentSymptom.end_time ? formatDateTime(currentSymptom.end_time) : "Ongoing"}
                  </div>
                </div>
                <Badge
                  className={`text-xs h-4 px-1.5 mt-1 ${
                    currentSymptom.end_time
                      ? "bg-gray-500/20 text-gray-300 border-gray-500/30"
                      : "bg-red-500/20 text-red-400 border-red-500/30"
                  }`}
                >
                  {currentSymptom.end_time ? "Past" : "Ongoing"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Annotator */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="px-2 py-1">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-indigo-500/20 flex-shrink-0">
                <Activity className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white font-medium mb-2">Annotator</p>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-gray-300">Name</p>
                    <p className="text-sm text-white font-medium">{currentSymptom.annotator.name}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div>
                      <p className="text-xs text-gray-300">Version</p>
                      <p className="text-sm text-white font-medium">
                        {currentSymptom.annotator.version ? `v${currentSymptom.annotator.version}` : "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-300">Type</p>
                      <Badge variant="outline" className="text-xs border-purple-600 text-purple-300">
                        {currentSymptom.annotator.annotator_type}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      <Card className="bg-gray-800/50 border-gray-700 mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Description
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="description" className="text-white font-medium">
              Description:
            </Label>
            {isEditing ? (
              <Textarea
                id="description"
                value={editedSymptom?.description || ""}
                onChange={(e) =>
                  setEditedSymptom((prev: SymptomDetail | null) =>
                    prev ? { ...prev, description: e.target.value } : null,
                  )
                }
                className="mt-1 bg-gray-900 border-gray-600 text-white"
                rows={3}
              />
            ) : (
              <p className="mt-1 text-sm text-gray-200">{currentSymptom.description || "No description provided"}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Metric Information */}
      {currentSymptom.symptom && (
        <Card className="bg-gray-800/50 border-gray-700 mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Metric Information
            </CardTitle>
            <CardDescription>Details about the monitored metric</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {currentSymptom.symptom.metric && (
                <div>
                  <Label className="text-white font-medium">Metric Name:</Label>
                  <p className="mt-1 text-sm text-blue-300 font-mono">{currentSymptom.symptom.metric}</p>
                </div>
              )}

              {currentSymptom.symptom.dimensions && Object.keys(currentSymptom.symptom.dimensions).length > 0 && (
                <div>
                  <Label className="text-white font-medium">Dimensions:</Label>
                  <div className="mt-2 p-3 bg-gray-900/50 rounded border border-gray-700">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {Object.entries(currentSymptom.symptom.dimensions).map(([key, value]) => (
                        <div key={key} className="flex flex-col">
                          <span className="text-xs text-gray-400">{key}</span>
                          <span className="text-sm text-white font-mono">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {currentSymptom.pattern && (
                <div>
                  <Label className="text-white font-medium">Pattern:</Label>
                  <Badge variant="outline" className="mt-1 border-gray-600 text-gray-300">
                    {currentSymptom.pattern}
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Telemetry Data */}
      {currentSymptom.telemetry_data && Object.keys(currentSymptom.telemetry_data).length > 0 && (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Telemetry Data
            </CardTitle>
            <CardDescription>Time-series visualization of the symptom</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <ChartContainer
                config={{
                  value: {
                    label: currentSymptom.symptom?.metric || "Value",
                    color: "hsl(217, 91%, 60%)",
                  },
                }}
                className="h-full w-full"
              >
                <LineChart data={prepareChartData(currentSymptom.telemetry_data)}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
                  {clampedStartTimestamp && clampedEndTimestamp && (
                    <ReferenceArea
                      x1={clampedStartTimestamp}
                      x2={clampedEndTimestamp}
                      stroke={getBandColor(currentSymptom.symptom?.concern_score || 0)}
                      strokeOpacity={0.8}
                      fill={getBandColor(currentSymptom.symptom?.concern_score || 0)}
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  )}
                  <XAxis
                    dataKey="rawTimestamp"
                    type="number"
                    domain={telemetryRange ? [telemetryRange.min, telemetryRange.max] : ["auto", "auto"]}
                    tickFormatter={(value) => formatTimestamp(value.toString())}
                    className="text-xs"
                    tick={{ fill: "rgb(156, 163, 175)", fontSize: 10 }}
                  />
                  <YAxis className="text-xs" tick={{ fill: "rgb(156, 163, 175)", fontSize: 10 }} />
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
                    dot={{ fill: "hsl(217, 91%, 60%)", r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ChartContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
