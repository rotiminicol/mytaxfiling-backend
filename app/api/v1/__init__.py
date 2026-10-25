from fastapi import APIRouter
from app.api.v1.endpoints import profiles, documents, invoices, receipts, admin

api_router = APIRouter()

api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(invoices.clients_router, prefix="/invoices/clients", tags=["invoices"])
api_router.include_router(invoices.templates_router, prefix="/invoices/templates", tags=["invoices"])
api_router.include_router(invoices.activities_router, prefix="/invoices/activities", tags=["invoices"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
