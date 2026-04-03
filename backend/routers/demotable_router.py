from fastapi import APIRouter, Response, status

from models.schemas import DocsQueryRunRequest, TableDeleteRequest, TableInsertRequest, TableUpdateRequest
from services.demotable_service import (
    delete_table_row,
    fetch_table_rows,
    get_table_metadata,
    initiate_demotable,
    insert_table_row,
    list_docs_queries,
    list_tables,
    run_docs_query,
    run_demotable_queries_preview,
    test_oracle_connection,
    update_table_row,
)

router = APIRouter()


@router.get("/check-db-connection")
def check_db_connection() -> Response:
    is_connected = test_oracle_connection()
    return Response(
        content="Connected" if is_connected else "unable to connect",
        media_type="text/plain",
    )


@router.get("/tables")
def get_tables() -> dict:
    return {"tables": list_tables()}


@router.post("/initiate-demotable")
def post_initiate_demotable(response: Response) -> dict:
    success = initiate_demotable()
    if not success:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"success": success}


@router.post("/run-demotable-queries")
def post_run_demotable_queries(response: Response) -> dict:
    try:
        return {"success": True, "results": run_demotable_queries_preview()}
    except Exception as exc:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"success": False, "message": str(exc), "results": []}


@router.get("/docs-queries")
def get_docs_queries() -> dict:
    return {"success": True, "queries": list_docs_queries()}


@router.post("/docs-run-query")
def post_docs_run_query(payload: DocsQueryRunRequest, response: Response) -> dict:
    try:
        return {"success": True, "result": run_docs_query(payload.queryId, payload.params)}
    except ValueError as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "message": str(exc)}
    except Exception as exc:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"success": False, "message": str(exc)}


@router.get("/table-metadata/{table_name}")
def get_metadata(table_name: str, response: Response) -> dict:
    metadata = get_table_metadata(table_name)
    if metadata is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"success": False, "message": "Table not found"}
    return {"success": True, "metadata": metadata}


@router.get("/table-rows/{table_name}")
def get_table_rows(table_name: str, response: Response) -> dict:
    metadata = get_table_metadata(table_name)
    if metadata is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"success": False, "message": "Table not found", "data": []}
    return {"success": True, "data": fetch_table_rows(table_name)}


@router.post("/table-insert")
def post_table_insert(payload: TableInsertRequest, response: Response) -> dict:
    success, message = insert_table_row(payload.tableName, payload.values)
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return {"success": success, "message": message}


@router.post("/table-update")
def post_table_update(payload: TableUpdateRequest, response: Response) -> dict:
    success, message = update_table_row(payload.tableName, payload.keys, payload.values)
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return {"success": success, "message": message}


@router.post("/table-delete")
def post_table_delete(payload: TableDeleteRequest, response: Response) -> dict:
    success, message = delete_table_row(payload.tableName, payload.keys)
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return {"success": success, "message": message}
