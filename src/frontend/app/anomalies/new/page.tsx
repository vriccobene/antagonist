"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, CalendarIcon, Search, Check } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { API_BASE_URL, ENDPOINTS } from "@/app/api"
import { localDateToUTC } from "@/lib/timezone-utils"
import { cn } from "@/lib/utils"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface Service {
  id: string
  type?: string
  [key: string]: any  // Allow additional fields
}

export default function NewAnomalyPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [services, setServices] = useState<Service[]>([])
  const [loadingServices, setLoadingServices] = useState(true)
  const [serviceSearchQuery, setServiceSearchQuery] = useState("")
  const [selectedServiceType, setSelectedServiceType] = useState<string>("all")
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  // Form fields
  const [uri, setUri] = useState("")
  const [description, setDescription] = useState("")
  const [startDate, setStartDate] = useState<Date>()
  const [startTime, setStartTime] = useState("")
  const [endDate, setEndDate] = useState<Date>()
  const [endTime, setEndTime] = useState("")
  const [state, setState] = useState<string>("unknown")
  const [selectedServiceId, setSelectedServiceId] = useState<string>("")
  const [publisherName, setPublisherName] = useState("")
  const [publisherVersion, setPublisherVersion] = useState("")

  // Validation errors
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch services on mount
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.SERVICE}`)
        if (response.ok) {
          const data = await response.json()
          console.log("Fetched services:", data)
          console.log("Sample service:", data[0])
          setServices(data)
        }
      } catch (err) {
        console.error("Error fetching services:", err)
      } finally {
        setLoadingServices(false)
      }
    }

    fetchServices()
  }, [])

  // Get all unique service types
  const getServiceTypes = () => {
    const types = new Set<string>()
    services.forEach((service) => {
      if (service.type) {
        types.add(service.type)
      }
    })
    return Array.from(types).sort()
  }

  // Filter services by type
  const getFilteredServicesByType = () => {
    if (selectedServiceType === "all") {
      return services
    }
    return services.filter((service) => service.type === selectedServiceType)
  }

  // Get all unique extra field keys from filtered services (excluding id and type)
  // Only include fields where at least one service has a non-null value
  const getExtraFieldKeys = () => {
    const filteredServices = getFilteredServicesByType()
    const fieldCounts = new Map<string, number>()
    
    filteredServices.forEach((service) => {
      Object.keys(service).forEach((key) => {
        if (key !== 'id' && key !== 'type') {
          // Count how many services have this field with a non-null value
          if (service[key] !== null && service[key] !== undefined) {
            fieldCounts.set(key, (fieldCounts.get(key) || 0) + 1)
          }
        }
      })
    })
    
    // Only include fields that exist in at least one service
    const result = Array.from(fieldCounts.keys()).sort()
    console.log("Extra field keys found:", result)
    console.log("Field counts:", Object.fromEntries(fieldCounts))
    return result
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!description.trim()) {
      newErrors.description = "Description is required"
    }

    if (!startDate) {
      newErrors.startDate = "Start date is required"
    }

    if (!startTime) {
      newErrors.startTime = "Start time is required"
    }

    if (endDate && !endTime) {
      newErrors.endTime = "End time is required when end date is set"
    }

    if (!publisherName.trim()) {
      newErrors.publisherName = "Publisher name is required"
    }

    if (!selectedServiceId) {
      newErrors.service = "Service selection is required"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      // Combine date and time for start_time
      const startDateTime = new Date(startDate!)
      const [startHours, startMinutes] = startTime.split(":")
      startDateTime.setHours(Number.parseInt(startHours), Number.parseInt(startMinutes), 0, 0)

      // Combine date and time for end_time if provided
      let endDateTime: Date | undefined
      if (endDate && endTime) {
        endDateTime = new Date(endDate)
        const [endHours, endMinutes] = endTime.split(":")
        endDateTime.setHours(Number.parseInt(endHours), Number.parseInt(endMinutes), 0, 0)
      }

      const payload = {
        revision: 1,
        uri: uri.trim() || undefined,
        description: description.trim(),
        start_time: localDateToUTC(startDateTime),
        end_time: endDateTime ? localDateToUTC(endDateTime) : undefined,
        state: state,
        confidence_score: 0.5,
        concern_score: 0.5,
        publisher: {
          name: publisherName.trim(),
          version: publisherVersion.trim() || undefined,
        },
        service: {
          id: selectedServiceId,
        },
        anomaly: [],
      }

      console.log("Submitting anomaly:", payload)

      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.RELEVANT_STATE}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || "Failed to create anomaly")
      }

      const responseData = await response.json()
      console.log("Anomaly created successfully", responseData)

      // Navigate to the newly created anomaly detail page
      // Backend returns the UUID directly as a string, not an object with id property
      if (responseData) {
        router.push(`/anomalies/${responseData}`)
      } else {
        router.push("/anomalies")
      }
    } catch (err) {
      console.error("Error creating anomaly:", err)
      setError(err instanceof Error ? err.message : "An error occurred while creating the anomaly")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <Link href="/anomalies">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Anomalies
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">Create New Anomaly</h1>
          <p className="text-muted-foreground mt-2">Define a new anomaly detection event</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400">
            <p className="font-medium">Error creating anomaly</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>Provide the core details for this anomaly</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  placeholder="Describe the anomaly..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className={errors.description ? "border-red-500" : ""}
                  rows={4}
                />
                {errors.description && <p className="text-sm text-red-500">{errors.description}</p>}
                <p className="text-sm text-muted-foreground">A detailed description of the anomaly</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="uri">URI</Label>
                <Input
                  id="uri"
                  placeholder="https://api.example.com/services/..."
                  value={uri}
                  onChange={(e) => setUri(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">Optional URI reference for this anomaly</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="state">State *</Label>
                <Select value={state} onValueChange={setState}>
                  <SelectTrigger id="state">
                    <SelectValue placeholder="Select state" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="unknown">Unknown</SelectItem>
                    <SelectItem value="potential">Potential</SelectItem>
                    <SelectItem value="forecasted">Forecasted</SelectItem>
                    <SelectItem value="confirmed">Confirmed</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">Current state of the anomaly</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Time Range</CardTitle>
              <CardDescription>Specify when the anomaly occurred</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Start Time *</Label>
                <div className="flex gap-2">
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "flex-1 justify-start text-left font-normal",
                          !startDate && "text-muted-foreground",
                          errors.startDate && "border-red-500",
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {startDate ? startDate.toLocaleDateString() : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar mode="single" selected={startDate} onSelect={setStartDate} initialFocus />
                    </PopoverContent>
                  </Popover>
                  <Input
                    type="time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className={cn("w-40", errors.startTime && "border-red-500")}
                  />
                </div>
                {(errors.startDate || errors.startTime) && (
                  <p className="text-sm text-red-500">{errors.startDate || errors.startTime}</p>
                )}
                <p className="text-sm text-muted-foreground">When the anomaly started</p>
              </div>

              <div className="space-y-2">
                <Label>End Time</Label>
                <div className="flex gap-2">
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "flex-1 justify-start text-left font-normal",
                          !endDate && "text-muted-foreground",
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {endDate ? endDate.toLocaleDateString() : "Pick a date (optional)"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar mode="single" selected={endDate} onSelect={setEndDate} initialFocus />
                    </PopoverContent>
                  </Popover>
                  <Input
                    type="time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className={cn("w-40", errors.endTime && "border-red-500")}
                  />
                </div>
                {errors.endTime && <p className="text-sm text-red-500">{errors.endTime}</p>}
                <p className="text-sm text-muted-foreground">When the anomaly ended (leave empty if ongoing)</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Service Selection</CardTitle>
              <CardDescription>Select the service affected by this anomaly</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!loadingServices && getExtraFieldKeys().length === 0 && selectedServiceType === "all" && (
                <div className="mb-4 p-3 bg-yellow-900/20 border border-yellow-800/50 rounded-lg text-yellow-400 text-sm">
                  <p className="font-medium">ℹ️ No additional service fields found</p>
                  <p className="text-xs mt-1 text-yellow-300/80">
                    Services in the database only have ID and Type. To add custom fields, create services with additional properties via the API.
                  </p>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="serviceType">Filter by Type</Label>
                  <Select 
                    value={selectedServiceType} 
                    onValueChange={(value: string) => {
                      setSelectedServiceType(value)
                      setCurrentPage(1) // Reset to first page on type change
                    }}
                    disabled={loadingServices}
                  >
                    <SelectTrigger id="serviceType">
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      {getServiceTypes().map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="serviceSearch">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="serviceSearch"
                      placeholder="Search services..."
                      value={serviceSearchQuery}
                      onChange={(e) => {
                        setServiceSearchQuery(e.target.value)
                        setCurrentPage(1) // Reset to first page on search
                      }}
                      className="pl-10"
                    />
                  </div>
                </div>
              </div>
              
              {errors.service && <p className="text-sm text-red-500">{errors.service}</p>}
              
              {!loadingServices && (
                <div className="text-sm text-muted-foreground">
                  {selectedServiceType !== "all" && (
                    <span>
                      Showing <span className="font-medium text-foreground">{getFilteredServicesByType().length}</span> {getFilteredServicesByType().length === 1 ? 'service' : 'services'} of type "{selectedServiceType}"
                    </span>
                  )}
                  {selectedServiceType === "all" && (
                    <span>
                      Total: <span className="font-medium text-foreground">{services.length}</span> {services.length === 1 ? 'service' : 'services'}
                    </span>
                  )}
                </div>
              )}

              {loadingServices ? (
                <div className="text-center py-8 text-muted-foreground">Loading services...</div>
              ) : (
                <>
                  <div className="border rounded-lg overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-12"></TableHead>
                          <TableHead>ID</TableHead>
                          <TableHead>Type</TableHead>
                          {getExtraFieldKeys().map((key: string) => (
                            <TableHead key={key} className="capitalize">
                              {key.replace(/_/g, " ")}
                            </TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {(() => {
                          // First filter by type
                          const typeFilteredServices = getFilteredServicesByType()
                          
                          // Then filter based on search query
                          const filteredServices = typeFilteredServices.filter((service) => {
                            if (!serviceSearchQuery) return true
                            
                            const searchLower = serviceSearchQuery.toLowerCase()
                            // Search in id, type, and all extra fields
                            const matchesId = service.id.toLowerCase().includes(searchLower)
                            const matchesType = service.type?.toLowerCase().includes(searchLower)
                            const matchesExtra = Object.entries(service).some(([key, value]) => {
                              if (key === 'id' || key === 'type') return false
                              return String(value).toLowerCase().includes(searchLower)
                            })
                            return matchesId || matchesType || matchesExtra
                          })

                          // Calculate pagination
                          const startIndex = (currentPage - 1) * itemsPerPage
                          const endIndex = startIndex + itemsPerPage
                          const paginatedServices = filteredServices.slice(startIndex, endIndex)
                          const totalPages = Math.ceil(filteredServices.length / itemsPerPage)
                          const extraFieldKeys = getExtraFieldKeys()

                          if (paginatedServices.length === 0) {
                            return (
                              <TableRow>
                                <TableCell colSpan={3 + extraFieldKeys.length} className="text-center py-8 text-muted-foreground">
                                  {serviceSearchQuery ? "No services found matching your search." : "No services available."}
                                </TableCell>
                              </TableRow>
                            )
                          }

                          return (
                            <>
                              {paginatedServices.map((service) => (
                                <TableRow
                                  key={service.id}
                                  className={cn(
                                    "cursor-pointer hover:bg-muted/50",
                                    selectedServiceId === service.id && "bg-muted",
                                  )}
                                  onClick={() => setSelectedServiceId(service.id)}
                                >
                                  <TableCell>
                                    {selectedServiceId === service.id && <Check className="h-4 w-4 text-blue-500" />}
                                  </TableCell>
                                  <TableCell className="font-mono text-xs text-muted-foreground max-w-xs">
                                    {service.id}
                                  </TableCell>
                                  <TableCell className="font-medium">{service.type || "-"}</TableCell>
                                  {extraFieldKeys.map((key: string) => (
                                    <TableCell key={key} className="text-muted-foreground">
                                      {service[key] !== undefined ? String(service[key]) : "-"}
                                    </TableCell>
                                  ))}
                                </TableRow>
                              ))}
                            </>
                          )
                        })()}
                      </TableBody>
                    </Table>
                  </div>

                  {/* Pagination Controls */}
                  {(() => {
                    // First filter by type
                    const typeFilteredServices = getFilteredServicesByType()
                    
                    // Then filter based on search query
                    const filteredServices = typeFilteredServices.filter((service) => {
                      if (!serviceSearchQuery) return true
                      
                      const searchLower = serviceSearchQuery.toLowerCase()
                      // Search in id, type, and all extra fields
                      const matchesId = service.id.toLowerCase().includes(searchLower)
                      const matchesType = service.type?.toLowerCase().includes(searchLower)
                      const matchesExtra = Object.entries(service).some(([key, value]) => {
                        if (key === 'id' || key === 'type') return false
                        return String(value).toLowerCase().includes(searchLower)
                      })
                      return matchesId || matchesType || matchesExtra
                    })
                    const totalPages = Math.ceil(filteredServices.length / itemsPerPage)

                    if (totalPages <= 1) return null

                    return (
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">
                          Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredServices.length)} of {filteredServices.length} services
                        </p>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                            disabled={currentPage === 1}
                          >
                            Previous
                          </Button>
                          <div className="flex items-center gap-1">
                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                              let pageNum: number
                              if (totalPages <= 5) {
                                pageNum = i + 1
                              } else if (currentPage <= 3) {
                                pageNum = i + 1
                              } else if (currentPage >= totalPages - 2) {
                                pageNum = totalPages - 4 + i
                              } else {
                                pageNum = currentPage - 2 + i
                              }

                              return (
                                <Button
                                  key={pageNum}
                                  variant={currentPage === pageNum ? "default" : "outline"}
                                  size="sm"
                                  onClick={() => setCurrentPage(pageNum)}
                                  className="w-10"
                                >
                                  {pageNum}
                                </Button>
                              )
                            })}
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                            disabled={currentPage === totalPages}
                          >
                            Next
                          </Button>
                        </div>
                      </div>
                    )
                  })()}
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Publisher</CardTitle>
              <CardDescription>Information about who detected this anomaly</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="publisherName">Publisher Name *</Label>
                  <Input
                    id="publisherName"
                    value={publisherName}
                    onChange={(e) => setPublisherName(e.target.value)}
                    className={errors.publisherName ? "border-red-500" : ""}
                  />
                  {errors.publisherName && <p className="text-sm text-red-500">{errors.publisherName}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="publisherVersion">Version</Label>
                  <Input
                    id="publisherVersion"
                    value={publisherVersion}
                    onChange={(e) => setPublisherVersion(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-4 justify-end">
            <Link href="/anomalies">
              <Button type="button" variant="outline" disabled={isSubmitting}>
                Cancel
              </Button>
            </Link>
            <Button type="submit" disabled={isSubmitting} className="bg-blue-600 hover:bg-blue-700">
              {isSubmitting ? "Creating..." : "Create Anomaly"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
