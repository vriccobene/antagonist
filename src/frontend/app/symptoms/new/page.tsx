"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Plus,
  Trash2,
  Server,
  Activity,
  Tag,
  Settings,
  X,
  Search,
  ZoomIn,
  ZoomOut,
  Sliders,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChartContainer } from "@/components/ui/chart"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ReferenceArea, Legend } from "recharts"
import { API_BASE_URL, ENDPOINTS } from "@/app/api"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { 
  localDateToUTC, 
  formatTime, 
  formatDateTime as formatDateTimeDisplay 
} from "@/lib/timezone-utils"

interface Service {
  id: string
  name?: string
  type?: string
  metadata?: Record<string, string | number>
}

interface MetricData {
  name: string
  dimensions: string[]
}

interface TimeseriesPoint {
  timestamp: number
  value: number
}

interface TaggedInterval {
  start: number
  end: number
}

interface CustomField {
  id: string
  name: string
  type: "string" | "integer" | "float" | "enum" // Added float type
  value: string | number
  enumOptions?: string[]
}

export default function CreateSymptomPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [services, setServices] = useState<Service[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedServiceType, setSelectedServiceType] = useState<string>("all")
  const [metadataFilters, setMetadataFilters] = useState<Record<string, string>>({})

  const [selectedService, setSelectedService] = useState<Service | null>(null)
  const [availableMetrics, setAvailableMetrics] = useState<MetricData[]>([])
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null)
  const [selectedDimensionValues, setSelectedDimensionValues] = useState<Record<string, string[]>>({})
  const [availableDimensionValues, setAvailableDimensionValues] = useState<Record<string, string[]>>({})

  const [timeWindow, setTimeWindow] = useState<"1h" | "6h" | "24h" | "7d" | "30d">("24h")
  const [zoomLevel, setZoomLevel] = useState(1)

  const [timeseriesData, setTimeseriesData] = useState<Record<string, TimeseriesPoint[]>>({})
  const [taggedIntervals, setTaggedIntervals] = useState<TaggedInterval[]>([])
  const [concernScore, setConcernScore] = useState(0.5)
  const [confidenceScore, setConfidenceScore] = useState(0.5) // Added confidence score state
  const [customFields, setCustomFields] = useState<CustomField[]>([])
  const [loading, setLoading] = useState(false)
  const [showJsonModal, setShowJsonModal] = useState(false)
  const [anomalyJson, setAnomalyJson] = useState<string>("")

  const chartRef = useRef<any>(null)
  const chartContainerRef = useRef<HTMLDivElement>(null)

  const steps = [
    { number: 1, title: "Choose Entity", icon: Server },
    { number: 2, title: "Choose Metric", icon: Activity },
    { number: 3, title: "Set Dimensions", icon: Sliders },
    { number: 4, title: "Tag Timeseries", icon: Tag },
    { number: 5, title: "Configure Details", icon: Settings },
  ]

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.SERVICE}`)

        if (response.ok) {
          const data = await response.json()
          setServices(data)
        } else {
          console.error("Failed to fetch services")
          setServices([])
        }
      } catch (error) {
        console.error("Error fetching services:", error)
        setServices([])
      }
    }
    fetchServices()
  }, [])

  // Fetch metrics when service is selected
  useEffect(() => {
    if (selectedService) {
      // Mock metrics data - in production, fetch from API
      setAvailableMetrics([
        { name: "response_time_ms", dimensions: ["endpoint", "method", "status_code"] },
        { name: "error_rate", dimensions: ["endpoint", "error_type"] },
        { name: "request_count", dimensions: ["endpoint", "method"] },
        { name: "cpu_usage_percent", dimensions: ["host", "container"] },
        { name: "memory_usage_mb", dimensions: ["host", "container"] },
        { name: "disk_io_ops", dimensions: ["host", "device"] },
        { name: "network_throughput", dimensions: ["host", "interface"] },
      ])
    }
  }, [selectedService])

  useEffect(() => {
    if (selectedMetric) {
      const metric = availableMetrics.find((m) => m.name === selectedMetric)
      if (metric) {
        // Mock dimension values - in production, fetch from API
        const dimensionValues: Record<string, string[]> = {}
        metric.dimensions.forEach((dim) => {
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
          } else if (dim === "device") {
            dimensionValues[dim] = ["sda", "sdb", "nvme0"]
          } else if (dim === "interface") {
            dimensionValues[dim] = ["eth0", "eth1", "lo"]
          } else {
            dimensionValues[dim] = ["value1", "value2", "value3"]
          }
        })
        setAvailableDimensionValues(dimensionValues)
        // Reset selected dimension values when metric changes
        setSelectedDimensionValues({})
      }
    }
  }, [selectedMetric, availableMetrics])

  useEffect(() => {
    if (selectedMetric && Object.keys(selectedDimensionValues).length > 0) {
      const now = Date.now()
      const newTimeseriesData: Record<string, TimeseriesPoint[]> = {}

      // Calculate time range based on selected window and zoom
      let timeRangeMs = 24 * 60 * 60 * 1000 // default 24h
      let intervalMs = 60000 // 1 minute

      switch (timeWindow) {
        case "1h":
          timeRangeMs = 60 * 60 * 1000
          intervalMs = 30000 // 30 seconds
          break
        case "6h":
          timeRangeMs = 6 * 60 * 60 * 1000
          intervalMs = 60000 // 1 minute
          break
        case "24h":
          timeRangeMs = 24 * 60 * 60 * 1000
          intervalMs = 5 * 60000 // 5 minutes
          break
        case "7d":
          timeRangeMs = 7 * 24 * 60 * 60 * 1000
          intervalMs = 60 * 60000 // 1 hour
          break
        case "30d":
          timeRangeMs = 30 * 24 * 60 * 60 * 1000
          intervalMs = 4 * 60 * 60000 // 4 hours
          break
      }

      // Apply zoom level
      timeRangeMs = timeRangeMs / zoomLevel

      const numPoints = Math.floor(timeRangeMs / intervalMs)

      // Generate timeseries for all combinations of selected dimension values
      const generateCombinations = (
        dims: string[],
        values: Record<string, string[]>,
        current: Record<string, string> = {},
        index = 0,
      ): Record<string, string>[] => {
        if (index === dims.length) {
          return [current]
        }

        const dim = dims[index]
        const dimValues = values[dim] || []
        const combinations: Record<string, string>[] = []

        for (const value of dimValues) {
          combinations.push(...generateCombinations(dims, values, { ...current, [dim]: value }, index + 1))
        }

        return combinations
      }

      const dimensionKeys = Object.keys(selectedDimensionValues)
      const combinations = generateCombinations(dimensionKeys, selectedDimensionValues)

      combinations.forEach((dims, seriesIndex) => {
        const points: TimeseriesPoint[] = []
        const baseValue = 100 + seriesIndex * 30 // Different base for each series

        for (let i = 0; i < numPoints; i++) {
          const timestamp = now - (numPoints - i) * intervalMs
          const randomVariation = Math.random() * 20
          // Add anomaly spike around 60-70% of the timeline
          const anomalyStart = Math.floor(numPoints * 0.6)
          const anomalyEnd = Math.floor(numPoints * 0.7)
          const anomalyBoost = i >= anomalyStart && i <= anomalyEnd ? Math.random() * 60 : 0
          points.push({
            timestamp,
            value: baseValue + randomVariation + anomalyBoost,
          })
        }

        // Create a unique key for each timeseries with dimension labels
        const seriesKey = `${selectedMetric}{${Object.entries(dims)
          .map(([k, v]) => `${k}="${v}"`)
          .join(", ")}}`
        newTimeseriesData[seriesKey] = points
      })

      setTimeseriesData(newTimeseriesData)
    } else {
      setTimeseriesData({})
    }
  }, [selectedMetric, selectedDimensionValues, timeWindow, zoomLevel])

  const serviceTypes = ["all", ...Array.from(new Set(services.map((s) => s.type).filter(Boolean)))]

  const metadataKeys = Array.from(new Set(services.flatMap((s) => (s.metadata ? Object.keys(s.metadata) : []))))

  const filteredServices = services.filter((service) => {
    // Search filter
    const matchesSearch =
      searchQuery === "" ||
      service.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.id.toLowerCase().includes(searchQuery.toLowerCase())

    // Type filter
    const matchesType = selectedServiceType === "all" || service.type === selectedServiceType

    // Metadata filters
    const matchesMetadata = Object.entries(metadataFilters).every(([key, value]) => {
      if (!value) return true
      return service.metadata?.[key]?.toString().toLowerCase().includes(value.toLowerCase())
    })

    return matchesSearch && matchesType && matchesMetadata
  })

  const hasActiveFilters =
    searchQuery !== "" ||
    selectedServiceType !== "all" ||
    (Object.keys(metadataFilters).length > 0 && Object.values(metadataFilters)[0] !== "")

  const formatChartData = () => {
    const allSeriesKeys = Object.keys(timeseriesData)
    if (allSeriesKeys.length === 0) return []

    const firstSeries = timeseriesData[allSeriesKeys[0]] || []

    return firstSeries.map((point, index) => {
      const dataPoint: any = {
        timestamp: point.timestamp,
        formattedTime: new Date(point.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        fullTimestamp: new Date(point.timestamp).toLocaleString(),
      }

      allSeriesKeys.forEach((seriesKey) => {
        const seriesData = timeseriesData[seriesKey]
        if (seriesData && seriesData[index]) {
          dataPoint[seriesKey] = seriesData[index].value
        }
      })

      return dataPoint
    })
  }

  const [dragStart, setDragStart] = useState<number | null>(null)
  const [dragEnd, setDragEnd] = useState<number | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const getTimestampFromMouseEvent = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!chartContainerRef.current) return null

    const rect = chartContainerRef.current.getBoundingClientRect()
    const chartData = formatChartData()
    if (chartData.length === 0) return null

    // Calculate relative X position (0 to 1)
    const relativeX = (e.clientX - rect.left) / rect.width

    // Account for chart padding (approximate)
    const paddingLeft = 60 / rect.width // Y-axis takes ~60px
    const paddingRight = 20 / rect.width // Right padding ~20px
    const chartWidth = 1 - paddingLeft - paddingRight

    // Adjust relative position to account for padding
    const adjustedX = (relativeX - paddingLeft) / chartWidth

    // Clamp between 0 and 1
    const clampedX = Math.max(0, Math.min(1, adjustedX))

    // Map to timestamp range
    const minTimestamp = chartData[0].timestamp
    const maxTimestamp = chartData[chartData.length - 1].timestamp
    const timestamp = minTimestamp + (maxTimestamp - minTimestamp) * clampedX

    console.log("Mouse position:", {
      relativeX,
      adjustedX,
      clampedX,
      timestamp: new Date(timestamp).toLocaleTimeString(),
    })

    return timestamp
  }

  const handleChartMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    const timestamp = getTimestampFromMouseEvent(e)
    if (timestamp) {
      console.log("Drag started at:", new Date(timestamp).toLocaleTimeString())
      setIsDragging(true)
      setDragStart(timestamp)
      setDragEnd(timestamp)
    }
  }

  const handleChartMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isDragging && dragStart) {
      const timestamp = getTimestampFromMouseEvent(e)
      if (timestamp) {
        setDragEnd(timestamp)
      }
    }
  }

  const handleChartMouseUp = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isDragging && dragStart && dragEnd && dragStart !== dragEnd) {
      const newInterval = {
        start: Math.min(dragStart, dragEnd),
        end: Math.max(dragStart, dragEnd),
      }
      console.log("Tag created:", {
        start: new Date(newInterval.start).toLocaleTimeString(),
        end: new Date(newInterval.end).toLocaleTimeString(),
      })
      setTaggedIntervals([...taggedIntervals, newInterval])
    }
    setIsDragging(false)
    setDragStart(null)
    setDragEnd(null)
  }

  // Removed toggleMetricSelection as only one metric can be selected
  // const toggleMetricSelection = (metricName: string) => {
  //   if (selectedMetrics.includes(metricName)) {
  //     setSelectedMetrics(selectedMetrics.filter((m) => m !== metricName))
  //   } else {
  //     setSelectedMetrics([...selectedMetrics, metricName])
  //   }
  // }

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev * 2, 16))
  }

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(prev / 2, 1))
  }

  const toggleDimensionValue = (dimension: string, value: string) => {
    setSelectedDimensionValues((prev) => ({
      ...prev,
      [dimension]: [value], // Only one value per dimension
    }))
  }

  const addCustomField = () => {
    setCustomFields([
      ...customFields,
      {
        id: `field-${Date.now()}`,
        name: "",
        type: "string",
        value: "",
      },
    ])
  }

  const updateCustomField = (id: string, updates: Partial<CustomField>) => {
    setCustomFields(customFields.map((field) => (field.id === id ? { ...field, ...updates } : field)))
  }

  const removeCustomField = (id: string) => {
    setCustomFields(customFields.filter((field) => field.id !== id))
  }

  const addEnumOption = (fieldId: string) => {
    const field = customFields.find((f) => f.id === fieldId)
    if (field && field.type === "enum") {
      updateCustomField(fieldId, {
        enumOptions: [...(field.enumOptions || []), ""],
      })
    }
  }

  const updateEnumOption = (fieldId: string, index: number, value: string) => {
    const field = customFields.find((f) => f.id === fieldId)
    if (field && field.enumOptions) {
      const newOptions = [...field.enumOptions]
      newOptions[index] = value
      updateCustomField(field.id, { enumOptions: newOptions })
    }
  }

  const removeEnumOption = (fieldId: string, index: number) => {
    const field = customFields.find((f) => f.id === fieldId)
    if (field && field.enumOptions) {
      updateCustomField(field.id, {
        enumOptions: field.enumOptions.filter((_, i) => i !== index),
      })
    }
  }

  // Build Anomaly JSON object
  const buildAnomalyJson = () => {
    // Get the first tagged interval for start_time and end_time
    const firstInterval = taggedIntervals[0]

    // Build dimensions object (only selected dimension values)
    const symptomDimensions: Record<string, string | number> = {}
    Object.entries(selectedDimensionValues).forEach(([dim, values]) => {
      symptomDimensions[dim] = values.join(",")
    })

    // Build custom fields object (separate from dimensions)
    const customFieldsData: Record<string, string | number> = {}
    customFields.forEach((field) => {
      if (field.name && field.value !== "") {
        customFieldsData[field.name] = field.value
      }
    })

    const anomaly = {
      state: "unknown",
      description: `Symptom detected for ${selectedMetric} on ${selectedService?.name || selectedService?.id}`,
      start_time: firstInterval ? localDateToUTC(new Date(firstInterval.start)) : localDateToUTC(new Date()),
      end_time: firstInterval ? localDateToUTC(new Date(firstInterval.end)) : null,
      confidence_score: confidenceScore,
      pattern: null,
      annotator: {
        name: "user",
        version: 1,
        annotator_type: "human",
      },
      symptom: {
        concern_score: concernScore,
        metric: selectedMetric,
        dimensions: symptomDimensions,
        ...customFieldsData, // Custom fields at symptom level
      },
    }

    return JSON.stringify(anomaly, null, 2)
  }

  const handleCreateSymptom = () => {
    const json = buildAnomalyJson()
    setAnomalyJson(json)
    setShowJsonModal(true)
  }

  const handleFinalSubmit = async () => {
    setLoading(true)
    try {
      const anomalyData = JSON.parse(anomalyJson)

      // In production, POST to API
      console.log("Creating symptom with anomaly data:", anomalyData)

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      router.push("/symptoms")
    } catch (error) {
      console.error("Failed to create symptom:", error)
    } finally {
      setLoading(false)
      setShowJsonModal(false)
    }
  }

  const copyJsonToClipboard = () => {
    navigator.clipboard.writeText(anomalyJson)
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const symptomData = {
        concern_score: concernScore,
        confidence_score: confidenceScore, // Added confidence score to submission
        metric: selectedMetric, // Primary metric
        dimensions: selectedDimensionValues, // This should be selectedDimensionValues after step 3
        tagged_intervals: taggedIntervals,
        // Add custom fields to the symptom data
        ...customFields.reduce(
          (acc, field) => ({
            ...acc,
            [field.name]: field.value,
          }),
          {},
        ),
      }

      // In production, POST to API
      console.log("Creating symptom:", symptomData)
      console.log("Tagged intervals:", taggedIntervals)

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      router.push("/symptoms")
    } catch (error) {
      console.error("Failed to create symptom:", error)
    } finally {
      setLoading(false)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return selectedService !== null
      case 2:
        return selectedMetric !== null
      case 3:
        return (
          Object.keys(selectedDimensionValues).length > 0 &&
          Object.values(selectedDimensionValues).some((values) => values.length > 0)
        )
      case 4:
        return taggedIntervals.length > 0
      case 5:
        return true
      default:
        return false
    }
  }

  const metricColors = [
    "hsl(180, 100%, 50%)", // cyan
    "hsl(45, 100%, 50%)", // yellow/gold
    "hsl(120, 60%, 50%)", // green
    "hsl(0, 100%, 50%)", // red
    "hsl(270, 100%, 50%)", // purple
    "hsl(30, 100%, 50%)", // orange
    "hsl(200, 100%, 50%)", // light blue
  ]

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => router.push("/symptoms")} className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Symptoms
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Create New Symptom</h1>
              <p className="text-sm text-muted-foreground">
                Define a new symptom by selecting a monitored entity, metric, and tagging anomalous behavior
              </p>
            </div>
          </div>
        </div>

        {/* Step Indicator */}
        <div className="mb-3">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const StepIcon = step.icon
              const isActive = currentStep === step.number
              const isCompleted = currentStep > step.number
              return (
                <div key={step.number} className="flex items-center flex-1">
                  <div className="flex flex-col items-center flex-1">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                        isCompleted
                          ? "bg-green-600 border-green-600"
                          : isActive
                            ? "bg-blue-600 border-blue-600"
                            : "bg-muted border-border"
                      }`}
                    >
                      {isCompleted ? (
                        <Check className="w-5 h-5 text-white" />
                      ) : (
                        <StepIcon className="w-5 h-5 text-white" />
                      )}
                    </div>
                    <div className="mt-1.5 text-center">
                      <div
                        className={`text-xs font-medium ${isActive ? "text-blue-400" : isCompleted ? "text-green-400" : "text-muted-foreground"}`}
                      >
                        {step.title}
                      </div>
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={`h-0.5 flex-1 mx-2 transition-colors ${isCompleted ? "bg-green-600" : "bg-border"}`}
                    />
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Step Content */}
        <Card className="bg-gray-900 border-gray-700">
          <CardContent className="p-3">
            {/* Step 1: Select Monitored Entity */}
            {currentStep === 1 && (
              <div className="space-y-3">
                <div>
                  <h2 className="text-xl font-semibold text-foreground mb-1">Choose Entity</h2>
                  <p className="text-sm text-muted-foreground">
                    Choose the monitored entity that this symptom is associated with
                  </p>
                </div>

                <div className="space-y-2 p-2 bg-gray-800 rounded-lg border border-gray-700">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    {/* Search */}
                    <div>
                      <Label className="text-xs font-medium text-foreground mb-1.5 block">Search</Label>
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                          placeholder="Search entities..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="pl-10 bg-gray-900 border-gray-600 text-foreground"
                        />
                      </div>
                    </div>

                    {/* Service Type Filter */}
                    <div>
                      <Label className="text-xs font-medium text-foreground mb-1.5 block">Entity Type</Label>
                      <Select value={selectedServiceType} onValueChange={setSelectedServiceType}>
                        <SelectTrigger className="bg-gray-900 border-gray-600 text-foreground">
                          <SelectValue placeholder="All types" />
                        </SelectTrigger>
                        <SelectContent>
                          {serviceTypes.map((type) => (
                            <SelectItem key={type} value={type}>
                              {type === "all" ? "All Types" : type}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Metadata Filter */}
                    {metadataKeys.length > 0 && (
                      <div>
                        <Label className="text-xs font-medium text-foreground mb-1.5 block">Filter by Metadata</Label>
                        <Select
                          value={Object.keys(metadataFilters)[0] || "none"}
                          onValueChange={(key) => {
                            if (key && key !== "none") {
                              setMetadataFilters({ [key]: "" })
                            } else {
                              setMetadataFilters({})
                            }
                          }}
                        >
                          <SelectTrigger className="bg-gray-900 border-gray-600 text-foreground">
                            <SelectValue placeholder="Select metadata key" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">None</SelectItem>
                            {metadataKeys.map((key) => (
                              <SelectItem key={key} value={key}>
                                {key}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </div>

                  {/* Metadata Value Input */}
                  {Object.keys(metadataFilters).length > 0 && (
                    <div>
                      <Label className="text-xs font-medium text-foreground mb-1.5 block">
                        Filter by {Object.keys(metadataFilters)[0]} value
                      </Label>
                      <Input
                        placeholder={`Enter ${Object.keys(metadataFilters)[0]} value...`}
                        value={Object.values(metadataFilters)[0] || ""}
                        onChange={(e) => {
                          const key = Object.keys(metadataFilters)[0]
                          setMetadataFilters({ [key]: e.target.value })
                        }}
                        className="bg-gray-900 border-gray-600 text-foreground"
                      />
                    </div>
                  )}

                  {hasActiveFilters && (
                    <div className="text-xs text-muted-foreground">
                      Showing {filteredServices.length} of {services.length} entities
                    </div>
                  )}
                </div>

                {!hasActiveFilters ? (
                  <div className="text-center py-16 border border-dashed border-gray-600 rounded-lg bg-gray-900/50">
                    <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                    <h3 className="text-lg font-medium text-foreground mb-2">Apply Filters to View Entities</h3>
                    <p className="text-sm text-muted-foreground max-w-md mx-auto">
                      Use the search bar, entity type filter, or metadata filter above to find and select a monitored
                      entity.
                    </p>
                  </div>
                ) : filteredServices.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground border border-dashed border-gray-600 rounded-lg">
                    No entities match your filters. Try adjusting your search criteria.
                  </div>
                ) : (
                  <div className="border border-gray-700 rounded-lg overflow-hidden">
                    <Table>
                      <TableHeader>
                        <TableRow className="bg-gray-800 hover:bg-gray-800">
                          <TableHead className="text-foreground font-semibold">Name</TableHead>
                          <TableHead className="text-foreground font-semibold">ID</TableHead>
                          <TableHead className="text-foreground font-semibold">Type</TableHead>
                          <TableHead className="text-foreground font-semibold">Region</TableHead>
                          <TableHead className="text-foreground font-semibold">Version</TableHead>
                          <TableHead className="text-foreground font-semibold text-right">Action</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredServices.map((service) => (
                          <TableRow
                            key={service.id}
                            className={`cursor-pointer transition-colors ${
                              selectedService?.id === service.id
                                ? "bg-blue-950/30 hover:bg-blue-950/40"
                                : "hover:bg-gray-800"
                            }`}
                            onClick={() => setSelectedService(service)}
                          >
                            <TableCell className="font-medium">
                              <div className="flex items-center gap-2">
                                <Server className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                                <span className="text-foreground">{service.name || service.id}</span>
                              </div>
                            </TableCell>
                            <TableCell className="font-mono text-sm text-muted-foreground">{service.id}</TableCell>
                            <TableCell>
                              {service.type && (
                                <Badge variant="secondary" className="text-xs">
                                  {service.type}
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {service.metadata?.region || "-"}
                            </TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {service.metadata?.version || "-"}
                            </TableCell>
                            <TableCell className="text-right">
                              <Button
                                variant={selectedService?.id === service.id ? "default" : "outline"}
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setSelectedService(service)
                                }}
                                className={
                                  selectedService?.id === service.id
                                    ? "bg-blue-600 hover:bg-blue-700"
                                    : "border-gray-600 bg-gray-900"
                                }
                              >
                                {selectedService?.id === service.id ? (
                                  <>
                                    <Check className="w-4 h-4 mr-1" />
                                    Selected
                                  </>
                                ) : (
                                  "Select"
                                )}
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Choose Metric and Dimensions */}
            {currentStep === 2 && (
              <div className="space-y-3">
                <div>
                  <h2 className="text-xl font-semibold text-foreground mb-1">Choose Metric</h2>
                  <p className="text-sm text-muted-foreground">
                    Select a metric to monitor and preview its timeseries data
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-3">
                  {/* Left: Metric Selection */}
                  <div className="space-y-2">
                    <Label className="text-xs font-medium text-foreground mb-1.5 block">
                      Available Metrics (select one)
                    </Label>
                    <div className="space-y-0 max-h-[550px] overflow-y-auto pr-2">
                      {availableMetrics.map((metric) => (
                        <Card
                          key={metric.name}
                          className={`cursor-pointer transition-all hover:border-blue-500 ${
                            selectedMetric === metric.name
                              ? "border-blue-500 bg-blue-950/30"
                              : "border-gray-700 bg-gray-800"
                          }`}
                          onClick={() => setSelectedMetric(metric.name)}
                        >
                          <CardContent className="py-0 px-2 flex items-center gap-1 min-h-[24px]">
                            <div
                              className={`w-3 h-3 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                                selectedMetric === metric.name
                                  ? "border-blue-500 bg-blue-500"
                                  : "border-muted-foreground"
                              }`}
                            >
                              {selectedMetric === metric.name && (
                                <div className="w-1.5 h-1.5 rounded-full bg-white"></div>
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-mono text-xs text-foreground font-medium break-words leading-tight py-1">
                                {metric.name}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>

                  {/* Right: Timeseries Preview */}
                  <div className="flex flex-col">
                    {selectedMetric ? (
                      <>
                        <div className="p-2 bg-gray-800 rounded-lg border border-gray-700 space-y-2 mb-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Activity className="w-4 h-4 text-muted-foreground" />
                              <Label className="text-xs font-medium text-foreground">Time Window</Label>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleZoomOut}
                                disabled={zoomLevel <= 1}
                                title="Increase time window (show more time)"
                                className="border-gray-600 bg-gray-900"
                              >
                                <ZoomOut className="w-4 h-4" />
                              </Button>
                              <span className="text-sm text-muted-foreground min-w-[60px] text-center">
                                {zoomLevel}x zoom
                              </span>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleZoomIn}
                                disabled={zoomLevel >= 16}
                                title="Reduce time window (show less time, more detail)"
                                className="border-gray-600 bg-gray-900"
                              >
                                <ZoomIn className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {(["1h", "6h", "24h", "7d", "30d"] as const).map((window) => (
                              <Button
                                key={window}
                                variant={timeWindow === window ? "default" : "outline"}
                                size="sm"
                                onClick={() => setTimeWindow(window)}
                                className={
                                  timeWindow === window
                                    ? "bg-blue-600 hover:bg-blue-700"
                                    : "border-gray-600 bg-gray-900"
                                }
                              >
                                {window.toUpperCase()}
                              </Button>
                            ))}
                          </div>
                        </div>

                        <div className="h-[450px] border border-gray-700 rounded-lg bg-gray-900 p-2 overflow-hidden">
                          {Object.keys(timeseriesData).length > 0 ? (
                            <ChartContainer
                              config={Object.keys(timeseriesData).reduce(
                                (acc, seriesKey, index) => ({
                                  ...acc,
                                  [seriesKey]: {
                                    label: seriesKey,
                                    color: metricColors[index % metricColors.length],
                                  },
                                }),
                                {},
                              )}
                              className="h-full w-full"
                            >
                              <LineChart data={formatChartData()}>
                                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                <XAxis
                                  dataKey="timestamp"
                                  type="number"
                                  domain={["dataMin", "dataMax"]}
                                  tickFormatter={(value) =>
                                    new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                                  }
                                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                                  stroke="hsl(var(--border))"
                                />
                                <YAxis
                                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                                  stroke="hsl(var(--border))"
                                />
                                <Legend
                                  wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }}
                                  iconType="line"
                                  formatter={(value) => (
                                    <span style={{ color: "hsl(var(--foreground))" }}>{value}</span>
                                  )}
                                />
                                {Object.keys(timeseriesData).map((seriesKey, index) => (
                                  <Line
                                    key={seriesKey}
                                    type="monotone"
                                    dataKey={seriesKey}
                                    stroke={metricColors[index % metricColors.length]}
                                    strokeWidth={2}
                                    dot={false}
                                    activeDot={{ r: 4 }}
                                  />
                                ))}
                              </LineChart>
                            </ChartContainer>
                          ) : (
                            <div className="h-full flex items-center justify-center text-muted-foreground">
                              Loading timeseries data...
                            </div>
                          )}
                        </div>

                        <div className="text-xs text-muted-foreground mt-1.5">
                          Showing preview with all dimension combinations. You'll select specific dimensions in the next
                          step.
                        </div>
                      </>
                    ) : (
                      <div className="h-[450px] border border-dashed border-gray-700 rounded-lg flex items-center justify-center text-muted-foreground">
                        Select a metric to preview its timeseries data
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Set Dimensions */}
            {currentStep === 3 && (
              <div className="space-y-3">
                <div>
                  <h2 className="text-xl font-semibold text-foreground mb-1">Set Dimensions</h2>
                  <p className="text-sm text-muted-foreground">
                    Select one value for each dimension to identify the timeseries to monitor
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-3">
                  {/* Left: Dimension Selection */}
                  <div className="space-y-2">
                    {selectedMetric && (
                      <div className="p-2 bg-blue-950/20 border border-blue-500/30 rounded-lg">
                        <div className="flex items-center gap-2 text-sm">
                          <Activity className="w-4 h-4 text-blue-400" />
                          <span className="text-muted-foreground">Metric:</span>
                          <span className="font-mono font-medium text-foreground">{selectedMetric}</span>
                        </div>
                      </div>
                    )}

                    <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-2">
                      {Object.entries(availableDimensionValues).map(([dimension, values]) => (
                        <Card key={dimension} className="bg-gray-800 border-gray-700">
                          <CardHeader className="pb-1 px-2">
                            <CardTitle className="text-sm text-foreground flex items-center gap-2">
                              <Sliders className="w-3 h-3" />
                              {dimension}
                            </CardTitle>
                            <CardDescription className="text-muted-foreground text-xs">
                              Select one value
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-1 px-2 pb-2">
                            <div className="space-y-1">
                              {values.map((value) => {
                                const isSelected = selectedDimensionValues[dimension]?.[0] === value
                                return (
                                  <div
                                    key={value}
                                    className={`flex items-center gap-2 p-1 rounded border cursor-pointer transition-all ${
                                      isSelected
                                        ? "bg-blue-950/30 border-blue-500"
                                        : "bg-gray-900 border-gray-600 hover:border-blue-500/50"
                                    }`}
                                    onClick={() => toggleDimensionValue(dimension, value)}
                                  >
                                    <div
                                      className={`w-3 h-3 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                                        isSelected ? "border-blue-500 bg-blue-500" : "border-muted-foreground"
                                      }`}
                                    >
                                      {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white"></div>}
                                    </div>
                                    <span className="text-xs font-mono text-foreground">{value}</span>
                                  </div>
                                )
                              })}
                            </div>
                          </CardContent>
                        </Card>
                      ))}

                      {Object.keys(availableDimensionValues).length === 0 && (
                        <div className="text-center py-12 text-muted-foreground border border-dashed border-gray-600 rounded-lg">
                          No dimensions available for the selected metric.
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right: Timeseries Preview */}
                  <div className="flex flex-col">
                    {Object.keys(selectedDimensionValues).length > 0 ? (
                      <>
                        <div className="p-2 bg-gray-800 rounded-lg border border-gray-700 space-y-2 mb-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Activity className="w-4 h-4 text-muted-foreground" />
                              <Label className="text-xs font-medium text-foreground">Time Window</Label>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleZoomOut}
                                disabled={zoomLevel <= 1}
                                className="border-gray-600 bg-gray-900"
                              >
                                <ZoomOut className="w-4 h-4" />
                              </Button>
                              <span className="text-sm text-muted-foreground min-w-[60px] text-center">
                                {zoomLevel}x zoom
                              </span>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={handleZoomIn}
                                disabled={zoomLevel >= 16}
                                className="border-gray-600 bg-gray-900"
                              >
                                <ZoomIn className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {(["1h", "6h", "24h", "7d", "30d"] as const).map((window) => (
                              <Button
                                key={window}
                                variant={timeWindow === window ? "default" : "outline"}
                                size="sm"
                                onClick={() => setTimeWindow(window)}
                                className={
                                  timeWindow === window
                                    ? "bg-blue-600 hover:bg-blue-700"
                                    : "border-gray-600 bg-gray-900"
                                }
                              >
                                {window.toUpperCase()}
                              </Button>
                            ))}
                          </div>
                        </div>

                        <div className="h-[450px] border border-gray-700 rounded-lg bg-gray-900 p-2 overflow-hidden">
                          {Object.keys(timeseriesData).length > 0 ? (
                            <ChartContainer
                              config={Object.keys(timeseriesData).reduce(
                                (acc, seriesKey, index) => ({
                                  ...acc,
                                  [seriesKey]: {
                                    label: seriesKey,
                                    color: metricColors[index % metricColors.length],
                                  },
                                }),
                                {},
                              )}
                              className="h-full w-full"
                            >
                              <LineChart data={formatChartData()}>
                                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                <XAxis
                                  dataKey="timestamp"
                                  type="number"
                                  domain={["dataMin", "dataMax"]}
                                  tickFormatter={(value) =>
                                    new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                                  }
                                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                                  stroke="hsl(var(--border))"
                                />
                                <YAxis
                                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                                  stroke="hsl(var(--border))"
                                />
                                <Legend
                                  wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }}
                                  iconType="line"
                                  formatter={(value) => (
                                    <span style={{ color: "hsl(var(--foreground))" }}>{value}</span>
                                  )}
                                />
                                {Object.keys(timeseriesData).map((seriesKey, index) => (
                                  <Line
                                    key={seriesKey}
                                    type="monotone"
                                    dataKey={seriesKey}
                                    stroke={metricColors[index % metricColors.length]}
                                    strokeWidth={2}
                                    dot={false}
                                    activeDot={{ r: 4 }}
                                  />
                                ))}
                              </LineChart>
                            </ChartContainer>
                          ) : (
                            <div className="h-full flex items-center justify-center text-muted-foreground">
                              Loading timeseries data...
                            </div>
                          )}
                        </div>

                        <div className="text-xs text-muted-foreground mt-1.5">
                          Showing {Object.keys(timeseriesData).length} timeseries based on your dimension selections
                        </div>
                      </>
                    ) : (
                      <div className="h-[450px] border border-dashed border-gray-700 rounded-lg flex items-center justify-center text-muted-foreground">
                        Select dimension values to preview timeseries
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Tag Timeseries */}
            {currentStep === 4 && (
              <div className="space-y-3">
                <div>
                  <h2 className="text-xl font-semibold text-foreground mb-1">Tag Anomalous Intervals</h2>
                  <p className="text-sm text-muted-foreground">
                    Click and drag on the chart to select time intervals that appear anomalous
                  </p>
                </div>

                <div className="p-2 bg-gray-800 rounded-lg border border-gray-700 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-muted-foreground" />
                      <Label className="text-xs font-medium text-foreground">Time Window</Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleZoomOut}
                        disabled={zoomLevel <= 1}
                        className="border-gray-600 bg-gray-900"
                      >
                        <ZoomOut className="w-4 h-4" />
                      </Button>
                      <span className="text-sm text-muted-foreground min-w-[60px] text-center">{zoomLevel}x zoom</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleZoomIn}
                        disabled={zoomLevel >= 16}
                        className="border-gray-600 bg-gray-900"
                      >
                        <ZoomIn className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(["1h", "6h", "24h", "7d", "30d"] as const).map((window) => (
                      <Button
                        key={window}
                        variant={timeWindow === window ? "default" : "outline"}
                        size="sm"
                        onClick={() => setTimeWindow(window)}
                        className={
                          timeWindow === window ? "bg-blue-600 hover:bg-blue-700" : "border-gray-600 bg-gray-900"
                        }
                      >
                        {window.toUpperCase()}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <div
                    ref={chartContainerRef}
                    className="h-[400px] border border-gray-700 rounded-lg bg-gray-900 p-2 cursor-crosshair overflow-hidden"
                    onMouseDown={handleChartMouseDown}
                    onMouseMove={handleChartMouseMove}
                    onMouseUp={handleChartMouseUp}
                    onMouseLeave={handleChartMouseUp}
                  >
                    <ChartContainer
                      config={Object.keys(timeseriesData).reduce(
                        (acc, seriesKey, index) => ({
                          ...acc,
                          [seriesKey]: {
                            label: seriesKey,
                            color: metricColors[index % metricColors.length],
                          },
                        }),
                        {},
                      )}
                      className="h-full w-full"
                    >
                      <LineChart data={formatChartData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />

                        {/* Show tagged intervals */}
                        {taggedIntervals.map((interval, idx) => (
                          <ReferenceArea
                            key={idx}
                            x1={interval.start}
                            x2={interval.end}
                            stroke="hsl(0, 84%, 60%)"
                            strokeOpacity={0.8}
                            fill="hsl(0, 84%, 60%)"
                            fillOpacity={0.2}
                            strokeWidth={2}
                          />
                        ))}

                        {/* Show current drag selection */}
                        {isDragging && dragStart && dragEnd && (
                          <ReferenceArea
                            x1={dragStart}
                            x2={dragEnd}
                            stroke="hsl(45, 93%, 47%)"
                            strokeOpacity={0.8}
                            fill="hsl(45, 93%, 47%)"
                            fillOpacity={0.2}
                            strokeWidth={2}
                          />
                        )}

                        <XAxis
                          dataKey="timestamp"
                          type="number"
                          domain={["dataMin", "dataMax"]}
                          tickFormatter={(value) =>
                            new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                          }
                          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                          stroke="hsl(var(--border))"
                        />
                        <YAxis
                          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                          stroke="hsl(var(--border))"
                        />
                        <Legend
                          wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }}
                          iconType="line"
                          formatter={(value) => <span style={{ color: "hsl(var(--foreground))" }}>{value}</span>}
                        />
                        {Object.keys(timeseriesData).map((seriesKey, index) => (
                          <Line
                            key={seriesKey}
                            type="monotone"
                            dataKey={seriesKey}
                            stroke={metricColors[index % metricColors.length]}
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                          />
                        ))}
                      </LineChart>
                    </ChartContainer>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-red-500/20 border-2 border-red-500 rounded"></div>
                      <span>Tagged Anomalous Interval</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-yellow-500/20 border-2 border-yellow-500 rounded"></div>
                      <span>Current Selection</span>
                    </div>
                  </div>

                  {taggedIntervals.length > 0 && (
                    <div className="space-y-1.5">
                      <Label className="text-xs font-medium text-foreground">
                        Tagged Intervals ({taggedIntervals.length})
                      </Label>
                      <div className="space-y-1.5">
                        {taggedIntervals.map((interval, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-1.5 bg-gray-800 rounded border border-gray-700"
                          >
                            <div className="text-xs font-mono text-foreground">
                              {new Date(interval.start).toLocaleString()} →{" "}
                              {new Date(interval.end).toLocaleTimeString()}
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setTaggedIntervals(taggedIntervals.filter((_, i) => i !== index))}
                            >
                              <Trash2 className="w-4 h-4 text-red-400" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Step 5: Configure Details */}
            {currentStep === 5 && (
              <div className="space-y-3">
                <div>
                  <h2 className="text-xl font-semibold text-foreground mb-1">Configure Symptom Details</h2>
                  <p className="text-sm text-muted-foreground">
                    Set the concern score, confidence score, and add any custom fields
                  </p>
                </div>

                <div className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {/* Concern Score */}
                    <Card className="bg-gray-800 border-gray-700">
                      <CardHeader className="pb-2 px-3">
                        <CardTitle className="text-base text-foreground">Concern Score</CardTitle>
                        <CardDescription className="text-muted-foreground text-sm">
                          How concerning is this symptom? (0-100%)
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-2 px-3 pb-3">
                        <div className="flex items-center gap-4">
                          <Slider
                            value={[concernScore]}
                            onValueChange={(value) => setConcernScore(value[0])}
                            max={1}
                            min={0}
                            step={0.01}
                            className="flex-1"
                          />
                          <div className="w-20 text-right">
                            <Badge
                              className={`${
                                concernScore >= 0.8
                                  ? "bg-red-600"
                                  : concernScore >= 0.6
                                    ? "bg-yellow-600"
                                    : "bg-green-600"
                              }`}
                            >
                              {(concernScore * 100).toFixed(0)}%
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-gray-800 border-gray-700">
                      <CardHeader className="pb-2 px-3">
                        <CardTitle className="text-base text-foreground">Confidence Score</CardTitle>
                        <CardDescription className="text-muted-foreground text-sm">
                          How confident are you in this symptom? (0-100%)
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-2 px-3 pb-3">
                        <div className="flex items-center gap-4">
                          <Slider
                            value={[confidenceScore]}
                            onValueChange={(value) => setConfidenceScore(value[0])}
                            max={1}
                            min={0}
                            step={0.01}
                            className="flex-1"
                          />
                          <div className="w-20 text-right">
                            <Badge className="bg-blue-600">{(confidenceScore * 100).toFixed(0)}%</Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Custom Fields */}
                  <Card className="bg-gray-800 border-gray-700">
                    <CardHeader className="px-3 pb-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-base text-foreground">Custom Fields</CardTitle>
                          <CardDescription className="text-muted-foreground text-sm mt-1">
                            Add custom metadata fields to this symptom
                          </CardDescription>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={addCustomField}
                          className="border-gray-600 bg-gray-900"
                        >
                          <Plus className="w-4 h-4" />
                          Add Field
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3 px-3 pb-3">
                      {customFields.length === 0 && (
                        <div className="text-center py-8 text-muted-foreground border border-dashed border-gray-600 rounded-lg bg-gray-900/50">
                          No custom fields added. Click "Add Field" to create one.
                        </div>
                      )}

                      {customFields.map((field) => (
                        <Card key={field.id} className="bg-gray-900 border-gray-600">
                          <CardContent className="p-3 space-y-2">
                            <div className="flex items-start gap-2">
                              <div className="flex-1 space-y-2">
                                <div className="grid grid-cols-2 gap-2">
                                  <div>
                                    <Label className="text-xs text-muted-foreground mb-1 block">Field Name</Label>
                                    <Input
                                      placeholder="e.g., severity_level"
                                      value={field.name}
                                      onChange={(e) => updateCustomField(field.id, { name: e.target.value })}
                                      className="bg-gray-800 border-gray-600 text-foreground"
                                    />
                                  </div>
                                  <div>
                                    <Label className="text-xs text-muted-foreground mb-1 block">Field Type</Label>
                                    <Select
                                      value={field.type}
                                      onValueChange={(value: "string" | "integer" | "float" | "enum") =>
                                        updateCustomField(field.id, { type: value, value: "" })
                                      }
                                    >
                                      <SelectTrigger className="bg-gray-800 border-gray-600 text-foreground">
                                        <SelectValue />
                                      </SelectTrigger>
                                      <SelectContent>
                                        <SelectItem value="string">String</SelectItem>
                                        <SelectItem value="integer">Integer</SelectItem>
                                        <SelectItem value="float">Float</SelectItem>
                                        <SelectItem value="enum">Enum</SelectItem>
                                      </SelectContent>
                                    </Select>
                                  </div>
                                </div>

                                {field.type === "string" && (
                                  <div>
                                    <Label className="text-xs text-muted-foreground mb-1 block">Value</Label>
                                    <Input
                                      placeholder="Enter string value"
                                      value={field.value as string}
                                      onChange={(e) => updateCustomField(field.id, { value: e.target.value })}
                                      className="bg-gray-800 border-gray-600 text-foreground"
                                    />
                                  </div>
                                )}

                                {field.type === "integer" && (
                                  <div>
                                    <Label className="text-xs text-muted-foreground mb-1 block">Value</Label>
                                    <Input
                                      type="number"
                                      placeholder="Enter integer value"
                                      value={field.value as number}
                                      onChange={(e) =>
                                        updateCustomField(field.id, { value: Number.parseInt(e.target.value) || 0 })
                                      }
                                      className="bg-gray-800 border-gray-600 text-foreground"
                                    />
                                  </div>
                                )}

                                {field.type === "float" && (
                                  <div>
                                    <Label className="text-xs text-muted-foreground mb-1 block">Value</Label>
                                    <Input
                                      type="number"
                                      step="0.01"
                                      placeholder="Enter float value"
                                      value={field.value as number}
                                      onChange={(e) =>
                                        updateCustomField(field.id, { value: Number.parseFloat(e.target.value) || 0 })
                                      }
                                      className="bg-gray-800 border-gray-600 text-foreground"
                                    />
                                  </div>
                                )}

                                {field.type === "enum" && (
                                  <div className="space-y-1.5">
                                    <div className="flex items-center justify-between">
                                      <Label className="text-xs text-muted-foreground">Enum Options</Label>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => addEnumOption(field.id)}
                                        className="h-6 text-xs border-gray-600 bg-gray-900"
                                      >
                                        <Plus className="w-3 h-3 mr-1" />
                                        Add Option
                                      </Button>
                                    </div>
                                    {field.enumOptions?.map((option, index) => (
                                      <div key={index} className="flex items-center gap-1.5">
                                        <Input
                                          placeholder={`Option ${index + 1}`}
                                          value={option}
                                          onChange={(e) => updateEnumOption(field.id, index, e.target.value)}
                                          className="bg-gray-800 border-gray-600 text-foreground text-sm"
                                        />
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          onClick={() => removeEnumOption(field.id, index)}
                                          className="h-8 w-8 p-0"
                                        >
                                          <X className="w-4 h-4 text-red-400" />
                                        </Button>
                                      </div>
                                    ))}
                                    {field.enumOptions && field.enumOptions.length > 0 && (
                                      <div>
                                        <Label className="text-xs text-muted-foreground mb-1 block">
                                          Selected Value
                                        </Label>
                                        <Select
                                          value={field.value as string}
                                          onValueChange={(value) => updateCustomField(field.id, { value })}
                                        >
                                          <SelectTrigger className="bg-gray-800 border-gray-600 text-foreground">
                                            <SelectValue placeholder="Select an option" />
                                          </SelectTrigger>
                                          <SelectContent>
                                            {field.enumOptions
                                              .filter((option) => option.trim() !== "")
                                              .map((option, index) => (
                                                <SelectItem key={index} value={option}>
                                                  {option}
                                                </SelectItem>
                                              ))}
                                          </SelectContent>
                                        </Select>
                                      </div>
                                    )}
                                  </div>
                                )}
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeCustomField(field.id)}
                                className="h-8 w-8 p-0"
                              >
                                <Trash2 className="w-4 h-4 text-red-400" />
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </CardContent>
                  </Card>

                  {/* Summary */}
                  <Card className="bg-gray-800 border-gray-700">
                    <CardHeader className="px-3 pb-2">
                      <CardTitle className="text-base text-foreground">Symptom Summary</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 px-3 pb-3">
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                        <div>
                          <div className="text-muted-foreground">Monitored Entity</div>
                          <div className="font-medium text-foreground">
                            {selectedService?.name || selectedService?.id}
                          </div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Metric</div>
                          <div className="font-medium font-mono text-foreground">{selectedMetric}</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Timeseries Count</div>
                          <div className="font-medium text-foreground">{Object.keys(timeseriesData).length}</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Tagged Intervals</div>
                          <div className="font-medium text-foreground">{taggedIntervals.length}</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Concern Score</div>
                          <div className="font-medium text-foreground">{(concernScore * 100).toFixed(0)}%</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Confidence Score</div>
                          <div className="font-medium text-foreground">{(confidenceScore * 100).toFixed(0)}%</div>
                        </div>
                        <div>
                          <div className="text-muted-foreground">Custom Fields</div>
                          <div className="font-medium text-foreground">{customFields.length}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* JSON Preview Modal */}
        <Dialog open={showJsonModal} onOpenChange={setShowJsonModal}>
          <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto bg-gray-900 border-gray-700">
            <DialogHeader>
              <DialogTitle className="text-xl text-foreground">Review Anomaly JSON</DialogTitle>
              <DialogDescription className="text-muted-foreground">
                Review the JSON representation of the anomaly before submitting
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="bg-gray-950 border border-gray-700 rounded-lg p-4 overflow-x-auto">
                <pre className="text-sm text-foreground font-mono whitespace-pre-wrap">{anomalyJson}</pre>
              </div>
            </div>

            <DialogFooter className="flex items-center justify-between">
              <Button variant="outline" onClick={copyJsonToClipboard} className="border-gray-600 bg-gray-800">
                Copy JSON
              </Button>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowJsonModal(false)}
                  className="border-gray-600 bg-gray-800"
                >
                  Cancel
                </Button>
                <Button onClick={handleFinalSubmit} disabled={loading} className="bg-green-600 hover:bg-green-700">
                  {loading ? "Creating..." : "Submit Symptom"}
                  <Check className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between mt-3">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Previous
          </Button>

          {currentStep < 5 ? (
            <Button
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!canProceed()}
              className="gap-2 bg-blue-600 hover:bg-blue-700"
            >
              Next
              <ArrowRight className="w-4 h-4" />
            </Button>
          ) : (
            <Button onClick={handleCreateSymptom} disabled={loading} className="gap-2 bg-green-600 hover:bg-green-700">
              Create Symptom
              <Check className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
