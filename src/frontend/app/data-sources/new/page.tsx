"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Plus, X } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { API_BASE_URL, ENDPOINTS } from "@/app/api"

enum DatabaseType {
  INFLUXDB = "influxdb",
}

interface MetadataEntry {
  key: string
  value: string
}

export default function NewDataSourcePage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form fields
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [database, setDatabase] = useState<DatabaseType>(DatabaseType.INFLUXDB)
  const [version, setVersion] = useState("")
  const [url, setUrl] = useState("")
  const [metadataEntries, setMetadataEntries] = useState<MetadataEntry[]>([])

  // Validation errors
  const [errors, setErrors] = useState<Record<string, string>>({})

  const addMetadataEntry = () => {
    setMetadataEntries([...metadataEntries, { key: "", value: "" }])
  }

  const removeMetadataEntry = (index: number) => {
    setMetadataEntries(metadataEntries.filter((_, i) => i !== index))
  }

  const updateMetadataEntry = (index: number, field: "key" | "value", value: string) => {
    const updated = [...metadataEntries]
    updated[index][field] = value
    setMetadataEntries(updated)
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!name.trim()) {
      newErrors.name = "Name is required"
    }

    if (!version.trim()) {
      newErrors.version = "Version is required"
    }

    if (!url.trim()) {
      newErrors.url = "URL is required"
    } else if (!/^https?:\/\/.+/.test(url)) {
      newErrors.url = "URL must start with http:// or https://"
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
      // Build metadata object from entries
      const metadata: Record<string, any> = {}
      metadataEntries.forEach((entry) => {
        if (entry.key.trim()) {
          // Try to parse value as JSON, otherwise use as string
          try {
            metadata[entry.key] = JSON.parse(entry.value)
          } catch {
            metadata[entry.key] = entry.value
          }
        }
      })

      const payload = {
        name: name.trim(),
        description: description.trim() || undefined,
        type: {
          database: database,
          version: version.trim(),
        },
        end_point: {
          url: url.trim(),
          metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
        },
      }

      console.log("Submitting data source:", payload)

      const response = await fetch(`${API_BASE_URL}${ENDPOINTS.DATA_SOURCE}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || "Failed to create data source")
      }

      const responseData = await response.json() // Parse response for additional feedback
      console.log("Data source created successfully", responseData)
      alert("Data source created successfully! ID: " + responseData.id) // Provide user feedback

      // Success - navigate back to data sources list
      router.push("/data-sources")
    } catch (err) {
      console.error("Error creating data source:", err)
      setError(err instanceof Error ? err.message : "An error occurred while creating the data source")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <Link href="/data-sources">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Data Sources
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">Create New Data Source</h1>
          <p className="text-muted-foreground mt-2">Configure a new data source for your telemetry system</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400">
            <p className="font-medium">Error creating data source</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>Provide the basic details for your data source</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  placeholder="Production Database"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={errors.name ? "border-red-500" : ""}
                />
                {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
                <p className="text-sm text-muted-foreground">A descriptive name for this data source</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Main production database for user data"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">
                  Optional description of what this data source is used for
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Database Configuration</CardTitle>
              <CardDescription>Specify the database type and version</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="database">Database Type *</Label>
                <Select value={database} onValueChange={(value) => setDatabase(value as DatabaseType)}>
                  <SelectTrigger id="database">
                    <SelectValue placeholder="Select database type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={DatabaseType.INFLUXDB}>InfluxDB</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">The type of database system</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="version">Version *</Label>
                <Input
                  id="version"
                  placeholder="2.7.1"
                  value={version}
                  onChange={(e) => setVersion(e.target.value)}
                  className={errors.version ? "border-red-500" : ""}
                />
                {errors.version && <p className="text-sm text-red-500">{errors.version}</p>}
                <p className="text-sm text-muted-foreground">The version of the database system</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Endpoint Configuration</CardTitle>
              <CardDescription>Configure the connection endpoint</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="url">URL *</Label>
                <Input
                  id="url"
                  placeholder="https://influxdb.example.com:8086"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className={errors.url ? "border-red-500" : ""}
                />
                {errors.url && <p className="text-sm text-red-500">{errors.url}</p>}
                <p className="text-sm text-muted-foreground">The full URL to connect to the data source</p>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Metadata</Label>
                    <p className="text-sm text-muted-foreground">
                      Optional key-value pairs for additional configuration
                    </p>
                  </div>
                  <Button type="button" variant="outline" size="sm" onClick={addMetadataEntry}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Entry
                  </Button>
                </div>

                {metadataEntries.length > 0 && (
                  <div className="space-y-2">
                    {metadataEntries.map((entry, index) => (
                      <div key={index} className="flex gap-2 items-start">
                        <Input
                          placeholder="Key"
                          value={entry.key}
                          onChange={(e) => updateMetadataEntry(index, "key", e.target.value)}
                          className="flex-1"
                        />
                        <Input
                          placeholder="Value"
                          value={entry.value}
                          onChange={(e) => updateMetadataEntry(index, "value", e.target.value)}
                          className="flex-1"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeMetadataEntry(index)}
                          className="shrink-0"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}

                {metadataEntries.length === 0 && (
                  <div className="text-sm text-muted-foreground italic">No metadata entries added</div>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-4 justify-end">
            <Link href="/data-sources">
              <Button type="button" variant="outline" disabled={isSubmitting}>
                Cancel
              </Button>
            </Link>
            <Button type="submit" disabled={isSubmitting} className="bg-blue-600 hover:bg-blue-700">
              {isSubmitting ? "Creating..." : "Create Data Source"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
