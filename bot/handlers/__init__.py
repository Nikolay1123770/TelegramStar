from bot.handlers.start import router as start_router
from bot.handlers.purchase import router as purchase_router
from bot.handlers.support import router as support_router

routers = [
    start_router,
    purchase_router,
    support_router,
]
