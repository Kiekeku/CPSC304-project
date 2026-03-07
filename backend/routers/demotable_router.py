from fastapi import APIRouter, Response, status

from models.schemas import InsertDemotableRequest, UpdateNameDemotableRequest
from services.demotable_service import (
    count_demotable,
    fetch_demotable,
    initiate_demotable,
    insert_demotable,
    test_oracle_connection,
    update_name_demotable,
)

router = APIRouter()


@router.get("/check-db-connection")
def check_db_connection() -> Response:
    is_connected = test_oracle_connection()
    return Response(
        content="Connected" if is_connected else "unable to connect",
        media_type="text/plain",
    )


@router.get("/demotable")
def get_demotable() -> dict:
    return {"data": fetch_demotable()}


@router.post("/initiate-demotable")
def post_initiate_demotable(response: Response) -> dict:
    success = initiate_demotable()
    if not success:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"success": success}


@router.post("/insert-demotable")
def post_insert_demotable(payload: InsertDemotableRequest, response: Response) -> dict:
    success = insert_demotable(payload.id, payload.name)
    if not success:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"success": success}


@router.post("/update-name-demotable")
def post_update_name_demotable(payload: UpdateNameDemotableRequest, response: Response) -> dict:
    success = update_name_demotable(payload.oldName, payload.newName)
    if not success:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"success": success}


@router.get("/count-demotable")
def get_count_demotable(response: Response) -> dict:
    table_count = count_demotable()
    success = table_count >= 0
    if not success:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return {"success": success, "count": table_count}
