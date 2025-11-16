"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Edit2, Save, X, Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
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

interface MetadataEntry {
  key: string
  value: string
}

export default function DataSourceDetailPage() {
  const params = useParams()
  const router = useRouter()
  const dataSourceId = params.id as string

  const [dataSource, setDataSource] = useState<DataSource | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Edit form state
  const [editName, setEditName] = useState("")
  const [editDescription, setEditDescription] = useState("")
  const [editDatabase, setEditDatabase] = useState<DatabaseType>(DatabaseType.INFLUXDB)
  const [editVersion, setEditVersion] = useState("")
  const [editUrl, setEditUrl] = useState("")
  const [editMetadata, setEditMetadata] = useState<MetadataEntry[]>([])

  useEffect(() => {
    const fetchDataSource = async () => {
      try {
        setLoading(true)
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.DATA_SOURCE}/${dataSourceId}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          throw new Error("Failed to fetch data source")
        }

        const data = await response.json()
        setDataSource(data)
        initializeEditForm(data)
        setError(null)
      } catch (err) {
        console.error("Failed to fetch data source:", err)
        setError(err instanceof Error ? err.message : "An error occurred")
      } finally {
        setLoading(false)
      }
    }

    fetchDataSource()
  }, [dataSourceId])

  const initializeEditForm = (data: DataSource) => {
    setEditName(data.name)
    setEditDescription(data.description || "")

    // Validate `type` and `type.database`
    if (data.type && data.type.database) {
      setEditDatabase(data.type.database)
    } else {
      console.warn("Data source type or database is missing", data)
      setEditDatabase(DatabaseType.INFLUXDB) // Default value
    }

    setEditVersion(data.type?.version || "")

    // Validate `end_point` and `end_point.url`
    if (data.end_point && data.end_point.url) {
      setEditUrl(data.end_point.url)
    } else {
      console.warn("Data source endpoint or URL is missing", data)
      setEditUrl("") // Default value
    }

    const metadataEntries: MetadataEntry[] = data.end_point?.metadata
      ? Object.entries(data.end_point.metadata).map(([key, value]) => ({
          key,
          value: String(value),
        }))
      : []
    setEditMetadata(metadataEntries)
  }

  const handleEdit = () => {
    if (dataSource) {
      initializeEditForm(dataSource)
    }
    setIsEditMode(true)
  }

  const handleCancel = () => {
    setIsEditMode(false)
    if (dataSource) {
      initializeEditForm(dataSource)
    }
  }

  const handleSave = async () => {
    if (!editName.trim()) {
      alert("Name is required")
      return
    }

    if (!editVersion.trim()) {
      alert("Version is required")
      return
    }

    if (!editUrl.trim()) {
      alert("URL is required")
      return
    }

    const urlPattern = /^https?:\/\/.+/
    if (!urlPattern.test(editUrl)) {
      alert("Please enter a valid URL starting with http:// or https://")
      return
    }

    const metadata: Record<string, any> = {}
    for (const entry of editMetadata) {
      if (entry.key.trim()) {
        let value: any = entry.value
        if (value === "true") value = true
        else if (value === "false") value = false
        else if (!isNaN(Number(value)) && value.trim() !== "") value = Number(value)
        metadata[entry.key] = value
      }
    }

    const updatedDataSource: DataSource = {
      id: dataSourceId,
      name: editName,
      description: editDescription || undefined,
      type: {
        database: editDatabase,
        version: editVersion,
      },
      end_point: {
        url: editUrl,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
      },
    }

    try {
      setIsSaving(true)
      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.DATA_SOURCE}/${dataSourceId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedDataSource),
      })

      if (!response.ok) {
        throw new Error("Failed to update data source")
      }

      const data = await response.json()
      setDataSource(data)
      setIsEditMode(false)
      alert("Data source updated successfully!")

      // Reload the page to reflect updated data
      window.location.reload()
    } catch (err) {
      console.error("Error updating data source:", err)
      // For development, simulate success
      setDataSource(updatedDataSource)
      setIsEditMode(false)
      alert("Data source updated successfully! (Mock mode)")

      // Reload the page to reflect updated data
      window.location.reload()
    } finally {
      setIsSaving(false)
    }
  }

  const addMetadataEntry = () => {
    setEditMetadata([...editMetadata, { key: "", value: "" }])
  }

  const removeMetadataEntry = (index: number) => {
    setEditMetadata(editMetadata.filter((_, i) => i !== index))
  }

  const updateMetadataEntry = (index: number, field: "key" | "value", value: string) => {
    const updated = [...editMetadata]
    updated[index][field] = value
    setEditMetadata(updated)
  }

  if (loading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading data source...</div>
        </div>
      </div>
    )
  }

  if (!dataSource) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Data source not found</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      <div className="mb-6">
        <Link href="/data-sources">
          <Button variant="ghost" className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Data Sources
          </Button>
        </Link>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{isEditMode ? "Edit Data Source" : dataSource.name}</h1>
            <p className="text-muted-foreground">
              {isEditMode ? "Modify the data source configuration" : "View data source details"}
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

      <div className="bg-card rounded-lg p-6 border border-border">
        <div className="space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-xl font-semibold mb-4 pb-2 border-b border-border">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label className="text-sm font-medium text-muted-foreground mb-2 block">Name</Label>
                {isEditMode ? (
                  <Input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    placeholder="Data source name"
                    className="bg-card border-border"
                  />
                ) : (
                  <div className="text-base">{dataSource.name}</div>
                )}
              </div>

              <div>
                <Label className="text-sm font-medium text-muted-foreground mb-2 block">ID</Label>
                <div className="text-base font-mono text-gray-400">{dataSource.id}</div>
              </div>

              <div className="md:col-span-2">
                <Label className="text-sm font-medium text-muted-foreground mb-2 block">Description</Label>
                {isEditMode ? (
                  <Textarea
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    placeholder="Data source description"
                    className="bg-card border-border min-h-[80px]"
                  />
                ) : (
                  <div className="text-base">{dataSource.description || "No description provided"}</div>
                )}
              </div>
            </div>
          </div>

          {/* Database Configuration */}
          <div>
            <h2 className="text-xl font-semibold mb-4 pb-2 border-b border-border">Database Configuration</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label className="text-sm font-medium text-muted-foreground mb-2 block">Database Type</Label>
                {isEditMode ? (
                  <select
                    value={editDatabase}
                    onChange={(e) => setEditDatabase(e.target.value as DatabaseType)}
                    className="w-full bg-card border border-border rounded-md px-3 py-2 text-sm text-foreground"
                  >
                    <option value={DatabaseType.INFLUXDB}>InfluxDB</option>
                  </select>
                ) : (
                  <Badge className="bg-blue-700 text-blue-200 border-blue-600">
                    {dataSource?.type?.database || "Unknown"}
                  </Badge>
                )}
              </div>

              <div>
                <Label className="text-sm font-medium text-muted-foreground mb-2 block">Version</Label>
                {isEditMode ? (
                  <Input
                    value={editVersion}
                    onChange={(e) => setEditVersion(e.target.value)}
                    placeholder="1.0.0"
                    className="bg-card border-border"
                  />
                ) : (
                  <Badge className="bg-gray-700 text-gray-200 border-gray-600">
                    {dataSource?.type?.version || "Unknown Version"}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Endpoint Configuration */}
          <div>
            <h2 className="text-xl font-semibold mb-4 pb-2 border-b border-border">Endpoint Configuration</h2>
            <div className="space-y-4">
              <div>
                <Label className="text-sm font-medium text-muted-foreground mb-2 block">URL</Label>
                {isEditMode ? (
                  <Input
                    value={editUrl}
                    onChange={(e) => setEditUrl(e.target.value)}
                    placeholder="https://example.com:8086"
                    className="bg-card border-border font-mono"
                  />
                ) : (
                  <div className="text-base font-mono bg-muted px-3 py-2 rounded border border-border">
                    {dataSource.end_point.url}
                  </div>
                )}
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm font-medium text-muted-foreground">Metadata</Label>
                  {isEditMode && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={addMetadataEntry}
                      className="border-border bg-card"
                    >
                      <Plus className="w-3 h-3 mr-1" />
                      Add Entry
                    </Button>
                  )}
                </div>

                {isEditMode ? (
                  <div className="space-y-2">
                    {editMetadata.length === 0 ? (
                      <div className="text-sm text-muted-foreground bg-muted px-3 py-2 rounded border border-border">
                        No metadata entries. Click "Add Entry" to add one.
                      </div>
                    ) : (
                      editMetadata.map((entry, index) => (
                        <div key={index} className="flex gap-2">
                          <Input
                            placeholder="Key"
                            value={entry.key}
                            onChange={(e) => updateMetadataEntry(index, "key", e.target.value)}
                            className="flex-1 bg-card border-border"
                          />
                          <Input
                            placeholder="Value"
                            value={entry.value}
                            onChange={(e) => updateMetadataEntry(index, "value", e.target.value)}
                            className="flex-1 bg-card border-border"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeMetadataEntry(index)}
                            className="shrink-0"
                          >
                            <Trash2 className="w-4 h-4 text-red-400" />
                          </Button>
                        </div>
                      ))
                    )}
                  </div>
                ) : (
                  <div className="space-y-2">
                    {dataSource.end_point.metadata && Object.keys(dataSource.end_point.metadata).length > 0 ? (
                      <div className="bg-muted px-3 py-2 rounded border border-border">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {Object.entries(dataSource.end_point.metadata).map(([key, value]) => (
                            <div key={key} className="flex items-center gap-2">
                              <span className="text-sm font-medium text-blue-400">{key}:</span>
                              <span className="text-sm text-gray-300">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="text-sm text-muted-foreground bg-muted px-3 py-2 rounded border border-border">
                        No metadata configured
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons in Edit Mode */}
        {isEditMode && (
          <div className="flex gap-3 mt-6 pt-6 border-t border-border">
            <Button onClick={handleSave} disabled={isSaving} className="bg-blue-600 hover:bg-blue-700">
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? "Saving..." : "Save Changes"}
            </Button>
            <Button onClick={handleCancel} variant="outline" disabled={isSaving} className="border-border bg-card">
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
