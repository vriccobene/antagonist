"use client"
import { useState, useEffect } from "react"
import type React from "react"

import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { API_BASE_URL, ENDPOINTS } from "@/app/api"
import { useRouter } from "next/navigation"
import Link from "next/link"

enum DatabaseType {
  INFLUXDB = "influxdb",
}

interface DataSourceType {
  database: DatabaseType
  version: string
}

interface Endpoint {
  url: string
  metadata?: Record<string, any>
}

interface DataSource {
  id?: string
  name: string
  description?: string
  type: DataSourceType
  end_point: Endpoint
}

export default function NewMonitoredEntityPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Form state
  const [typeMode, setTypeMode] = useState<"existing" | "new">("existing")
  const [existingTypes, setExistingTypes] = useState<string[]>([])
  const [selectedExistingType, setSelectedExistingType] = useState("")
  const [customTypeName, setCustomTypeName] = useState("")
  const [description, setDescription] = useState("")
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [selectedDataSourceId, setSelectedDataSourceId] = useState("")

  // Loading states
  const [loadingTypes, setLoadingTypes] = useState(true)
  const [loadingDataSources, setLoadingDataSources] = useState(true)

  // Fetch existing monitored entity types
  useEffect(() => {
    const fetchExistingTypes = async () => {
      try {
        setLoadingTypes(true)
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.EXISTING_MONITORED_ENTITY_TYPES}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          throw new Error("Failed to fetch existing types")
        }

        const data = await response.json()
        setExistingTypes(data)
        if (data.length > 0) {
          setSelectedExistingType(data[0])
        }
      } catch (err) {
        console.error("Failed to fetch existing types:", err)
        setExistingTypes([])
      } finally {
        setLoadingTypes(false)
      }
    }

    fetchExistingTypes()
  }, [])

  // Fetch existing data sources
  useEffect(() => {
    const fetchDataSources = async () => {
      try {
        setLoadingDataSources(true)
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.DATA_SOURCE}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          throw new Error("Failed to fetch data sources")
        }

        const data = await response.json()
        setDataSources(data)
        if (data.length > 0) {
          setSelectedDataSourceId(data[0].id)
        }
      } catch (err) {
        console.error("Failed to fetch data sources:", err)
        setDataSources([])
      } finally {
        setLoadingDataSources(false)
      }
    }

    fetchDataSources()
  }, [])

  const validateForm = () => {
    const errors: string[] = []

    // Validate type name
    if (typeMode === "existing" && !selectedExistingType) {
      errors.push("Please select an existing entity type")
    }
    if (typeMode === "new" && !customTypeName.trim()) {
      errors.push("Please enter a custom entity type name")
    }

    if (errors.length > 0) {
      setError(errors.join(", "))
      return false
    }

    setError(null)
    return true
  }

  // Adjust the payload structure to use `data_source_id` instead of `data_source`
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const entityName = typeMode === "existing" ? selectedExistingType : customTypeName

      // Adjust the payload to use `data_source_id`
      const payload = {
        name: entityName,
        description: description || undefined,
        data_source_id: selectedDataSourceId || undefined,
      }

      console.log("Submitting monitored entity:", payload)

      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.MONITORED_ENTITY}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        setError(errorData.detail?.error || "Failed to create monitored entity")
        return
      }

      const successData = await response.json()
      setSuccessMessage(successData.message || "Monitored entity type created successfully!")
      setTimeout(() => {
        router.push("/monitored-entity-types")
      }, 1500)
    } catch (err) {
      console.error("Error creating monitored entity:", err)
      setError(err instanceof Error ? err.message : "An error occurred while creating the monitored entity")
    } finally {
      setIsSubmitting(false)
    }
  }

  const isLoading = loadingTypes || loadingDataSources

  if (isLoading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading form data...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      <div className="mb-6">
        <Link href="/monitored-entity-types" className="inline-flex items-center text-blue-400 hover:text-blue-300 mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Monitored Entity Types
        </Link>
        <h1 className="text-3xl font-bold">Create New Entity Type</h1>
        <p className="text-muted-foreground mt-2">
          Add a new monitored entity type by selecting from existing types or creating a custom one
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400">
          <strong>Error:</strong> {error}
        </div>
      )}

      {successMessage && (
        <div className="mb-6 p-4 bg-green-900/20 border border-green-800 rounded-lg text-green-400">
          <strong>Success:</strong> {successMessage}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Entity Type Information</CardTitle>
            <CardDescription>Configure the monitored entity type details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Type Selection Mode */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Entity Type Selection</Label>
              <div className="grid grid-cols-2 gap-4">
                <label
                  htmlFor="radio-existing"
                  className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                    typeMode === "existing"
                      ? "border-blue-500 bg-blue-500/10"
                      : "border-border bg-muted/50 hover:border-muted-foreground"
                  }`}
                >
                  <input
                    type="radio"
                    id="radio-existing"
                    name="typeMode"
                    value="existing"
                    checked={typeMode === "existing"}
                    onChange={() => setTypeMode("existing")}
                    className="w-4 h-4 text-blue-600 bg-card border-border focus:ring-blue-500"
                  />
                  <span className="flex-1 font-medium">Select from existing entity types</span>
                </label>
                <label
                  htmlFor="radio-new"
                  className={`flex items-center space-x-3 p-4 rounded-lg border-2 transition-all cursor-pointer ${
                    typeMode === "new"
                      ? "border-blue-500 bg-blue-500/10"
                      : "border-border bg-muted/50 hover:border-muted-foreground"
                  }`}
                >
                  <input
                    type="radio"
                    id="radio-new"
                    name="typeMode"
                    value="new"
                    checked={typeMode === "new"}
                    onChange={() => setTypeMode("new")}
                    className="w-4 h-4 text-blue-600 bg-card border-border focus:ring-blue-500"
                  />
                  <span className="flex-1 font-medium">Create a new custom entity type</span>
                </label>
              </div>
            </div>

            {/* Existing Type Selection */}
            {typeMode === "existing" && (
              <div className="space-y-2">
                <Label htmlFor="existingType">
                  Select Entity Type <span className="text-red-500">*</span>
                </Label>
                <select
                  id="existingType"
                  value={selectedExistingType}
                  onChange={(e) => setSelectedExistingType(e.target.value)}
                  className="w-full px-3 py-2 bg-card border border-border rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required={typeMode === "existing"}
                >
                  {existingTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
                <p className="text-sm text-muted-foreground">
                  Choose from entity types already defined in your services
                </p>
              </div>
            )}

            {/* Custom Type Name */}
            {typeMode === "new" && (
              <div className="space-y-2">
                <Label htmlFor="customTypeName">
                  Custom Entity Type Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="customTypeName"
                  placeholder="e.g., Load Balancer, Storage Service"
                  value={customTypeName}
                  onChange={(e) => setCustomTypeName(e.target.value)}
                  className="bg-card border-border"
                  required={typeMode === "new"}
                />
                <p className="text-sm text-muted-foreground">Enter a unique name for your custom entity type</p>
              </div>
            )}

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                placeholder="Describe the purpose and characteristics of this entity type..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="bg-card border-border min-h-[100px]"
              />
              <p className="text-sm text-muted-foreground">Provide additional context about this entity type</p>
            </div>

            {/* Data Source Selection */}
            <div className="space-y-2">
              <Label htmlFor="dataSource">Data Source (Optional)</Label>
              <select
                id="dataSource"
                value={selectedDataSourceId}
                onChange={(e) => setSelectedDataSourceId(e.target.value)}
                className="w-full px-3 py-2 bg-card border border-border rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">No data source</option>
                {dataSources.map((ds) => (
                  <option key={ds.id} value={ds.id}>
                    {ds.name} - {ds.type.database} v{ds.type.version}
                  </option>
                ))}
              </select>
              <p className="text-sm text-muted-foreground">
                Select a data source to associate with this entity type. You can add data sources in the{" "}
                <Link href="/data-sources" className="text-blue-400 hover:text-blue-300">
                  Data Sources
                </Link>{" "}
                page.
              </p>
            </div>

            {/* Form Actions */}
            <div className="flex gap-3 pt-4 border-t border-border">
              <Button type="submit" disabled={isSubmitting} className="bg-blue-600 hover:bg-blue-700 text-white">
                {isSubmitting ? "Creating..." : "Create Entity Type"}
              </Button>
              <Link href="/monitored-entity-types">
                <Button type="button" variant="outline" disabled={isSubmitting} className="border-border bg-card">
                  Cancel
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
