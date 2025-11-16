// Centralized API endpoint references
/// <reference types="node" />

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const ENDPOINTS = {
  RELEVANT_STATE: `/api/v1/label-store/relevant-state`,
  RELEVANT_STATE_TELEMETRY: `/api/v1/telemetry/data/relevant-state`,
  ANOMALY: `/api/v1/label-store/anomaly`,
  ANNOTATOR: `/api/v1/annotator`,
  DATA_SOURCE: `/api/v1/telemetry/data-source`,
  MONITORED_ENTITY: `/api/v1/telemetry/monitored-entity-type`,
  EXISTING_MONITORED_ENTITY_TYPES: `/api/v1/telemetry/router_existing_services`,
  SERVICE: `/api/v1/label-store/service`,
  TELEMETRY_QUERY: `/api/v1/telemetry/data/query`,
}
