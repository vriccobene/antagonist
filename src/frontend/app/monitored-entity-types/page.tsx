"use client"
import { useState, useEffect, useMemo } from "react"
import { Search, Plus, Eye, Sliders, ArrowUp, ArrowDown, ArrowUpDown, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Label } from "@/components/ui/label"
import { ENDPOINTS, API_BASE_URL } from "@/app/api"
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

interface MonitoredEntity {
  name: string
  description?: string
  data_source?: DataSource
}

export default function MonitoredEntitiesPage() {
  const router = useRouter()
  const [monitoredEntities, setMonitoredEntities] = useState<MonitoredEntity[]>([])
  const [filteredEntities, setFilteredEntities] = useState<MonitoredEntity[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  const [sortConfig, setSortConfig] = useState<{
    key: string
    direction: "asc" | "desc"
  } | null>(null)

  const [entityNameFilter, setEntityNameFilter] = useState("")
  const [dataSourceFilter, setDataSourceFilter] = useState("")
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMonitoredEntities = async () => {
      try {
        setLoading(true)

        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.MONITORED_ENTITY}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        })

        if (!response.ok) {
          throw new Error("Failed to fetch monitored entities")
        }

        const data = await response.json()
        setMonitoredEntities(data)
        setFilteredEntities(data)
        setError(null)
      } catch (err) {
        console.error("Failed to fetch monitored entity types:", err)
        setError(err instanceof Error ? err.message : "An error occurred")
        setMonitoredEntities([])
        setFilteredEntities([])
      } finally {
        setLoading(false)
      }
    }

    fetchMonitoredEntities()
  }, [])

  useEffect(() => {
    let filtered = monitoredEntities

    if (searchTerm) {
      filtered = filtered.filter(
        (entity) =>
          entity.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          entity.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          entity.data_source?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          entity.data_source?.description?.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    if (entityNameFilter) {
      filtered = filtered.filter((entity) => entity.name?.toLowerCase().includes(entityNameFilter.toLowerCase()))
    }

    if (dataSourceFilter) {
      filtered = filtered.filter((entity) =>
        entity.data_source?.name?.toLowerCase().includes(dataSourceFilter.toLowerCase()),
      )
    }

    setFilteredEntities(filtered)
  }, [searchTerm, monitoredEntities, entityNameFilter, dataSourceFilter])

  const clearAllFilters = () => {
    setEntityNameFilter("")
    setDataSourceFilter("")
  }

  const getActiveFiltersCount = () => {
    let count = 0
    if (entityNameFilter) count++
    if (dataSourceFilter) count++
    return count
  }

  const handleSort = (key: string) => {
    let direction: "asc" | "desc" = "asc"
    if (sortConfig && sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc"
    }
    setSortConfig({ key, direction })
  }

  // Ensure `sortedEntities` is always an array
  const sortedEntities = useMemo(() => {
    if (!Array.isArray(filteredEntities)) return []

    if (!sortConfig) return filteredEntities

    return [...filteredEntities].sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortConfig.key) {
        case "name":
          aValue = a.name || ""
          bValue = b.name || ""
          break
        case "description":
          aValue = a.description || ""
          bValue = b.description || ""
          break
        case "dataSource":
          aValue = a.data_source?.name || ""
          bValue = b.data_source?.name || ""
          break
        case "database":
          aValue = a.data_source?.type?.database || ""
          bValue = b.data_source?.type?.database || ""
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
  }, [filteredEntities, sortConfig])

  const totalPages = Math.ceil(sortedEntities.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  // Ensure `paginatedEntities` is computed safely
  const paginatedEntities = Array.isArray(sortedEntities) ? sortedEntities.slice(startIndex, endIndex) : []

  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, entityNameFilter, dataSourceFilter])

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

  const handleEditEntity = (entityName: string) => {
    router.push(`/monitored-entity-types/${encodeURIComponent(entityName)}`)
  }

  if (loading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading monitored entities...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Monitored Entity Types</h1>
        <Link href="/monitored-entity-types/new">
          <Button className="bg-blue-600 hover:bg-blue-700 text-white">
            <Plus className="w-4 h-4 mr-2" />
            Create New Entity Type
          </Button>
        </Link>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search monitored entities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-card border-border"
          />
        </div>
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
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">Entity Information</h4>
              <div className="space-y-2">
                <div>
                  <Label className="text-xs text-muted-foreground mb-1 block">Entity Name</Label>
                  <Input
                    placeholder="Filter by entity name..."
                    value={entityNameFilter}
                    onChange={(e) => setEntityNameFilter(e.target.value)}
                    className="bg-muted border-border text-sm"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">Data Source</h4>
              <div className="space-y-2">
                <div>
                  <Label className="text-xs text-muted-foreground mb-1 block">Data Source Name</Label>
                  <Input
                    placeholder="Filter by data source..."
                    value={dataSourceFilter}
                    onChange={(e) => setDataSourceFilter(e.target.value)}
                    className="bg-muted border-border text-sm"
                  />
                </div>
              </div>
            </div>
          </div>

          {(entityNameFilter || dataSourceFilter) && (
            <div className="mt-4 pt-3 border-t border-border">
              <div className="flex flex-wrap gap-2">
                {entityNameFilter && (
                  <Badge variant="secondary" className="text-xs">
                    Entity: {entityNameFilter}
                  </Badge>
                )}
                {dataSourceFilter && (
                  <Badge variant="secondary" className="text-xs">
                    Data Source: {dataSourceFilter}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-card rounded-lg p-6 border border-border">
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Monitored Entity Types Management</h2>
          <p className="text-muted-foreground">
            {"Add here all the entities to be captured and monitored by the system"}{" "}
          </p>
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
                    className="text-muted-foreground cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("name")}
                  >
                    <div className="flex items-center">
                      Entity Name
                      <SortIcon column="name" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("description")}
                  >
                    <div className="flex items-center">
                      Description
                      <SortIcon column="description" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("dataSource")}
                  >
                    <div className="flex items-center">
                      Data Source
                      <SortIcon column="dataSource" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("database")}
                  >
                    <div className="flex items-center">
                      Database Type
                      <SortIcon column="database" />
                    </div>
                  </TableHead>
                  <TableHead className="text-muted-foreground">Endpoint URL</TableHead>
                  <TableHead className="text-muted-foreground sticky right-0 bg-card border-l border-border min-w-[120px]">
                    Actions
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedEntities.map((entity, index) => (
                  <TableRow key={`${entity.name}-${index}`} className="border-border hover:bg-muted/30">
                    <TableCell className="font-medium max-w-xs truncate">{entity.name || "No name"}</TableCell>
                    <TableCell className="max-w-xs truncate">{entity.description || "No description"}</TableCell>
                    <TableCell>
                      {entity.data_source ? (
                        <div className="flex flex-col gap-1">
                          <span className="font-medium">{entity.data_source.name}</span>
                          {entity.data_source.description && (
                            <span className="text-xs text-muted-foreground">{entity.data_source.description}</span>
                          )}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">No data source</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {entity.data_source ? (
                        <Badge variant="secondary" className="text-xs bg-blue-700 text-blue-200 border-blue-600">
                          {entity.data_source.type.database}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-sm max-w-xs truncate">
                      {entity.data_source?.end_point?.url || "-"}
                    </TableCell>
                    <TableCell className="sticky right-0 bg-card border-l border-border">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-8 px-2"
                          onClick={() => handleEditEntity(entity.name)}
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
                Showing {startIndex + 1} to {Math.min(endIndex, sortedEntities.length)} of {sortedEntities.length}{" "}
                results
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={goToPreviousPage}
                  disabled={currentPage === 1}
                  className="border-border bg-card"
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
                  className="border-border bg-card"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {filteredEntities.length === 0 && !loading && (
          <div className="text-center py-8 text-muted-foreground">
            No monitored entities found matching your criteria.
          </div>
        )}
      </div>
    </div>
  )
}
