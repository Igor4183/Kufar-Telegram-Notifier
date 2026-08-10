from math import ceil

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from services.filters_manager import FiltersManager
from utils.logger import Logger
from states.settings import AddQuery
from views.settings import update_menu

router = Router()
filters_manager = FiltersManager()


@router.callback_query(AddQuery.editing, F.data == "edit_category")
async def edit_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    categories = filters_manager.get_categories()
    if not categories:
        Logger.error(callback.from_user.id, "(edit_category): список категорий пуст")
        await callback.message.edit_text("❌ Не удалось получить список категорий.")
        return

    await state.update_data(
        category_page=0,
        selected_category=None,
        selected_sub_category=None,
    )
    await update_categories_menu(callback, state)


async def update_categories_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    categories = filters_manager.get_categories()
    if not categories:
        Logger.error(
            callback.from_user.id, "(update_categories_menu): список категорий пуст"
        )
        return

    page = data.get("category_page", 0)
    items_per_page = 8
    total_pages = ceil(len(categories) / items_per_page)
    start = page * items_per_page
    end = start + items_per_page
    page_categories = categories[start:end]

    builder = InlineKeyboardBuilder()

    for category in page_categories:
        builder.button(
            text=category["name"], callback_data=f"select_category:{category['slug']}"
        )
    builder.adjust(1)
    keyboard = builder.export()

    if total_pages > 1:
        previous_button = (
            InlineKeyboardButton(text="◀️", callback_data=f"category_page:{page - 1}")
            if page > 0
            else InlineKeyboardButton(text=" ", callback_data="category_page:current")
        )
        next_button = (
            InlineKeyboardButton(text="▶️", callback_data=f"category_page:{page + 1}")
            if page < total_pages - 1
            else InlineKeyboardButton(text=" ", callback_data="category_page:current")
        )
        keyboard.append(
            [
                previous_button,
                InlineKeyboardButton(
                    text=f"{page + 1}/{total_pages}",
                    callback_data="category_page:current",
                ),
                next_button,
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🗑 Очистить настройки категорий",
                callback_data="clear_category",
            )
        ]
    )
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])

    await state.update_data(current_menu="category")
    await callback.message.edit_text(  # type: ignore
        "📂 Выберите категорию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(AddQuery.editing, F.data.startswith("category_page:"))
async def category_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        page = callback.data.split(":", 1)[1]  # type: ignore
        if page == "current":
            return
        page = int(page)

        await state.update_data(category_page=page)
        await update_categories_menu(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(category_page): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data.startswith("select_category:"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        slug = callback.data.split(":", 1)[1]  # type: ignore
        category = filters_manager.get_category(slug)
        if category is None:
            Logger.error(
                callback.from_user.id,
                f"(select_category): категория '{slug}' не найдена",
            )
            return

        sub_categories = category.get("subcategories", [])
        await state.update_data(
            selected_category=category["id"],
            selected_category_slug=slug,
            selected_sub_category=None,
            sub_categories_page=0,
        )
        if not sub_categories:
            await update_sub_categories_menu(callback, state)
            return
        await update_sub_categories_menu(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(select_category): ошибка: {error}")


async def update_sub_categories_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_category_slug = data.get("selected_category_slug")
    if selected_category_slug is None:
        Logger.error(
            callback.from_user.id,
            "(update_sub_categories_menu): selected_category_slug "
            "отсутствует в состоянии",
        )
        return

    category = filters_manager.get_category(selected_category_slug)
    if category is None:
        Logger.error(
            callback.from_user.id, "(update_sub_categories_menu): категория не найдена"
        )
        return

    sub_categories = category.get("subcategories", [])
    page = data.get("sub_categories_page", 0)

    if not sub_categories:
        await callback.message.edit_text(  # type: ignore
            f"📂 {category['name']}\n\n" "У этой категории нет подкатегорий.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Сохранить категорию",
                            callback_data="save_category",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="◀️ Назад",
                            callback_data="back_to_categories",
                        )
                    ],
                ]
            ),
        )
        return

    items_per_page = 8
    total_pages = ceil(len(sub_categories) / items_per_page)
    start = page * items_per_page
    end = start + items_per_page
    page_sub_categories = sub_categories[start:end]

    builder = InlineKeyboardBuilder()

    for sub_category in page_sub_categories:
        builder.button(
            text=sub_category["name"],
            callback_data=f"select_sub_category:{sub_category['slug']}",
        )

    builder.adjust(1)
    keyboard = builder.export()

    if total_pages > 1:
        previous_button = (
            InlineKeyboardButton(
                text="◀️", callback_data=f"sub_category_page:{page - 1}"
            )
            if page > 0
            else InlineKeyboardButton(
                text=" ", callback_data="sub_category_page:current"
            )
        )
        next_button = (
            InlineKeyboardButton(
                text="▶️", callback_data=f"sub_category_page:{page + 1}"
            )
            if page < total_pages - 1
            else InlineKeyboardButton(
                text=" ", callback_data="sub_category_page:current"
            )
        )
        keyboard.append(
            [
                previous_button,
                InlineKeyboardButton(
                    text=f"{page + 1}/{total_pages}",
                    callback_data="sub_category_page:current",
                ),
                next_button,
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="Все подкатегории",
                callback_data="all_sub_categories",
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="back_to_categories",
            )
        ]
    )

    await state.update_data(current_menu="sub_category")
    await callback.message.edit_text(  # type: ignore
        f"📂 {category['name']}\n\n" "Выберите подкатегорию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


def sub_categories_keyboard(category_has_sub_categories: bool):
    builder = InlineKeyboardBuilder()
    if category_has_sub_categories:
        builder.button(text="Все подкатегории", callback_data="all_sub_categories")
    builder.button(text="◀️ Назад", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(AddQuery.editing, F.data.startswith("sub_category_page:"))
async def sub_category_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        page = callback.data.split(":", 1)[1]  # type: ignore
        if page == "current":
            return
        page = int(page)
        await state.update_data(sub_categories_page=page)
        await update_sub_categories_menu(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(sub_category_page): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data.startswith("select_sub_category:"))
async def select_sub_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        slug = callback.data.split(":", 1)[1]  # type: ignore
        data = await state.get_data()
        selected_category_slug = data.get("selected_category_slug")

        if selected_category_slug is None:
            Logger.error(
                callback.from_user.id,
                "(select_sub_category): selected_category_slug отсутствует в состоянии",
            )
            return
        category = filters_manager.get_category(selected_category_slug)
        if category is None:
            Logger.error(
                callback.from_user.id, "(select_sub_category): категория не найдена"
            )
            return

        sub_category = next(
            (
                sub_category
                for sub_category in category.get("subcategories", [])
                if sub_category["slug"] == slug
            ),
            None,
        )
        if sub_category is None:
            Logger.error(
                callback.from_user.id,
                f"(select_sub_category): подкатегория '{slug}' не найдена",
            )
            return

        await state.update_data(selected_sub_category=sub_category["id"])
        await save_category(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(select_sub_category): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data == "all_sub_categories")
async def all_sub_categories(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        selected_category = data.get("selected_category")

        if selected_category is None:
            Logger.error(
                callback.from_user.id,
                "(all_sub_categories): selected_category " "отсутствует в состоянии",
            )
            return

        await state.update_data(selected_sub_category=None)
        await save_category(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(all_sub_categories): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        await state.update_data(
            selected_category_slug=None,
            selected_sub_category=None,
            sub_categories_page=0,
        )
        await update_categories_menu(callback, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(back_to_categories): ошибка: {error}")


@router.callback_query(AddQuery.editing, F.data == "clear_category")
async def clear_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    try:
        data = await state.get_data()
        query = data.get("query")
        if query is None:
            Logger.error(
                callback.from_user.id, "(clear_category): query отсутствует в состоянии"
            )
            return

        query.pop("category", None)
        query.pop("sub-category", None)

        await state.update_data(
            query=query,
            selected_category=None,
            selected_category_slug=None,
            selected_sub_category=None,
            category_page=0,
            sub_categories_page=0,
            current_menu="main",
        )
        Logger.info(
            callback.from_user.id, "/settings -> add_query -> категории очищены"
        )
        await update_menu(callback.bot, state)
    except Exception as error:
        Logger.error(callback.from_user.id, f"(clear_category): ошибка: {error}")


async def apply_category_selection(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    query = data.get("query")
    if query is None:
        Logger.error(
            callback.from_user.id,
            "(apply_category_selection): query отсутствует " "в состоянии",
        )
        return
    selected_category = data.get("selected_category")
    selected_sub_category = data.get("selected_sub_category")
    if selected_category is None:
        Logger.error(
            callback.from_user.id,
            "(apply_category_selection): selected_category " "отсутствует в состоянии",
        )
        return

    query["category"] = selected_category
    if selected_sub_category is not None:
        query["sub-category"] = selected_sub_category
    else:
        query.pop("sub-category", None)
    await state.update_data(
        query=query,
        current_menu="main",
    )
    await update_menu(callback.bot, state)


@router.callback_query(AddQuery.editing, F.data == "save_category")
async def save_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await apply_category_selection(callback, state)
        Logger.info(
            callback.from_user.id, "/settings -> add_query -> категория сохранена"
        )
    except Exception as error:
        Logger.error(callback.from_user.id, f"(save_category): ошибка: {error}")
