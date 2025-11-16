import uuid
from sqlmodel import Session, select
from data_models.label_store import db as label_store_db
from data_models.telemetry import db as telemetry_db


endpoint = "api/v1/telemetry/anomaly"


class TelemetryView:

    @staticmethod
    def retrieve(
            anomaly_ids: list[uuid.UUID],
            db_session: Session) -> list[]:
        """
        Retrieve telemetry from influxdb based on the input Anomaly IDs
        """




        return db_session.exec(select(db.Telemetry)).all()



"""
Examples of queries to implement

from(bucket: "network_telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "interface")
  |> filter(fn: (r) => r["_field"] == "active_opens")
  |> filter(fn: (r) => r["vpn-id"] == "machine-1-6")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")

from(bucket: "network_telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "bmp")
  |> filter(fn: (r) => r["_field"] == "XXX")
  |> filter(fn: (r) => r["machine-name"] == "machine-1-6")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")

from(bucket: "network_telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "ipfix")
  |> filter(fn: (r) => r["_field"] == "octectDeltaCount")
  |> filter(fn: (r) => r["machine-name"] == "machine-1-6")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
"""