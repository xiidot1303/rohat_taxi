from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)

from bot import CustomContext
from bot.resources.strings import Strings
from datetime import date, timedelta, datetime


def _words(update: Update | None = None, context: CustomContext | None = None):
    if context is not None and hasattr(context, "words"):
        return context.words

    user_id = (
        update.effective_chat.id
        if update and update.effective_chat
        else None
    )
    return Strings(user_id)


def _month_variable_name(month: int | str) -> str:
    month_names = {
        1: "january",
        2: "february",
        3: "march",
        4: "april",
        5: "may",
        6: "june",
        7: "july",
        8: "august",
        9: "september",
        10: "october",
        11: "november",
        12: "december",
    }
    return month_names[int(month)]


async def _inline_footer_buttons(
    buttons: list[list[InlineKeyboardButton]],
    *,
    update: Update | None = None,
    context: CustomContext | None = None,
    back=True,
    main_menu=True,
) -> list[list[InlineKeyboardButton]]:
    words = _words(update, context)
    footer_buttons = []

    if back:
        footer_buttons.append(
            InlineKeyboardButton(text=words.back, callback_data="back"),
        )
    if main_menu:
        footer_buttons.append(
            InlineKeyboardButton(
                text=words.main_menu,
                callback_data="main_menu",
            ),
        )

    if footer_buttons:
        buttons.append(footer_buttons)

    return buttons


async def select_lang_keyboard():
    return ReplyKeyboardMarkup(
        [Strings.uz_ru],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def settings_keyboard(context: CustomContext):
    return [
        [context.words.change_lang],
        [context.words.change_name],
        [context.words.change_phone_number],
        [context.words.change_city],
        [context.words.favorite_addresses],
        [context.words.main_menu],
    ]


async def build_keyboard(
    context: CustomContext,
    button_list,
    n_cols,
    back_button=True,
    main_menu_button=True,
):
    button_rows = [
        button_list[index:index + n_cols]
        for index in range(0, len(button_list), n_cols)
    ]
    footer_buttons = []

    if back_button:
        footer_buttons.append(context.words.back)
    if main_menu_button:
        footer_buttons.append(context.words.main_menu)
    if footer_buttons:
        button_rows.append(footer_buttons)

    return ReplyKeyboardMarkup(button_rows, resize_keyboard=True)


async def order_years_keyboard(
    update_or_years,
    years=None,
    *,
    update: Update | None = None,
    context: CustomContext | None = None,
):
    if years is None:
        years = update_or_years
    else:
        update = update_or_years

    inline_buttons = [
        InlineKeyboardButton(text=str(year), callback_data=f"year_{year}")
        for year in years
    ]
    button_rows = [
        inline_buttons[index:index + 3]
        for index in range(0, len(inline_buttons), 3)
    ]
    button_rows = await _inline_footer_buttons(
        button_rows,
        update=update,
        context=context,
        main_menu=False,
    )
    return InlineKeyboardMarkup(button_rows) if button_rows else None


async def order_months_keyboard(
    update_or_months,
    months=None,
    *,
    update: Update | None = None,
    context: CustomContext | None = None,
):
    if months is None:
        months = update_or_months
    else:
        update = update_or_months

    words = _words(update, context)
    inline_buttons = [
        InlineKeyboardButton(
            text=getattr(words, _month_variable_name(month)),
            callback_data=f"month_{month}",
        )
        for month in months
    ]
    button_rows = [
        inline_buttons[index:index + 3]
        for index in range(0, len(inline_buttons), 3)
    ]
    button_rows = await _inline_footer_buttons(
        button_rows,
        update=update,
        context=context,
    )
    return InlineKeyboardMarkup(button_rows) if button_rows else None


async def order_days_keyboard(
    update_or_days,
    days=None,
    *,
    update: Update | None = None,
    context: CustomContext | None = None,
):
    if days is None:
        days = update_or_days
    else:
        update = update_or_days

    inline_buttons = [
        InlineKeyboardButton(text=str(day), callback_data=f"day_{day}")
        for day in days
    ]
    button_rows = [
        inline_buttons[index:index + 4]
        for index in range(0, len(inline_buttons), 4)
    ]
    button_rows = await _inline_footer_buttons(
        button_rows,
        update=update,
        context=context,
    )
    return InlineKeyboardMarkup(button_rows) if button_rows else None


async def selecting_address_keyboard(
    update: Update | None = None,
    context: CustomContext | None = None,
    favorite_addresses_list: list[tuple[str, float, float]] | None = None,
):
    words = _words(update, context)
    inline_buttons = [
        [
            InlineKeyboardButton(
                text=words.search_addresses,
                switch_inline_query_current_chat="",
                style="success",
            ),
        ],
    ]
    if favorite_addresses_list:
        for address, lat, lon in favorite_addresses_list:
            inline_buttons.append([
                InlineKeyboardButton(
                    text=address,
                    callback_data=f"favorite_address-{lat}-{lon}",
                    style="primary",
                )
            ])
    inline_buttons = await _inline_footer_buttons(
        inline_buttons,
        update=update,
        context=context,
        back=False
    )
    return InlineKeyboardMarkup(inline_buttons)


async def request_location_keyboard(
    update: Update | None = None,
    context: CustomContext | None = None,
):
    words = _words(update, context)
    return ReplyKeyboardMarkup(
        [[KeyboardButton(words.send_location, request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def selecting_address_with_skip_keyboard(
    update: Update | None = None,
    context: CustomContext | None = None,
    favorite_addresses_list: list[tuple[str, float, float]] | None = None,
):
    words = _words(update, context)
    inline_buttons = [
        [
            InlineKeyboardButton(
                text=words.search_addresses,
                switch_inline_query_current_chat="",
                style="success",
            ),
        ]
    ]
    if favorite_addresses_list:
        for address, lat, lon in favorite_addresses_list:
            inline_buttons.append([
                InlineKeyboardButton(
                    text=address,
                    callback_data=f"favorite_address-{lat}-{lon}",
                    style="primary"
                )
            ])
    inline_buttons.append(
        [InlineKeyboardButton(text=words.skip, callback_data="skip", style="danger")]
    )
    inline_buttons = await _inline_footer_buttons(
        inline_buttons,
        update=update,
        context=context,
    )
    return InlineKeyboardMarkup(inline_buttons)


async def selecting_address_house_keyboard(
    update: Update | None = None,
    context: CustomContext | None = None,
):
    words = _words(update, context)
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text=words.back,
            callback_data="back"
        ),
        InlineKeyboardButton(
            text=words.skip,
            callback_data="skip"
        )
    ]])


async def confirm_order_keyboard(
    update: Update | None = None,
    context: CustomContext | None = None,
    pre_order_datetime: datetime | None = None
):
    words = _words(update, context)
    buttons = [
        [InlineKeyboardButton(text=words.confirm, callback_data="confirm")],
        [InlineKeyboardButton(text=words.change_point_a, callback_data="change_point_a")],
        [InlineKeyboardButton(text=words.change_point_b, callback_data="change_point_b")],
        [InlineKeyboardButton(text=words.change_pre_order_time, callback_data="change_pre_order_time")],
        [InlineKeyboardButton(text=words.main_menu, callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(buttons)


async def next_days_list_keyboard(context: CustomContext):
    today = date.today()
    buttons = [
        [InlineKeyboardButton(
            text=f"{(today + timedelta(days=i)).strftime('%d.%m.%Y')}",
            callback_data=f"pre_order_date-{(today + timedelta(days=i)).toordinal()}"
        )]
        for i in range(4)
    ]
    buttons.append([
        InlineKeyboardButton(
            text=context.words.back,
            callback_data="back"
        )
    ])
    return InlineKeyboardMarkup(buttons)