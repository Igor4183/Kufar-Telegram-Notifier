from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from services.models import Query
from utils.logger import Logger
from states.settings import AddQuery
from views.settings import update_menu

router = Router()


@router.callback_query(AddQuery.editing, F.data == "other_menu")
async def other_menu(callback: CallbackQuery, state: FSMContext):
    Logger.info(
        callback.from_user.id, "/settings -> add_query -> открыто меню 'прочее'"
    )
    await callback.answer()

    try:
        await state.update_data(current_menu="other")
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(other_menu): {error}")


@router.callback_query(AddQuery.editing, F.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    Logger.info(callback.from_user.id, "/settings -> add_query -> назад")
    await callback.answer()

    try:
        await state.update_data(current_menu="main")
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(back): {error}")


@router.callback_query(AddQuery.editing, F.data == "toggle_only_title")
async def toggle_only_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query: Query = data["query"]
        query.only_title_search = not query.only_title_search

        Logger.info(
            callback.from_user.id,
            f"/settings -> only-title-search -> {query.only_title_search}",
        )

        await state.update_data(query=query)
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(toggle_only_title): {error}")


@router.callback_query(AddQuery.editing, F.data == "toggle_only_with_photos")
async def toggle_only_with_photos(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query: Query = data["query"]
        query.only_with_photos = not query.only_with_photos

        Logger.info(
            callback.from_user.id,
            f"/settings -> only-with-photos -> {query.only_with_photos}",
        )

        await state.update_data(query=query)
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(toggle_only_with_photos): {error}")


@router.callback_query(AddQuery.editing, F.data == "toggle_only_with_videos")
async def toggle_only_with_videos(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query: Query = data["query"]
        query.only_with_videos = not query.only_with_videos

        Logger.info(
            callback.from_user.id,
            f"/settings -> only-with-videos -> {query.only_with_videos}",
        )

        await state.update_data(query=query)
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(toggle_only_with_videos): {error}")


@router.callback_query(AddQuery.editing, F.data == "toggle_condition")
async def toggle_condition(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query: Query = data["query"]

        if query.condition is None:
            query.condition = 1
        else:
            query.condition = (query.condition + 1) % 3
            if query.condition == 0:
                query.condition = None

        Logger.info(callback.from_user.id, f"(toggle_condition): {query.condition}")

        await state.update_data(query=query)
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(toggle_condition): {error}")


@router.callback_query(AddQuery.editing, F.data == "toggle_seller_type")
async def toggle_seller_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query: Query = data["query"]

        if query.seller_type is None:
            query.seller_type = 0
        else:
            query.seller_type = (query.seller_type + 1) % 3
            if query.seller_type == 2:
                query.seller_type = None

        Logger.info(
            callback.from_user.id,
            f"/settings -> seller-type -> {query.seller_type}",
        )

        await state.update_data(query=query)
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(toggle_seller_type): {error}")
