"use client"
import { useState, useEffect, useMemo } from "react"
import { Search, Plus, Eye, Sliders, ArrowUp, ArrowDown, ArrowUpDown, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Label } from "@/components/ui/label"
import { ENDPOINTS } from "@/app/api"
import { API_BASE_URL } from "@/app/api"
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

export default function DataSourcesPage() {
  const router = useRouter()
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [filteredDataSources, setFilteredDataSources] = useState<DataSource[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  const [sortConfig, setSortConfig] = useState<{
    key: string
    direction: "asc" | "desc"
  } | null>(null)

  const [dataSourceId, setDataSourceId] = useState("")
  const [databaseTypeFilter, setDatabaseTypeFilter] = useState("")
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDataSources = async () => {
      try {
        setLoading(true)

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
        setFilteredDataSources(data)
        setError(null)
      } catch (err) {
        console.error("Failed to fetch data sources:", err)
        setError(err instanceof Error ? err.message : "An error occurred")
        setDataSources([])
        setFilteredDataSources([])
      } finally {
        setLoading(false)
      }
    }

    fetchDataSources()
  }, [])

  useEffect(() => {
    let filtered = dataSources

    if (searchTerm) {
      filtered = filtered.filter(
        (dataSource) =>
          dataSource.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          dataSource.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          dataSource.type?.version?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          dataSource.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          dataSource.type?.database?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          dataSource.end_point?.url?.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    if (dataSourceId) {
      filtered = filtered.filter((dataSource) => dataSource.id?.toLowerCase().includes(dataSourceId.toLowerCase()))
    }

    if (databaseTypeFilter) {
      filtered = filtered.filter((dataSource) => dataSource.type.database === databaseTypeFilter)
    }

    setFilteredDataSources(filtered)
  }, [searchTerm, dataSources, dataSourceId, databaseTypeFilter])

  const clearAllFilters = () => {
    setDataSourceId("")
    setDatabaseTypeFilter("")
  }

  const getActiveFiltersCount = () => {
    let count = 0
    if (dataSourceId) count++
    if (databaseTypeFilter) count++
    return count
  }

  const handleSort = (key: string) => {
    let direction: "asc" | "desc" = "asc"
    if (sortConfig && sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc"
    }
    setSortConfig({ key, direction })
  }

  const sortedDataSources = useMemo(() => {
    if (!sortConfig) return filteredDataSources

    return [...filteredDataSources].sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortConfig.key) {
        case "name":
          aValue = a.name || ""
          bValue = b.name || ""
          break
        case "version":
          aValue = a.type?.version || ""
          bValue = b.type?.version || ""
          break
        case "description":
          aValue = a.description || ""
          bValue = b.description || ""
          break
        case "database":
          aValue = a.type?.database || ""
          bValue = b.type?.database || ""
          break
        case "url":
          aValue = a.end_point?.url || ""
          bValue = b.end_point?.url || ""
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
  }, [filteredDataSources, sortConfig])

  const totalPages = Math.ceil(sortedDataSources.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedDataSources = sortedDataSources.slice(startIndex, endIndex)

  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, dataSourceId, databaseTypeFilter])

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

  const handleViewDataSource = (dataSourceId: string) => {
    router.push(`/data-sources/${dataSourceId}`)
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

  if (loading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading data sources...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 bg-page-background text-page-foreground min-h-screen">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Data Sources</h1>
        <Link href="/data-sources/new">
          <Button className="bg-blue-600 hover:bg-blue-700 text-white">
            <Plus className="w-4 h-4 mr-2" />
            Create New Data Source
          </Button>
        </Link>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search data sources..."
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
              <h4 className="text-sm font-medium text-muted-foreground">Identifiers</h4>
              <div className="space-y-2">
                <div>
                  <Label className="text-xs text-muted-foreground mb-1 block">Data Source ID</Label>
                  <Input
                    placeholder="Filter by Data Source ID..."
                    value={dataSourceId}
                    onChange={(e) => setDataSourceId(e.target.value)}
                    className="bg-muted border-border text-sm"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">Database Type</h4>
              <div className="space-y-2">
                <div>
                  <Label className="text-xs text-muted-foreground mb-1 block">Database Type</Label>
                  <select
                    value={databaseTypeFilter}
                    onChange={(e) => setDatabaseTypeFilter(e.target.value)}
                    className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground"
                  >
                    <option value="">All Types</option>
                    <option value={DatabaseType.INFLUXDB}>InfluxDB</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {(dataSourceId || databaseTypeFilter) && (
            <div className="mt-4 pt-3 border-t border-border">
              <div className="flex flex-wrap gap-2">
                {dataSourceId && (
                  <Badge variant="secondary" className="text-xs">
                    ID: {dataSourceId}
                  </Badge>
                )}
                {databaseTypeFilter && (
                  <Badge variant="secondary" className="text-xs">
                    Database: {databaseTypeFilter}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-card rounded-lg p-6 border border-border">
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Data Source Management</h2>
          <p className="text-muted-foreground">View and manage configured data sources</p>
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
                      Name
                      <SortIcon column="name" />
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
                  <TableHead
                    className="text-muted-foreground cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort("version")}
                  >
                    <div className="flex items-center">
                      Version
                      <SortIcon column="version" />
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
                    onClick={() => handleSort("url")}
                  >
                    <div className="flex items-center">
                      URL
                      <SortIcon column="url" />
                    </div>
                  </TableHead>
                  <TableHead className="text-muted-foreground">Metadata</TableHead>
                  <TableHead className="text-muted-foreground sticky right-0 bg-card border-l border-border min-w-[120px]">
                    Actions
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedDataSources.map((dataSource) => (
                  <TableRow key={dataSource.id} className="border-border hover:bg-muted/30">
                    <TableCell className="font-medium max-w-xs truncate">{dataSource.name || "No name"}</TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="text-xs bg-blue-700 text-blue-200 border-blue-600">
                        {dataSource.type.database}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {dataSource.type.version ? (
                        <Badge variant="secondary" className="text-xs bg-gray-700 text-gray-200 border-gray-600">
                          {dataSource.type.version}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="max-w-xs truncate">{dataSource.description || "No description"}</TableCell>
                    <TableCell className="font-mono text-sm max-w-xs truncate">{dataSource.end_point.url}</TableCell>
                    <TableCell>
                      {dataSource.end_point.metadata && Object.keys(dataSource.end_point.metadata).length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(dataSource.end_point.metadata)
                            .slice(0, 2)
                            .map(([key, value]) => (
                              <Badge key={key} variant="outline" className="text-xs border-border text-gray-300">
                                {key}: {String(value)}
                              </Badge>
                            ))}
                          {Object.keys(dataSource.end_point.metadata).length > 2 && (
                            <Badge variant="outline" className="text-xs border-border text-gray-300">
                              +{Object.keys(dataSource.end_point.metadata).length - 2} more
                            </Badge>
                          )}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="sticky right-0 bg-card border-l border-border">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-8 px-2"
                          onClick={() => handleViewDataSource(dataSource.id || "")}
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
                Showing {startIndex + 1} to {Math.min(endIndex, sortedDataSources.length)} of {sortedDataSources.length}{" "}
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

        {filteredDataSources.length === 0 && !loading && (
          <div className="text-center py-8 text-muted-foreground">No data sources found matching your criteria.</div>
        )}
      </div>
    </div>
  )
}
