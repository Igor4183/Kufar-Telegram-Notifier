from aiogram import Router

from .main import router as main_router
from .other import router as other_router
from .region import router as region_router
from .category import router as category_router

router = Router()

router.include_router(main_router)
router.include_router(other_router)
router.include_router(region_router)
router.include_router(category_router)
