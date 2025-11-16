"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Edit2, Save, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ENDPOINTS, API_BASE_URL } from "@/app/api"
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

interface MonitoredEntity {
  id?: string
  name: string
  description?: string
  data_source_id?: string
  data_source?: DataSource
}

export default function MonitoredEntityDetailPage() {
  const params = useParams()
  const router = useRouter()
  const entityName = decodeURIComponent(params.id as string)

  const [entity, setEntity] = useState<MonitoredEntity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Edit form state
  const [typeMode, setTypeMode] = useState<"existing" | "new">("existing")
  const [existingTypes, setExistingTypes] = useState<string[]>([])
  const [selectedExistingType, setSelectedExistingType] = useState("")
  const [customTypeName, setCustomTypeName] = useState("")
  const [editDescription, setEditDescription] = useState("")
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [selectedDataSourceId, setSelectedDataSourceId] = useState("")

  // Loading states
  const [loadingTypes, setLoadingTypes] = useState(false)
  const [loadingDataSources, setLoadingDataSources] = useState(false)

  // Fetch entity details
  useEffect(() => {
    const fetchEntity = async () => {
      try {
        setLoading(true)
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.MONITORED_ENTITY}/${encodeURIComponent(entityName)}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          throw new Error("Failed to fetch monitored entity")
        }

        const data = await response.json()
        setEntity(data)
        initializeEditForm(data)
      } catch (err) {
        console.error("Error fetching monitored entity:", err)
        setError(err instanceof Error ? err.message : "An error occurred")
      } finally {
        setLoading(false)
      }
    }

    fetchEntity()
  }, [entityName])

  // Fetch existing types when entering edit mode
  useEffect(() => {
    if (isEditMode) {
      fetchExistingTypes()
      fetchDataSources()
    }
  }, [isEditMode])

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
    } catch (err) {
      console.error("Error fetching existing types:", err)
      setExistingTypes([])
    } finally {
      setLoadingTypes(false)
    }
  }

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
    } catch (err) {
      console.error("Error fetching data sources:", err)
      setDataSources([])
    } finally {
      setLoadingDataSources(false)
    }
  }

  const initializeEditForm = (data: MonitoredEntity) => {
    setCustomTypeName(data.name)
    setEditDescription(data.description || "")
    setSelectedDataSourceId(data.data_source_id || "")

    // Check if the entity name exists in existing types
    if (existingTypes.includes(data.name)) {
      setTypeMode("existing")
      setSelectedExistingType(data.name)
    } else {
      setTypeMode("new")
    }
  }

  const handleEdit = () => {
    if (entity) {
      initializeEditForm(entity)
    }
    setIsEditMode(true)
  }

  const handleCancel = () => {
    setIsEditMode(false)
    if (entity) {
      initializeEditForm(entity)
    }
  }

  const validateForm = () => {
    const errors: string[] = []

    if (typeMode === "existing" && !selectedExistingType) {
      errors.push("Please select an existing entity type")
    }
    if (typeMode === "new" && !customTypeName.trim()) {
      errors.push("Please enter a custom entity type name")
    }

    if (errors.length > 0) {
      alert(errors.join(", "))
      return false
    }

    return true
  }

  const handleSave = async () => {
    if (!validateForm()) {
      return
    }

    setIsSaving(true)

    try {
      const entityNameToUse = typeMode === "existing" ? selectedExistingType : customTypeName

      const payload = {
        name: entityNameToUse,
        description: editDescription || undefined,
        data_source_id: selectedDataSourceId || undefined,
      }

      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.MONITORED_ENTITY}/${encodeURIComponent(entityName)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail?.error || "Failed to update monitored entity")
      }

      const data = await response.json()
      setEntity(data)
      setIsEditMode(false)
      alert("Monitored entity updated successfully!")

      // If name changed, redirect to new URL
      if (entityNameToUse !== entityName) {
        router.push(`/monitored-entities/${encodeURIComponent(entityNameToUse)}`)
      } else {
        window.location.reload()
      }
    } catch (err) {
      console.error("Error updating monitored entity:", err)
      alert(err instanceof Error ? err.message : "An error occurred while updating the monitored entity")
    } finally {
      setIsSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading monitored entity...</div>
        </div>
      </div>
    )
  }

  if (!entity) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Monitored entity not found</div>
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

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{isEditMode ? "Edit Entity Type" : entity.name}</h1>
            <p className="text-muted-foreground">
              {isEditMode ? "Modify the monitored entity type details" : "View monitored entity details"}
            </p>
          </div>
          {!isEditMode && (
            <Button onClick={handleEdit} className="bg-blue-600 hover:bg-blue-700">
              <Edit2 className="w-4 h-4 mr-2" />
              Edit
            </Button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900/20 border border-red-800 rounded text-red-400">
          {error}
        </div>
      )}

      {isEditMode ? (
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
                {loadingTypes ? (
                  <div className="text-sm text-muted-foreground">Loading entity types...</div>
                ) : (
                  <select
                    id="existingType"
                    value={selectedExistingType}
                    onChange={(e) => setSelectedExistingType(e.target.value)}
                    className="w-full px-3 py-2 bg-card border border-border rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required={typeMode === "existing"}
                  >
                    <option value="">Select an entity type</option>
                    {existingTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                )}
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
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                className="bg-card border-border min-h-[100px]"
              />
              <p className="text-sm text-muted-foreground">Provide additional context about this entity type</p>
            </div>

            {/* Data Source Selection */}
            <div className="space-y-2">
              <Label htmlFor="dataSource">Data Source (Optional)</Label>
              {loadingDataSources ? (
                <div className="text-sm text-muted-foreground">Loading data sources...</div>
              ) : (
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
              )}
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
              <Button onClick={handleSave} disabled={isSaving} className="bg-blue-600 hover:bg-blue-700">
                <Save className="w-4 h-4 mr-2" />
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
              <Button onClick={handleCancel} variant="outline" disabled={isSaving} className="border-border bg-card">
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="bg-card rounded-lg p-6 border border-border">
          <div className="space-y-6">
            {/* Basic Information */}
            <div>
              <h2 className="text-xl font-semibold mb-4 pb-2 border-b border-border">Basic Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground mb-2 block">Entity Name</Label>
                  <div className="text-base">{entity.name}</div>
                </div>

                <div>
                  <Label className="text-sm font-medium text-muted-foreground mb-2 block">ID</Label>
                  <div className="text-base font-mono text-gray-400">{entity.id || entity.name}</div>
                </div>

                <div className="md:col-span-2">
                  <Label className="text-sm font-medium text-muted-foreground mb-2 block">Description</Label>
                  <div className="text-base">{entity.description || "No description provided"}</div>
                </div>
              </div>
            </div>

            {/* Data Source Information */}
            {entity.data_source && (
              <div>
                <h2 className="text-xl font-semibold mb-4 pb-2 border-b border-border">Data Source</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground mb-2 block">Data Source Name</Label>
                    <div className="text-base">{entity.data_source.name}</div>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground mb-2 block">Database Type</Label>
                    <Badge className="bg-blue-700 text-blue-200 border-blue-600">
                      {entity.data_source.type.database}
                    </Badge>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground mb-2 block">Version</Label>
                    <Badge className="bg-gray-700 text-gray-200 border-gray-600">
                      {entity.data_source.type.version}
                    </Badge>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground mb-2 block">Endpoint URL</Label>
                    <div className="text-base font-mono text-sm">{entity.data_source.end_point.url}</div>
                  </div>
                </div>
              </div>
            )}

            {!entity.data_source && (
              <div>
                <h2 className="text-xl font-semibold mb-4 pb-2 border-b border-border">Data Source</h2>
                <div className="text-sm text-muted-foreground">No data source associated with this entity</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
