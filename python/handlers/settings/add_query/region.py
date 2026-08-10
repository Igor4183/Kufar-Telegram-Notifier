from math import ceil

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from services.filters_manager import FiltersManager
from utils.logger import Logger
from states.settings import AddQuery
from keyboards.add_query import areas_keyboard
from views.settings import update_menu

router = Router()
filters_manager = FiltersManager()


@router.callback_query(AddQuery.editing, F.data == "edit_region")
async def edit_region(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    data = await state.get_data()
    query = data.get("query")
    if query is None:
        Logger.error(
            callback.from_user.id,
            "Не удалось открыть выбор области: query отсутствует в состоянии",
        )
        await callback.message.edit_text("❌ Не удалось открыть выбор области.")
        return
    regions = filters_manager.get_regions()

    if not regions:
        Logger.error(
            callback.from_user.id,
            "Не удалось открыть выбор области: список регионов пуст",
        )
        await callback.message.edit_text("❌ Не удалось получить список регионов.")
        return

    builder = InlineKeyboardBuilder()
    for region in regions:
        builder.button(
            text=region["name"], callback_data=f"select_region:{region['slug']}"
        )
    builder.button(text="🗑 Очистить регион", callback_data="clear_region")
    builder.button(text="◀️ Назад", callback_data="back")
    builder.adjust(1)

    await state.update_data(current_menu="region")
    await callback.message.edit_text(
        "🌍 Выберите область:",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(AddQuery.editing, F.data.startswith("select_region:"))
async def select_region(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        slug = callback.data.split(":", 1)[1]  # type: ignore
        region = filters_manager.get_region(slug)
        if region is None:
            Logger.error(
                callback.from_user.id, f"(select_region): регион '{slug}' не найден"
            )
            return

        areas = region.get("areas", [])
        await state.update_data(
            selected_region=slug,
            selected_areas=[],
            areas_page=0,
        )

        if not areas:
            await apply_region_selection(callback, state)
            return

        total_pages = ceil(len(areas) / 8)

        await callback.message.edit_text(  # type: ignore
            f"📍 {region['name']}\n\n"
            "Выберите районы или города.\n"
            "Можно выбрать несколько:",
            reply_markup=areas_keyboard(areas, 0, [], total_pages),
        )
    except Exception as error:
        Logger.error(callback.from_user.id, f"(select_region): ошибка: {error}")


async def update_areas_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    selected_region = data.get("selected_region")
    selected_areas = data.get("selected_areas", [])
    page = data.get("areas_page", 0)

    if selected_region is None:
        Logger.error(
            callback.from_user.id,
            "(update_areas_menu): selected_region отсутствует в состоянии",
        )
        return

    region = filters_manager.get_region(selected_region)

    if region is None:
        Logger.error(
            callback.from_user.id,
            f"(update_areas_menu): регион '{selected_region}' не найден",
        )
        return

    areas = region.get("areas", [])
    total_pages = ceil(len(areas) / 8)

    await callback.message.edit_text(  # type: ignore
        f"📍 {region['name']}\n\n"
        "Выберите районы или города.\n"
        "Можно выбрать несколько:",
        reply_markup=areas_keyboard(areas, page, selected_areas, total_pages),
    )


@router.callback_query(AddQuery.editing, F.data.startswith("area:"))
async def toggle_area(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        if callback.data is None:
            Logger.error(
                callback.from_user.id, "(toggle_area): callback_data отсутствует"
            )
            return

        slug = callback.data.split(":", 1)[1]
        data = await state.get_data()
        selected_region = data.get("selected_region")

        if selected_region is None:
            Logger.error(
                callback.from_user.id,
                "(toggle_area): selected_region отсутствует в состоянии",
            )
            return

        region = filters_manager.get_region(selected_region)

        if region is None:
            Logger.error(
                callback.from_user.id,
                f"(toggle_area): регион '{selected_region}' не найден",
            )
            return

        area = next(
            (area for area in region.get("areas", []) if area["slug"] == slug), None
        )

        if area is None:
            Logger.error(
                callback.from_user.id,
                f"(toggle_area): район '{slug}' не найден "
                f"в регионе '{selected_region}'",
            )
            return

        selected_areas = data.get("selected_areas", [])
        area_id = area["id"]

        if area_id in selected_areas:
            selected_areas.remove(area_id)
        else:
            selected_areas.append(area_id)

        await state.update_data(selected_areas=selected_areas)
        await update_areas_menu(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(toggle_area): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data.startswith("areas_page:"))
async def areas_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        page = callback.data.split(":", 1)[1]  # type: ignore
        if page == "current":
            return

        page = int(page)
        await state.update_data(areas_page=page)
        await update_areas_menu(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(areas_page): ошибка: {error}")


async def apply_region_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    query = data.get("query")

    if query is None:
        Logger.error(
            callback.from_user.id,
            "(apply_region_selection): query отсутствует в состоянии",
        )
        return

    selected_region = data.get("selected_region")
    selected_areas = data.get("selected_areas", [])

    if selected_region is None:
        Logger.error(
            callback.from_user.id,
            "(apply_region_selection): selected_region отсутствует в состоянии",
        )
        return

    region = filters_manager.get_region(selected_region)

    if region is None:
        Logger.error(
            callback.from_user.id,
            f"(apply_region_selection): регион '{selected_region}' не найден",
        )
        return

    query["region"] = region["id"]

    if selected_areas:
        query["areas"] = selected_areas.copy()
    else:
        query.pop("areas", None)

    await state.update_data(query=query, current_menu="main")
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "clear_region")
async def clear_region(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query = data.get("query")
        if query is None:
            Logger.error(
                callback.from_user.id, "(clear_region): query отсутствует в состоянии"
            )
            return
        query.pop("region", None)
        query.pop("areas", None)

        await state.update_data(
            query=query,
            selected_region=None,
            selected_areas=[],
            areas_page=0,
            current_menu="main",
        )
        Logger.info(callback.from_user.id, "/settings -> add_query -> регион очищен")
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(clear_region): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data == "areas_all")
async def areas_all(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        await state.update_data(selected_areas=[])
        await apply_region_selection(callback, state)
        Logger.info(
            callback.from_user.id, "/settings -> add_query -> выбрана вся область"
        )
    except Exception as error:
        Logger.error(callback.from_user.id, f"(areas_all): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data == "back_to_regions")
async def back_to_regions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        regions = filters_manager.get_regions()
        builder = InlineKeyboardBuilder()

        for region in regions:
            builder.button(
                text=region["name"], callback_data=f"select_region:{region['slug']}"
            )
        builder.button(text="🗑 Очистить регион", callback_data="clear_region")
        builder.button(text="◀️ Назад", callback_data="back")
        builder.adjust(1)

        await state.update_data(
            selected_region=None,
            selected_areas=[],
            areas_page=0,
        )

        await callback.message.edit_text(  # type: ignore
            "🌍 Выберите область:", reply_markup=builder.as_markup()
        )
    except Exception as error:
        Logger.error(callback.from_user.id, f"(back_to_regions): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data == "save_region")
async def save_region(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        await apply_region_selection(callback, state)
        Logger.info(callback.from_user.id, "/settings -> add_query -> регион сохранён")
    except Exception as error:
        Logger.error(callback.from_user.id, f"(save_region): ошибка: {error}")
