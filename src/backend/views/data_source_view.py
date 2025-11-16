from typing import List
from sqlmodel import Session, select, and_
from data_models.telemetry import db, api, api_request


class DataSourceView:

    @staticmethod
    def retrieve(
        data_source_request: api_request.DataSourceRequest = None,
        db_session: Session = None
    ) -> api.DataSource | List[api.DataSource] | None:

        """
        Retrieve data sources from the database based on the provided
        criteria in data_source_request or data_source_name.

        If the ID is provided, it only looks for that specific data source.
        If the ID is not provided, it tries to match based on all the
        other fields.
        """
        query = select(db.DataSource)

        if data_source_request:
            if data_source_request.id:
                query = query.where(db.DataSource.id == data_source_request.id)
            else:
                if data_source_request.name:
                    query = query.where(
                        db.DataSource.name == data_source_request.name)
                if data_source_request.description:
                    query = query.where(
                        db.DataSource.description ==
                        data_source_request.description)
                if data_source_request.type:
                    db_type = data_source_request.type.value
                    db_version = data_source_request.type.version
                    query = query.where(
                        db.DataSource.database_type == db_type)
                    query = query.where(
                        db.DataSource.database_version == db_version)
                if data_source_request.end_point:
                    if data_source_request.end_point.host:
                        query = query.where(
                            db.DataSource.end_point.has(
                                db.Endpoint.host ==
                                data_source_request.end_point.host))
                    if data_source_request.end_point.port:
                        query = query.where(
                            db.DataSource.end_point.has(
                                db.Endpoint.port ==
                                data_source_request.end_point.port))

        results = db_session.exec(query).all()
        results = [
            api.DataSource(
                id=r.id,
                name=r.name,
                description=r.description,
                type=api.DataSourceType(
                    database=r.database_type,
                    version=r.database_version
                ),
                end_point=api.Endpoint(
                    url=r.end_point_url,
                    metadata=r.end_point_metadata
                )
            )
            for r in results
        ] if results else []
        if results is None:
            return None
        else:
            if data_source_request.id and len(results) == 1:
                return results[0]
            return results

    @staticmethod
    def create(data_source: api.DataSource,
               db_session: Session) -> db.DataSource:
        """
        Create a new data source in the database if it does not exist.
        """
        # Compose the type string from the API model
        db_type = data_source.type.database.value
        db_version = data_source.type.version
        ds = db_session.exec(select(db.DataSource).where(
            and_(
                db.DataSource.name == data_source.name,
                db.DataSource.database_type == db_type,
                db.DataSource.database_version == db_version
            )
        )).first()

        if not ds:
            ds = db.DataSource(
                name=data_source.name,
                description=data_source.description,
                database_type=db_type,
                database_version=data_source.type.version,
                end_point_url=data_source.end_point.url,
                end_point_metadata=data_source.end_point.metadata
            )
            db_session.add(ds)
            db_session.commit()
            db_session.refresh(ds)
        return ds

    @staticmethod
    def update(
            updated_data_source: api.DataSource,
            db_session: Session) \
            -> db.DataSource | None:
        """
        Update an existing data source in the database.
        Finds by id, updates fields, commits, and returns the updated object.
        Returns None if not found.
        """
        if not updated_data_source.id:
            return None
        ds = db_session.get(db.DataSource, updated_data_source.id)
        if not ds:
            return None

        # Update simple fields
        for field in ["name", "description"]:
            value = getattr(updated_data_source, field, None)
            if value is not None:
                setattr(ds, field, value)

        # Update type fields
        if updated_data_source.type:
            ds.database_type = updated_data_source.type.database.value
            ds.database_version = updated_data_source.type.version

        # Update endpoint fields
        if updated_data_source.end_point:
            ds.end_point_url = updated_data_source.end_point.url
            ds.end_point_metadata = updated_data_source.end_point.metadata

        db_session.commit()
        db_session.refresh(ds)
        return ds
