from aiogram import Router

from .main import router as main_router
from .add_query import router as add_query_router
from .edit_query import router as edit_query_router

router = Router()

router.include_router(main_router)
router.include_router(add_query_router)
router.include_router(edit_query_router)
