"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { AlertTriangle, Database, Activity, Plus, ArrowRight, Eye, Server, Layers } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ENDPOINTS, API_BASE_URL } from "@/app/api"
import type { RelevantState } from "@/lib/shared-types"

interface DataSource {
  id?: string
  name?: string
  type?: string
  status?: string
  host?: string
}

interface MonitoredEntityType {
  id?: string
  name?: string
  description?: string
}

interface DashboardStats {
  incidents: {
    total: number
    ongoing: number
    highConcern: number
  }
  anomalies: {
    total: number
    ongoing: number
    toBeAnalysed: number
  }
  dataSources: {
    total: number
    active: number
  }
  entityTypes: {
    total: number
  }
}

export default function HomePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<DashboardStats>({
    incidents: { total: 0, ongoing: 0, highConcern: 0 },
    anomalies: { total: 0, ongoing: 0, toBeAnalysed: 0 },
    dataSources: { total: 0, active: 0 },
    entityTypes: { total: 0 },
  })
  const [recentIncidents, setRecentIncidents] = useState<RelevantState[]>([])
  const [recentAnomalies, setRecentAnomalies] = useState<RelevantState[]>([])
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [entityTypes, setEntityTypes] = useState<MonitoredEntityType[]>([])

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        setError(null)

        const now = new Date()
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

        let incidents: RelevantState[] = []
        let anomalies: RelevantState[] = []
        let dataSourcesData: DataSource[] = []
        let entityTypesData: MonitoredEntityType[] = []

        // Fetch incidents
        try {
          const incidentsParams = new URLSearchParams({
            state: "incident",
            start_time: thirtyDaysAgo.toISOString().slice(0, 10),
            end_time: now.toISOString().slice(0, 10),
          })

          const incidentsResponse = await fetch(
            `${API_BASE_URL}${ENDPOINTS.RELEVANT_STATE}?${incidentsParams.toString()}`,
            { signal: AbortSignal.timeout(5000) },
          )

          if (incidentsResponse.ok) {
            incidents = await incidentsResponse.json()
          } else {
            console.error("Failed to fetch incidents")
          }
        } catch (error) {
          console.error("Error fetching incidents:", error)
        }

        // Fetch anomalies (relevant states that are not incidents)
        try {
          const anomaliesParams = new URLSearchParams({
            start_time: thirtyDaysAgo.toISOString().slice(0, 10),
            end_time: now.toISOString().slice(0, 10),
          })
          const anomaliesResponse = await fetch(
            `${API_BASE_URL}${ENDPOINTS.RELEVANT_STATE}?${anomaliesParams.toString()}`,
            {
              signal: AbortSignal.timeout(5000),
            },
          )

          if (anomaliesResponse.ok) {
            const allRelevantStates = await anomaliesResponse.json()
            // Filter out incidents - anomalies are relevant states with state != "incident"
            anomalies = Array.isArray(allRelevantStates)
              ? allRelevantStates.filter((rs: RelevantState) => rs.state !== "incident")
              : []
            console.log("Fetched anomalies:", anomalies)
          } else {
            console.error("Failed to fetch anomalies")
          }
        } catch (error) {
          console.error("Error fetching anomalies:", error)
        }

        // Fetch data sources
        try {
          const dataSourcesResponse = await fetch(`${API_BASE_URL}${ENDPOINTS.DATA_SOURCE}`, {
            signal: AbortSignal.timeout(5000),
          })

          if (dataSourcesResponse.ok) {
            dataSourcesData = await dataSourcesResponse.json()
          } else {
            console.error("Failed to fetch data sources")
          }
        } catch (error) {
          console.error("Error fetching data sources:", error)
        }

        // Fetch monitored entity types
        try {
          const entityTypesResponse = await fetch(`${API_BASE_URL}${ENDPOINTS.MONITORED_ENTITY}`, {
            signal: AbortSignal.timeout(5000),
          })

          if (entityTypesResponse.ok) {
            entityTypesData = await entityTypesResponse.json()
          } else {
            console.error("Failed to fetch entity types")
          }
        } catch (error) {
          console.error("Error fetching entity types:", error)
        }

        // Calculate stats
        const ongoingIncidents = incidents.filter((i) => !i.end_time)
        const highConcernIncidents = incidents.filter((i) => i.concern_score >= 0.8)
        const ongoingAnomalies = anomalies.filter((a) => !a.end_time && a.state === "confirmed")
        const toBeAnalysedAnomalies = anomalies.filter(
          (a) => a.state === "unknown" || a.state === "potential" || a.state === "forecasted",
        )
        const activeDataSources = dataSourcesData.filter((ds) => ds.status === "active" || !ds.status)

        setStats({
          incidents: {
            total: incidents.length,
            ongoing: ongoingIncidents.length,
            highConcern: highConcernIncidents.length,
          },
          anomalies: {
            total: anomalies.length,
            ongoing: ongoingAnomalies.length,
            toBeAnalysed: toBeAnalysedAnomalies.length,
          },
          dataSources: {
            total: dataSourcesData.length,
            active: activeDataSources.length,
          },
          entityTypes: {
            total: entityTypesData.length,
          },
        })

        // Set recent items (top 5)
        setRecentIncidents(incidents.slice(0, 5))
        setRecentAnomalies(anomalies.slice(0, 5))
        setDataSources(dataSourcesData.slice(0, 5))
        setEntityTypes(entityTypesData.slice(0, 5))
      } catch (error) {
        console.error("Error fetching dashboard data:", error)
        setError("Failed to load dashboard data. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getConcernColor = (score: number) => {
    if (score >= 0.8) return "text-red-400"
    if (score >= 0.6) return "text-yellow-400"
    return "text-green-400"
  }

  if (loading) {
    return (
      <div className="p-8 bg-page-background text-page-foreground min-h-screen">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading dashboard...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-page-background text-page-foreground min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-muted-foreground">Overview of your anomaly detection system</p>
        {error && (
          <div className="mt-3 p-2.5 bg-red-900/20 border border-red-800 rounded text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Incidents Card */}
        <Card className="bg-card border-border hover:border-muted transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 px-4 pt-4">
            <CardTitle className="text-sm font-medium text-card-foreground">Incidents</CardTitle>
            <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4 text-red-400" />
            </div>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <div className="text-3xl font-bold mb-3 text-card-foreground">{stats.incidents.total}</div>
            <div className="space-y-1.5 mb-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-foreground/60">Ongoing</span>
                <span className="font-medium text-yellow-500">{stats.incidents.ongoing}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-foreground/60">High concern</span>
                <span className="font-medium text-red-500">{stats.incidents.highConcern}</span>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="w-full h-8 text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
              onClick={() => router.push("/incidents")}
            >
              View All
              <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </CardContent>
        </Card>

        {/* Anomalies Card */}
        <Card className="bg-card border-border hover:border-muted transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 px-4 pt-4">
            <CardTitle className="text-sm font-medium text-card-foreground">Anomalies</CardTitle>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Activity className="w-4 h-4 text-blue-400" />
            </div>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <div className="text-3xl font-bold mb-3 text-card-foreground">{stats.anomalies.total}</div>
            <div className="space-y-1.5 mb-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-foreground/60">Ongoing</span>
                <span className="font-medium text-orange-500">{stats.anomalies.ongoing}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-foreground/60">To be analysed</span>
                <span className="font-medium text-blue-500">{stats.anomalies.toBeAnalysed}</span>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="w-full h-8 text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
              onClick={() => router.push("/anomalies")}
            >
              View All
              <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </CardContent>
        </Card>

        {/* Data Sources Card */}
        <Card className="bg-card border-border hover:border-muted transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 px-4 pt-4">
            <CardTitle className="text-sm font-medium text-card-foreground">Data Sources</CardTitle>
            <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
              <Database className="w-4 h-4 text-green-400" />
            </div>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <div className="text-3xl font-bold mb-3 text-card-foreground">{stats.dataSources.total}</div>
            <div className="space-y-1.5 mb-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-foreground/60">Active</span>
                <span className="font-medium text-green-500">{stats.dataSources.active}</span>
              </div>
              <div className="h-4"></div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="w-full h-8 text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
              onClick={() => router.push("/data-sources")}
            >
              Manage
              <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </CardContent>
        </Card>

        {/* Entity Types Card */}
        <Card className="bg-card border-border hover:border-muted transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 px-4 pt-4">
            <CardTitle className="text-sm font-medium text-card-foreground">Entity Types</CardTitle>
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center">
              <Layers className="w-4 h-4 text-purple-400" />
            </div>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <div className="text-3xl font-bold mb-3 text-card-foreground">{stats.entityTypes.total}</div>
            <div className="space-y-1.5 mb-3">
              <div className="text-xs text-foreground/60">Monitored types configured</div>
              <div className="h-4"></div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="w-full h-8 text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
              onClick={() => router.push("/monitored-entity-types")}
            >
              Manage
              <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Items */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent Incidents */}
        <Card className="bg-card border-border">
          <CardHeader className="flex flex-row items-center justify-between px-5 py-4">
            <div>
              <CardTitle className="text-base font-semibold text-card-foreground">Recent Incidents</CardTitle>
              <CardDescription className="text-xs text-foreground/60">Latest detected incidents</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/incidents")}
              className="text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
            >
              View All
            </Button>
          </CardHeader>
          <CardContent className="px-5 pb-5">
            {recentIncidents.length > 0 ? (
              <div className="space-y-2">
                {recentIncidents.map((incident) => (
                  <div
                    key={incident.id}
                    className="flex items-start justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => router.push(`/incidents/${incident.id}`)}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium truncate text-foreground">
                          {typeof incident.description === "string"
                            ? incident.description
                            : incident.description
                              ? JSON.stringify(incident.description)
                              : "No description"}
                        </span>
                        {!incident.end_time && (
                          <Badge variant="secondary" className="text-xs bg-yellow-600 text-white">
                            Ongoing
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-foreground/70">
                        <span className={getConcernColor(incident.concern_score)}>
                          {(incident.concern_score * 100).toFixed(0)}% concern
                        </span>
                        <span>{formatDateTime(incident.start_time)}</span>
                      </div>
                    </div>
                    <Eye className="w-4 h-4 text-muted-foreground flex-shrink-0 ml-2" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">No recent incidents</div>
            )}
          </CardContent>
        </Card>

        {/* Recent Anomalies */}
        <Card className="bg-card border-border">
          <CardHeader className="flex flex-row items-center justify-between px-5 py-4">
            <div>
              <CardTitle className="text-base font-semibold text-card-foreground">Recent Anomalies</CardTitle>
              <CardDescription className="text-xs text-foreground/60">Latest detected anomalies</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/anomalies")}
              className="text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
            >
              View All
            </Button>
          </CardHeader>
          <CardContent className="px-5 pb-5">
            {recentAnomalies.length > 0 ? (
              <div className="space-y-2">
                {recentAnomalies.map((anomaly) => (
                  <div
                    key={anomaly.id}
                    className="flex items-start justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => router.push(`/anomalies/${anomaly.id}`)}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium truncate text-foreground">
                          {typeof anomaly.description === "string"
                            ? anomaly.description
                            : anomaly.description
                              ? JSON.stringify(anomaly.description)
                              : "No description"}
                        </span>
                        <Badge
                          variant="secondary"
                          className={`text-xs ${
                            anomaly.state === "confirmed"
                              ? "bg-orange-600"
                              : anomaly.state === "unknown" ||
                                  anomaly.state === "potential" ||
                                  anomaly.state === "forecasted"
                                ? "bg-blue-600"
                                : "bg-gray-600"
                          } text-white`}
                        >
                          {String(anomaly.state || "unknown")}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-foreground/70">
                        <span className="text-blue-400">
                          {anomaly.confidence_score ? (anomaly.confidence_score * 100).toFixed(0) : 0}% confidence
                        </span>
                        <span className={getConcernColor(anomaly.concern_score)}>
                          {(anomaly.concern_score * 100).toFixed(0)}% concern
                        </span>
                        <span>{formatDateTime(anomaly.start_time)}</span>
                      </div>
                    </div>
                    <Eye className="w-4 h-4 text-muted-foreground flex-shrink-0 ml-2" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">No recent anomalies</div>
            )}
          </CardContent>
        </Card>

        {/* Data Sources */}
        <Card className="bg-card border-border">
          <CardHeader className="flex flex-row items-center justify-between px-5 py-4">
            <div>
              <CardTitle className="text-base font-semibold text-card-foreground">Data Sources</CardTitle>
              <CardDescription className="text-xs text-foreground/60">Connected data sources</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/data-sources")}
              className="text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
            >
              View All
            </Button>
          </CardHeader>
          <CardContent className="px-5 pb-5">
            {dataSources.length > 0 ? (
              <div className="space-y-2">
                {dataSources.map((source) => (
                  <div
                    key={source.id}
                    className="flex items-start justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => router.push(`/data-sources/${source.id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <Server className="w-4 h-4 text-green-400" />
                      <div>
                        <div className="text-sm font-medium text-foreground">
                          {typeof source.name === "string"
                            ? source.name
                            : source.name
                              ? JSON.stringify(source.name)
                              : "Unnamed Source"}
                        </div>
                        <div className="text-xs text-foreground/70">
                          {typeof source.type === "string"
                            ? source.type
                            : source.type
                              ? JSON.stringify(source.type)
                              : "Unknown type"}
                        </div>
                      </div>
                    </div>
                    <Badge
                      variant="secondary"
                      className={`text-xs ${source.status === "active" || !source.status ? "bg-green-600" : "bg-gray-600"} text-white`}
                    >
                      {typeof source.status === "string"
                        ? source.status
                        : source.status
                          ? JSON.stringify(source.status)
                          : "active"}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No data sources configured</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3 bg-transparent border-border"
                  onClick={() => router.push("/data-sources/new")}
                >
                  <Plus className="w-3 h-3 mr-2" />
                  Add Data Source
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Monitored Entity Types */}
        <Card className="bg-card border-border">
          <CardHeader className="flex flex-row items-center justify-between px-5 py-4">
            <div>
              <CardTitle className="text-base font-semibold text-card-foreground">Monitored Entity Types</CardTitle>
              <CardDescription className="text-xs text-foreground/60">Configured entity types</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/monitored-entity-types")}
              className="text-xs text-blue-500 hover:text-blue-600 hover:bg-blue-500/10"
            >
              View All
            </Button>
          </CardHeader>
          <CardContent className="px-5 pb-5">
            {entityTypes.length > 0 ? (
              <div className="space-y-2">
                {entityTypes.map((entityType) => (
                  <div
                    key={entityType.id}
                    className="flex items-start justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => router.push(`/monitored-entity-types/${entityType.id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <Layers className="w-4 h-4 text-purple-400" />
                      <div>
                        <div className="text-sm font-medium text-foreground">
                          {typeof entityType.name === "string"
                            ? entityType.name
                            : entityType.name
                              ? JSON.stringify(entityType.name)
                              : "Unnamed Type"}
                        </div>
                        <div className="text-xs text-foreground/70 truncate max-w-xs">
                          {typeof entityType.description === "string"
                            ? entityType.description
                            : entityType.description
                              ? JSON.stringify(entityType.description)
                              : "No description"}
                        </div>
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Layers className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No entity types configured</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3 bg-transparent border-border"
                  onClick={() => router.push("/monitored-entity-types/new")}
                >
                  <Plus className="w-3 h-3 mr-2" />
                  Add Entity Type
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
