from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, purchase_orders, workflows, confirmations, outbounds, inventory, reports, notifications, test_import
# 暂时注释掉PDA模块，等数据库迁移完成后再启用
# from app.api.api_v1.endpoints import pda

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(purchase_orders.router, prefix="/purchase", tags=["purchase_orders"])
api_router.include_router(workflows.router, prefix="/workflow", tags=["workflows"])
api_router.include_router(confirmations.router, prefix="/confirmation", tags=["confirmations"])
api_router.include_router(outbounds.router, prefix="/outbound", tags=["outbounds"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(test_import.router, prefix="/test", tags=["test"])
# 暂时注释掉PDA路由，等数据库迁移完成后再启用
# api_router.include_router(pda.router, prefix="/pda", tags=["pda"])
