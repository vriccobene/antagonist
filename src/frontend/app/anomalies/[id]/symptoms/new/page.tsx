"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Slider } from "@/components/ui/slider"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { ChevronLeft, ChevronRight, Plus, X, Check, CalendarIcon, RefreshCw } from "lucide-react"
import { LineChart, Line, CartesianGrid, XAxis, YAxis, ReferenceArea } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { API_BASE_URL, ENDPOINTS } from "@/app/api"

interface AnnotationBox {
  id: string
  x1: number
  x2: number
  color: string
}

export default function NewSymptomPage() {
  const params = useParams()
  const router = useRouter()
  const anomalyId = params.id as string

  const [currentStep, setCurrentStep] = useState(1)
  const [anomaly, setAnomaly] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // Form state
  const [selectedMetric, setSelectedMetric] = useState("")
  const [selectedDimensions, setSelectedDimensions] = useState<Record<string, string>>({})
  const [description, setDescription] = useState("")
  const [concernScore, setConcernScore] = useState(0.5)
  const [customFields, setCustomFields] = useState<Array<{ key: string; value: string }>>([])

  // Available options
  const [availableMetrics, setAvailableMetrics] = useState<Array<{ name: string; dimensions: string[] }>>([])
  const [availableDimensionValues, setAvailableDimensionValues] = useState<Record<string, string[]>>({})

  // Time window selection
  const [annotations, setAnnotations] = useState<AnnotationBox[]>([])
  const [isDrawing, setIsDrawing] = useState(false)
  const [drawStart, setDrawStart] = useState<number | null>(null)
  const [drawEnd, setDrawEnd] = useState<number | null>(null)

  const [manualStartDate, setManualStartDate] = useState<Date | undefined>(undefined)
  const [manualEndDate, setManualEndDate] = useState<Date | undefined>(undefined)
  const [manualStartTime, setManualStartTime] = useState("")
  const [manualEndTime, setManualEndTime] = useState("")

  // Mock telemetry data for chart
  const [telemetryData, setTelemetryData] = useState<Array<{ timestamp: number; value: number }>>([])
  const [loadingTelemetry, setLoadingTelemetry] = useState(false)

  useEffect(() => {
    fetchAnomaly()
  }, [anomalyId])

  useEffect(() => {
    if (!manualStartTime) {
      setManualStartTime("00:00")
    }
    if (!manualEndTime) {
      setManualEndTime("00:00")
    }
  }, [])

  const fetchAnomaly = async () => {
    try {
      setLoading(true)

      try {
        console.log(
          "Attempting to fetch from backend:",
          `${API_BASE_URL}${ENDPOINTS.RELEVANT_STATE_TELEMETRY}/${anomalyId}`,
        )

        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.RELEVANT_STATE_TELEMETRY}/${anomalyId}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (response.ok) {
          const data = await response.json()
          console.log("Successfully fetched from backend:", data)
          setAnomaly(data)

          // Fetch available metrics from service's related relevant states
          if (data.service && data.service.id) {
            await fetchAvailableMetricsFromService(data.service.id)
          } else {
            console.error("No service found in anomaly data")
            setAvailableMetrics([])
          }
          return
        } else {
          console.log(" Backend responded with error:", response.status, response.statusText)
          throw new Error(`Backend error: ${response.status}`)
        }
      } catch (backendError) {
        console.error("Backend fetch failed:", backendError)
        throw backendError
      }
    } catch (err) {
      console.error(" Error in fetchAnomaly:", err)
      alert("Failed to load anomaly data")
    } finally {
      setLoading(false)
    }
  }



  const fetchAvailableMetricsFromService = async (serviceId: string) => {
    try {
      console.log(" Fetching relevant states for service:", serviceId)

      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.SERVICE}/${serviceId}/relevant_states`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        console.error("Failed to fetch service relevant states")
        setAvailableMetrics([])
        return
      }

      const relevantStates = await response.json()
      console.log(" Fetched relevant states:", relevantStates)

      // Extract unique metrics and their dimensions from all symptoms
      const metricsMap = new Map<string, Set<string>>()
      const dimensionValuesMap = new Map<string, Set<string>>()

      relevantStates.forEach((rs: any) => {
        if (rs.anomaly && Array.isArray(rs.anomaly)) {
          rs.anomaly.forEach((symptom: any) => {
            if (symptom.symptom) {
              const metric = symptom.symptom.metric
              const dimensions = symptom.symptom.dimensions

              if (metric) {
                // Add metric if not exists
                if (!metricsMap.has(metric)) {
                  metricsMap.set(metric, new Set())
                }

                // Collect dimension keys and values
                if (dimensions && typeof dimensions === "object") {
                  Object.entries(dimensions).forEach(([key, value]) => {
                    // Add dimension key to metric
                    metricsMap.get(metric)?.add(key)

                    // Store dimension value
                    const dimKey = `${metric}:${key}`
                    if (!dimensionValuesMap.has(dimKey)) {
                      dimensionValuesMap.set(dimKey, new Set())
                    }
                    dimensionValuesMap.get(dimKey)?.add(String(value))
                  })
                }
              }
            }
          })
        }
      })

      // Convert to the expected format
      const metrics = Array.from(metricsMap.entries()).map(([name, dimensionKeys]) => ({
        name,
        dimensions: Array.from(dimensionKeys),
      }))

      console.log(" Extracted metrics:", metrics)

      if (metrics.length === 0) {
        console.log("No metrics found in service symptoms")
        setAvailableMetrics([])
      } else {
        setAvailableMetrics(metrics)

        // Store dimension values for later use
        const dimensionValues: Record<string, string[]> = {}
        dimensionValuesMap.forEach((values, key) => {
          dimensionValues[key] = Array.from(values)
        })

        // Store in component state for use when metric is selected
        ;(window as any).__dimensionValuesCache = dimensionValues
      }
    } catch (error) {
      console.error("Error fetching metrics from service:", error)
      setAvailableMetrics([])
    }
  }

  const fetchTelemetryData = async (
    overrideStartDate?: Date,
    overrideStartTime?: string,
    overrideEndDate?: Date,
    overrideEndTime?: string,
  ) => {
    if (!anomaly || !anomaly.service || !anomaly.service.type) {
      console.error("No service type available for telemetry data fetch")
      setTelemetryData([])
      return
    }

    try {
      setLoadingTelemetry(true)
      console.log(" Fetching telemetry data for metric:", selectedMetric, "dimensions:", selectedDimensions)

      // Use override values if provided, otherwise use state values
      const effectiveStartDate = overrideStartDate ?? manualStartDate
      const effectiveStartTime = overrideStartTime ?? manualStartTime
      const effectiveEndDate = overrideEndDate ?? manualEndDate
      const effectiveEndTime = overrideEndTime ?? manualEndTime

      console.log(
        " Effective dates - Start:",
        effectiveStartDate,
        effectiveStartTime,
        "End:",
        effectiveEndDate,
        effectiveEndTime,
      )

      // Calculate time range - use manual dates if set, otherwise use anomaly time range or default
      let startTime: Date
      let endTime: Date

      // Determine end time first (needed for default start time calculation)
      if (effectiveEndDate && effectiveEndTime) {
        // Use manually selected end date and time
        const [hours, minutes] = effectiveEndTime.split(":")
        endTime = new Date(effectiveEndDate)
        endTime.setHours(Number.parseInt(hours), Number.parseInt(minutes), 0, 0)
        console.log(" Using manual end time:", endTime.toISOString())
      } else if (anomaly.end_time) {
        endTime = new Date(anomaly.end_time)
        console.log(" Using anomaly end time:", endTime.toISOString())
      } else {
        endTime = new Date()
        console.log(" Using current time as end time:", endTime.toISOString())
      }

      // Determine start time
      if (effectiveStartDate && effectiveStartTime) {
        // Use manually selected start date and time
        const [hours, minutes] = effectiveStartTime.split(":")
        startTime = new Date(effectiveStartDate)
        startTime.setHours(Number.parseInt(hours), Number.parseInt(minutes), 0, 0)
        console.log(" Using manual start time:", startTime.toISOString())
      } else if (anomaly.start_time) {
        startTime = new Date(anomaly.start_time)
        console.log(" Using anomaly start time:", startTime.toISOString())
      } else {
        // Default: 24 hours before end time
        startTime = new Date(endTime.getTime() - 24 * 60 * 60 * 1000)
        console.log(" Using default start time (24h before end):", startTime.toISOString())
      }

      console.log(" Final query range - Start:", startTime.toISOString(), "End:", endTime.toISOString())

      // Build query parameters
      const params = new URLSearchParams({
        service_type: anomaly.service.type,
        metric: selectedMetric,
        dimensions: JSON.stringify(selectedDimensions),
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
      })

      console.log(" Query parameters:", params.toString())

      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.TELEMETRY_QUERY}?${params.toString()}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        console.error("Failed to fetch telemetry data")
        setTelemetryData([])
        return
      }

      const data = await response.json()
      console.log(" Fetched telemetry data:", data)

      if (data.telemetry_data && typeof data.telemetry_data === "object") {
        // Convert telemetry_data from {timestamp: value} to array format
        const telemetryArray = Object.entries(data.telemetry_data)
          .map(([timestamp, value]) => ({
            timestamp: Number.parseInt(timestamp),
            value: typeof value === "number" ? value : Number.parseFloat(String(value)),
          }))
          .sort((a, b) => a.timestamp - b.timestamp)

        if (telemetryArray.length > 0) {
          console.log(" Converted telemetry data to array:", telemetryArray.length, "points")
          console.log(
            " First data point:",
            new Date(telemetryArray[0].timestamp * 1000).toISOString(),
            "value:",
            telemetryArray[0].value,
          )
          console.log(
            " Last data point:",
            new Date(telemetryArray[telemetryArray.length - 1].timestamp * 1000).toISOString(),
            "value:",
            telemetryArray[telemetryArray.length - 1].value,
          )
          setTelemetryData(telemetryArray)
          // Clear annotations when new data is loaded
          setAnnotations([])
        } else {
          console.log("No telemetry data points returned")
          setTelemetryData([])
        }
      } else {
        console.error("Invalid telemetry data format")
        setTelemetryData([])
      }
    } catch (error) {
      console.error("Error fetching telemetry data:", error)
      setTelemetryData([])
    } finally {
      setLoadingTelemetry(false)
    }
  }

  const handleMetricSelection = (metricName: string) => {
    setSelectedMetric(metricName)
    setSelectedDimensions({})

    const metric = availableMetrics.find((m) => m.name === metricName)
    if (metric) {
      // Try to get dimension values from cache (populated by backend)
      const cachedDimensionValues = (window as any).__dimensionValuesCache || {}
      const dimensionValues: Record<string, string[]> = {}

      metric.dimensions.forEach((dim) => {
        const cacheKey = `${metricName}:${dim}`

        if (cachedDimensionValues[cacheKey] && cachedDimensionValues[cacheKey].length > 0) {
          // Use values from backend
          dimensionValues[dim] = cachedDimensionValues[cacheKey]
        } else {
          // Fallback to mock values
          if (dim === "host") {
            dimensionValues[dim] = ["server1", "server2", "server3"]
          } else if (dim === "container") {
            dimensionValues[dim] = ["app1", "app2", "app3"]
          } else if (dim === "endpoint") {
            dimensionValues[dim] = ["/api/users", "/api/products", "/api/orders"]
          } else if (dim === "method") {
            dimensionValues[dim] = ["GET", "POST", "PUT", "DELETE"]
          } else if (dim === "status_code") {
            dimensionValues[dim] = ["200", "400", "404", "500"]
          } else if (dim === "error_type") {
            dimensionValues[dim] = ["timeout", "validation", "server_error"]
          } else {
            dimensionValues[dim] = ["value1", "value2", "value3"]
          }
        }
      })
      setAvailableDimensionValues(dimensionValues)
    }
  }

  const handleDimensionSelection = (dimension: string, value: string) => {
    setSelectedDimensions({
      ...selectedDimensions,
      [dimension]: value,
    })
  }

  const handleNextStep = async () => {
    if (currentStep === 1) {
      if (!selectedMetric) {
        alert("Please select a metric")
        return
      }
      if (Object.keys(selectedDimensions).length === 0) {
        alert("Please select at least one dimension value")
        return
      }
      // Fetch real telemetry data from backend
      await fetchTelemetryData()
    } else if (currentStep === 2) {
      if (annotations.length === 0) {
        alert("Please select a time window on the chart")
        return
      }
    } else if (currentStep === 3) {
      if (!description.trim()) {
        alert("Please add a description")
        return
      }
    }
    setCurrentStep(currentStep + 1)
  }

  const handlePreviousStep = () => {
    setCurrentStep(currentStep - 1)
  }

  const handleStartDateChange = (date: Date | undefined) => {
    console.log(" Start date changed to:", date)
    setManualStartDate(date)
    // Pass the new date directly to avoid stale state
    if (date && manualStartTime && currentStep === 2 && selectedMetric && Object.keys(selectedDimensions).length > 0) {
      fetchTelemetryData(date, manualStartTime, manualEndDate, manualEndTime)
    }
  }

  const handleEndDateChange = (date: Date | undefined) => {
    console.log(" End date changed to:", date)
    setManualEndDate(date)
    // Pass the new date directly to avoid stale state
    if (date && manualEndTime && currentStep === 2 && selectedMetric && Object.keys(selectedDimensions).length > 0) {
      fetchTelemetryData(manualStartDate, manualStartTime, date, manualEndTime)
    }
  }

  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = e.target.value
    console.log(" Start time changed to:", time)
    setManualStartTime(time)
    // Pass the new time directly to avoid stale state
    if (manualStartDate && time && currentStep === 2 && selectedMetric && Object.keys(selectedDimensions).length > 0) {
      fetchTelemetryData(manualStartDate, time, manualEndDate, manualEndTime)
    }
  }

  const handleEndTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = e.target.value
    console.log(" End time changed to:", time)
    setManualEndTime(time)
    // Pass the new time directly to avoid stale state
    if (manualEndDate && time && currentStep === 2 && selectedMetric && Object.keys(selectedDimensions).length > 0) {
      fetchTelemetryData(manualStartDate, manualStartTime, manualEndDate, time)
    }
  }

  const handleChartMouseDown = (e: any) => {
    if (!e || !e.activeLabel) return
    const timestamp = e.activeLabel
    console.log(" Chart mouse down at timestamp:", timestamp, "Date:", new Date(timestamp * 1000).toISOString())
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

    console.log(" Chart selection complete:", {
      x1,
      x2,
      x1Date: new Date(x1 * 1000).toISOString(),
      x2Date: new Date(x2 * 1000).toISOString(),
      duration: (x2 - x1) / 60,
      concernScore,
    })

    if (x2 - x1 > 0) {
      const newAnnotation: AnnotationBox = {
        id: `annotation-${Date.now()}`,
        x1,
        x2,
        color: getBandColor(concernScore),
      }

      console.log(" Creating annotation:", newAnnotation)
      setAnnotations([newAnnotation])

      const startDate = new Date(x1 * 1000)
      const endDate = new Date(x2 * 1000)
      setManualStartDate(startDate)
      setManualEndDate(endDate)
      setManualStartTime(formatTimeForInput(startDate))
      setManualEndTime(formatTimeForInput(endDate))
    }

    setIsDrawing(false)
    setDrawStart(null)
    setDrawEnd(null)
  }

  const formatTimeForInput = (date: Date) => {
    const hours = String(date.getHours()).padStart(2, "0")
    const minutes = String(date.getMinutes()).padStart(2, "0")
    return `${hours}:${minutes}`
  }

  const handleManualTimeChange = () => {
    if (!manualStartDate || !manualEndDate || !manualStartTime || !manualEndTime) {
      return
    }

    try {
      // Parse time strings
      const [startHours, startMinutes] = manualStartTime.split(":").map(Number)
      const [endHours, endMinutes] = manualEndTime.split(":").map(Number)

      // Create new dates with the specified times
      const startDateTime = new Date(manualStartDate)
      startDateTime.setHours(startHours, startMinutes, 0, 0)

      const endDateTime = new Date(manualEndDate)
      endDateTime.setHours(endHours, endMinutes, 0, 0)

      // Validate that end is after start
      if (endDateTime <= startDateTime) {
        alert("End time must be after start time")
        return
      }

      // Update chart annotation
      const x1 = Math.floor(startDateTime.getTime() / 1000)
      const x2 = Math.floor(endDateTime.getTime() / 1000)

      console.log(" Manual time change:", {
        x1,
        x2,
        x1Date: startDateTime.toISOString(),
        x2Date: endDateTime.toISOString(),
        chartDataRange:
          telemetryData.length > 0
            ? {
                min: telemetryData[0].timestamp,
                max: telemetryData[telemetryData.length - 1].timestamp,
                minDate: new Date(telemetryData[0].timestamp * 1000).toISOString(),
                maxDate: new Date(telemetryData[telemetryData.length - 1].timestamp * 1000).toISOString(),
              }
            : "No data",
      })

      const newAnnotation: AnnotationBox = {
        id: `annotation-${Date.now()}`,
        x1,
        x2,
        color: getBandColor(concernScore),
      }

      console.log(" Setting annotation from manual input:", newAnnotation)
      setAnnotations([newAnnotation])
    } catch (error) {
      console.error(" Error parsing manual time:", error)
      alert("Invalid time format")
    }
  }

  useEffect(() => {
    if (manualStartDate && manualEndDate && manualStartTime && manualEndTime) {
      handleManualTimeChange()
    }
  }, [manualStartDate, manualEndDate, manualStartTime, manualEndTime])

  const getBandColor = (score: number) => {
    if (score >= 0.8) return "#ef4444" // red-500
    if (score >= 0.6) return "#f97316" // orange-500
    if (score >= 0.4) return "#eab308" // yellow-500
    return "#22c55e" // green-500
  }

  const handleAddCustomField = () => {
    setCustomFields([...customFields, { key: "", value: "" }])
  }

  const handleUpdateCustomField = (index: number, field: "key" | "value", newValue: string) => {
    const updatedFields = [...customFields]
    updatedFields[index][field] = newValue
    setCustomFields(updatedFields)
  }

  const handleRemoveCustomField = (index: number) => {
    setCustomFields(customFields.filter((_, i) => i !== index))
  }

  const localDateToUTC = (date: Date) => {
    return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString()
  }

  const handleCreateSymptom = async () => {
    if (!anomaly) return

    // Get the annotation time range
    const annotationStart = annotations.length > 0 ? annotations[0].x1 : null
    const annotationEnd = annotations.length > 0 ? annotations[0].x2 : null

    // Filter telemetry data to only include points within the annotation window
    // Add some padding (e.g., 10% on each side) to provide context in the visualization
    let filteredTelemetryData = telemetryData
    if (annotationStart && annotationEnd) {
      const padding = (annotationEnd - annotationStart) * 0.1 // 10% padding
      const filterStart = annotationStart - padding
      const filterEnd = annotationEnd + padding

      filteredTelemetryData = telemetryData.filter(
        (point) => point.timestamp >= filterStart && point.timestamp <= filterEnd,
      )

      console.log("[v0] Filtered telemetry data:", {
        original: telemetryData.length,
        filtered: filteredTelemetryData.length,
        annotationRange: { start: annotationStart, end: annotationEnd },
        filterRange: { start: filterStart, end: filterEnd },
      })
    }

    // Convert telemetry array back to object format for storage
    const telemetryDataObject: Record<string, number> = {}
    filteredTelemetryData.forEach((point) => {
      telemetryDataObject[point.timestamp.toString()] = point.value
    })

    // Build the symptom object according to the data model
    // NOTE: No ID is included - this signals to the backend that it's a new symptom
    const symptomToAdd: any = {
      state: "confirmed",
      description: description,
      start_time:
        annotations.length > 0 ? localDateToUTC(new Date(annotations[0].x1 * 1000)) : localDateToUTC(new Date()),
      end_time: annotations.length > 0 ? localDateToUTC(new Date(annotations[0].x2 * 1000)) : null,
      confidence_score: 1.0,
      pattern: "",
      annotator: {
        name: "Human Annotator",
        version: 0,
        annotator_type: "human",
      },
      symptom: {
        concern_score: concernScore,
        metric: selectedMetric,
        dimensions: selectedDimensions,
        // Add custom fields to symptom
        ...customFields.reduce((acc: any, field: any) => {
          if (field.key && field.value) {
            acc[field.key] = field.value
          }
          return acc
        }, {}),
      },
      // Add metric_name and dimensions at symptom level (for display consistency)
      metric_name: selectedMetric,
      dimensions: selectedDimensions,
      // Include filtered telemetry data (only points near the annotation window)
      telemetry_data: telemetryDataObject,
    }

    console.log("[v0] Creating new symptom (without ID) with filtered telemetry data:", symptomToAdd)

    // Store the new symptom in sessionStorage to be picked up by the anomaly detail page
    // This follows the pattern where symptoms are only saved to backend when the entire
    // relevant state is saved from the anomaly detail page
    try {
      const pendingSymptoms = sessionStorage.getItem(`pending_symptoms_${anomalyId}`)
      const symptoms = pendingSymptoms ? JSON.parse(pendingSymptoms) : []
      symptoms.push(symptomToAdd)
      sessionStorage.setItem(`pending_symptoms_${anomalyId}`, JSON.stringify(symptoms))
      console.log("Stored pending symptom in sessionStorage for anomaly:", anomalyId)
    } catch (storageError) {
      console.error("Failed to store pending symptom in sessionStorage:", storageError)
    }

    // Navigate back to anomaly detail page
    // The anomaly detail page will:
    // 1. Load pending symptoms from sessionStorage
    // 2. Add them to the anomaly object in the UI
    // 3. When user clicks Save, send all symptoms (without IDs) to backend
    console.log("Navigating back to anomaly detail page")
    router.push(`/anomalies/${anomalyId}`)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-page-background flex items-center justify-center">
        <div className="text-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-page-background p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => router.push(`/anomalies/${anomalyId}`)}
            className="mb-4 text-muted-foreground"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back to Anomaly
          </Button>
          <h1 className="text-3xl font-bold text-foreground mb-2">Create New Symptom</h1>
          <p className="text-muted-foreground">
            Step {currentStep} of 4 •{" "}
            {currentStep === 1
              ? "Select Metric & Dimensions"
              : currentStep === 2
                ? "Select Time Window"
                : currentStep === 3
                  ? "Add Description & Concern Score"
                  : "Review & Add Custom Fields"}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex-1">
                <div
                  className={`h-2 rounded-full transition-colors ${step <= currentStep ? "bg-blue-600" : "bg-muted"}`}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <Card className="bg-card border-border mb-6">
          <CardContent className="p-6">
            {/* Step 1: Select Metric and Dimensions */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <Label className="text-foreground font-medium text-lg mb-3 block">Select Metric</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {availableMetrics.map((metric) => (
                      <Card
                        key={metric.name}
                        className={`cursor-pointer transition-all ${
                          selectedMetric === metric.name
                            ? "border-blue-500 bg-blue-500/10"
                            : "border-border bg-card hover:border-blue-500/50"
                        }`}
                        onClick={() => handleMetricSelection(metric.name)}
                      >
                        <CardContent className="p-4">
                          <div className="font-mono text-base text-foreground">{metric.name}</div>
                          <div className="text-sm text-muted-foreground mt-1">
                            Dimensions: {metric.dimensions.join(", ")}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>

                {selectedMetric && (
                  <div>
                    <Label className="text-foreground font-medium text-lg mb-3 block">Select Dimension Values</Label>
                    <div className="space-y-4">
                      {Object.entries(availableDimensionValues).map(([dimension, values]) => (
                        <div key={dimension}>
                          <Label className="text-sm text-foreground/80 mb-2 block capitalize">{dimension}</Label>
                          <div className="grid grid-cols-4 gap-2">
                            {values.map((value) => (
                              <Button
                                key={value}
                                variant={selectedDimensions[dimension] === value ? "default" : "outline"}
                                size="sm"
                                onClick={() => handleDimensionSelection(dimension, value)}
                                className={
                                  selectedDimensions[dimension] === value
                                    ? "bg-blue-600 hover:bg-blue-700 text-white"
                                    : "border-border bg-card hover:bg-muted"
                                }
                              >
                                {value}
                              </Button>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Select Time Window */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div>
                  <Label className="text-foreground font-medium text-lg mb-2 block">Select Time Window</Label>
                  <p className="text-sm text-muted-foreground mb-4">
                    Drag on the chart to select a time window, or use the date/time pickers below to enter times
                    manually
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="space-y-2">
                    <Label className="text-foreground text-sm">Start Date & Time</Label>
                    <div className="flex gap-2">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="flex-1 justify-start text-left font-normal bg-card border-border text-foreground hover:bg-muted"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {manualStartDate ? manualStartDate.toLocaleDateString() : "Pick a date"}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0 bg-card border-border">
                          <Calendar
                            mode="single"
                            selected={manualStartDate}
                            onSelect={handleStartDateChange}
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                      <Input
                        type="time"
                        value={manualStartTime}
                        onChange={handleStartTimeChange}
                        className="w-32 bg-card border-border text-foreground"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-foreground text-sm">End Date & Time</Label>
                    <div className="flex gap-2">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="flex-1 justify-start text-left font-normal bg-card border-border text-foreground hover:bg-muted"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {manualEndDate ? manualEndDate.toLocaleDateString() : "Pick a date"}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0 bg-card border-border">
                          <Calendar
                            mode="single"
                            selected={manualEndDate}
                            onSelect={handleEndDateChange}
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                      <Input
                        type="time"
                        value={manualEndTime}
                        onChange={handleEndTimeChange}
                        className="w-32 bg-card border-border text-foreground"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button
                    onClick={() => {
                      console.log(" Refresh button clicked, current telemetry data points:", telemetryData.length)
                      fetchTelemetryData()
                    }}
                    disabled={loadingTelemetry}
                    size="sm"
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    <RefreshCw className={`w-4 h-4 mr-2 ${loadingTelemetry ? "animate-spin" : ""}`} />
                    {loadingTelemetry ? "Refreshing..." : "Refresh Data"}
                  </Button>
                </div>

                {loadingTelemetry ? (
                  <div className="h-[500px] w-full border border-border rounded bg-card/50 flex items-center justify-center">
                    <div className="text-foreground text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                      <p>Loading telemetry data...</p>
                    </div>
                  </div>
                ) : (
                  <div
                    className="h-[500px] w-full border border-border rounded bg-card/50 cursor-crosshair relative"
                    onMouseUp={handleChartMouseUp}
                    onMouseLeave={handleChartMouseUp}
                  >
                    {annotations.length === 0 && (
                      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-600/90 text-white px-4 py-2 rounded-lg text-sm font-medium z-10 pointer-events-none">
                        Click and drag on the chart to select a time window
                      </div>
                    )}
                    {telemetryData.length > 0 && (
                      <div className="absolute top-4 right-4 bg-card/90 text-foreground px-3 py-2 rounded text-xs font-mono z-10 pointer-events-none border border-border">
                        <div>Data points: {telemetryData.length}</div>
                        <div>
                          Range: {new Date(telemetryData[0].timestamp * 1000).toLocaleTimeString()} -{" "}
                          {new Date(telemetryData[telemetryData.length - 1].timestamp * 1000).toLocaleTimeString()}
                        </div>
                        {annotations.length > 0 && (
                          <div className="mt-1 pt-1 border-t border-border">
                            <div>
                              Selection: {new Date(annotations[0].x1 * 1000).toLocaleTimeString()} -{" "}
                              {new Date(annotations[0].x2 * 1000).toLocaleTimeString()}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    <ChartContainer
                      config={{
                        value: {
                          label: selectedMetric || "Value",
                          color: "hsl(217, 91%, 60%)",
                        },
                      }}
                      className="h-full w-full"
                    >
                      <LineChart
                        key={telemetryData.length > 0 ? telemetryData[0].timestamp : "empty"}
                        data={telemetryData}
                        onMouseDown={handleChartMouseDown}
                        onMouseMove={handleChartMouseMove}
                        margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis
                          dataKey="timestamp"
                          tickFormatter={(value) => {
                            const date = new Date(value * 1000)
                            return date.toLocaleString("en-US", {
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          }}
                          className="text-muted-foreground"
                          type="number"
                          domain={["dataMin", "dataMax"]}
                        />
                        <YAxis className="text-muted-foreground" />
                        <ChartTooltip
                          content={<ChartTooltipContent />}
                          labelFormatter={(value) => new Date(value * 1000).toLocaleString()}
                        />
                        <Line type="monotone" dataKey="value" stroke="var(--color-value)" strokeWidth={2} dot={false} />

                        {/* Annotations */}
                        {annotations.map((annotation) => {
                          console.log(" Rendering annotation:", annotation)
                          return (
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
                          )
                        })}

                        {/* Current drawing */}
                        {isDrawing && drawStart !== null && drawEnd !== null && (
                          <ReferenceArea
                            x1={Math.min(drawStart, drawEnd)}
                            x2={Math.max(drawStart, drawEnd)}
                            stroke="#3b82f6"
                            strokeOpacity={0.8}
                            fill="#3b82f6"
                            fillOpacity={0.3}
                            strokeWidth={2}
                          />
                        )}
                      </LineChart>
                    </ChartContainer>
                  </div>
                )}

                {annotations.length > 0 && (
                  <div className="bg-card border border-border rounded p-3">
                    <p className="text-sm text-foreground/80">
                      Selected time window:{" "}
                      <span className="text-foreground font-mono">
                        {new Date(annotations[0].x1 * 1000).toLocaleString()} →{" "}
                        {new Date(annotations[0].x2 * 1000).toLocaleString()}
                      </span>
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Description and Concern Score */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <div>
                  <Label className="text-foreground font-medium text-lg mb-2 block">Description</Label>
                  <Textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe the symptom..."
                    className="bg-card border-border text-foreground min-h-[120px]"
                  />
                </div>

                <div>
                  <Label className="text-foreground font-medium text-lg mb-2 block">
                    Concern Score: {Math.round(concernScore * 100)}%
                  </Label>
                  <Slider
                    value={[concernScore]}
                    onValueChange={(value: number[]) => setConcernScore(value[0])}
                    min={0}
                    max={1}
                    step={0.01}
                    className="mb-2"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Low Concern</span>
                    <span>High Concern</span>
                  </div>
                </div>

                <div className="bg-card border border-border rounded p-4 space-y-2">
                  <h3 className="text-foreground font-medium mb-3">Auto-populated Fields</h3>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-muted-foreground">State:</span>
                      <span className="text-foreground ml-2">Confirmed</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Confidence Score:</span>
                      <span className="text-foreground ml-2">100%</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Annotator Type:</span>
                      <span className="text-foreground ml-2">Human</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Annotator Name:</span>
                      <span className="text-foreground ml-2">Human Annotator</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Custom Fields and Summary */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div>
                  <Label className="text-foreground font-medium text-lg mb-2 block">Custom Fields (Optional)</Label>
                  <p className="text-sm text-muted-foreground mb-4">Add additional key-value pairs to the symptom</p>

                  <div className="space-y-3">
                    {customFields.map((field, index) => (
                      <div key={index} className="flex gap-2">
                        <Input
                          placeholder="Key"
                          value={field.key}
                          onChange={(e) => handleUpdateCustomField(index, "key", e.target.value)}
                          className="bg-card border-border text-foreground"
                        />
                        <Input
                          placeholder="Value"
                          value={field.value}
                          onChange={(e) => handleUpdateCustomField(index, "value", e.target.value)}
                          className="bg-card border-border text-foreground"
                        />
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRemoveCustomField(index)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>

                  <Button
                    onClick={handleAddCustomField}
                    variant="outline"
                    size="sm"
                    className="mt-3 border-border bg-transparent"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Custom Field
                  </Button>
                </div>

                <div className="bg-card border border-border rounded p-4">
                  <h3 className="text-foreground font-medium mb-3">Summary</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Metric:</span>
                      <span className="text-foreground ml-2 font-mono">{selectedMetric}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Dimensions:</span>
                      <span className="text-foreground ml-2">
                        {Object.entries(selectedDimensions)
                          .map(([k, v]) => `${k}=${v}`)
                          .join(", ")}
                      </span>
                    </div>
                    {annotations.length > 0 && (
                      <div>
                        <span className="text-muted-foreground">Time Window:</span>
                        <span className="text-foreground ml-2 font-mono text-xs">
                          {new Date(annotations[0].x1 * 1000).toLocaleString()} →{" "}
                          {new Date(annotations[0].x2 * 1000).toLocaleString()}
                        </span>
                      </div>
                    )}
                    <div>
                      <span className="text-muted-foreground">Concern Score:</span>
                      <span className="text-foreground ml-2">{Math.round(concernScore * 100)}%</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Description:</span>
                      <span className="text-foreground ml-2">{description}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePreviousStep}
            disabled={currentStep === 1}
            className="border-border text-foreground bg-transparent"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          {currentStep < 4 ? (
            <Button onClick={handleNextStep} className="bg-blue-600 hover:bg-blue-700 text-white">
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleCreateSymptom} className="bg-green-600 hover:bg-green-700 text-white">
              <Check className="w-4 h-4 mr-2" />
              Create Symptom
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
