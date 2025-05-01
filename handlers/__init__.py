from aiogram import Router
router = Router()

from .upload_documents import router as upload_router

router.include_router(upload_router)
