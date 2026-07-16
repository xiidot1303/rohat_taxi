class Strings:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def __getattribute__(self, key: str):
        if result := object.__getattribute__(self, key):
            if isinstance(result, list):
                from bot.services.redis_service import get_user_lang
                user_id = object.__getattribute__(self, "user_id")
                user_lang_code = get_user_lang(user_id)
                return result[user_lang_code]
            else:
                return result
        else:
            return key

    hello = (
        "🤖 Xush kelibsiz!\n Bot tilini tanlang  🌎 \n\n "
        "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        "    👋 Добро пожаловать \n "
        "\U0001F1FA\U0001F1FF Выберите язык бота \U0001F1F7\U0001F1FA"
    )
    added_group = "Чат успешно добавлена ✅"
    uz_ru = ["UZ 🇺🇿", "RU 🇷🇺"]
    main_menu = ["🏠 Asosiy menyu", "🏠 Главное меню"]
    change_lang = [
        "\U0001F1FA\U0001F1FF \U0001F1F7\U0001F1FA Tilni o'zgartirish",
        "\U0001F1FA\U0001F1FF \U0001F1F7\U0001F1FA Сменить язык",
    ]
    select_lang = [""" Tilni tanlang """, """Выберите язык бота """]
    type_name = ["""Ismingizni kiriting """, """Введите ваше имя """]
    send_number = [
        """Telefon raqamingizni yuboring """,
        """Оставьте свой номер телефона """,
    ]
    select_city = ["""Shaharni tanlang""", """Выберите город"""]
    leave_number = ["Telefon raqamni yuborish", "Оставить номер телефона"]
    back = ["""🔙 Ortga""", """🔙 Назад"""]
    next_step = ["""Davom etish ➡️""", """Далее ➡️"""]
    seller = ["""Sotuvchi 🛍""", """Продавцам 🛍"""]
    buyer = ["""Xaridor 💵""", """Покупателям 💵"""]
    settings = ["""Sozlamalar ⚙️""", """Настройки ⚙️"""]
    language_change = [
        """Tilni o\'zgartirish 🇺🇿🇷🇺""",
        """Смена языка 🇺🇿🇷🇺""",
    ]
    change_phone_number = [
        """📞 Telefon raqamni o\'zgartirish""",
        """📞 Смена номера телефона""",
    ]
    change_name = ["""👤 Ismni o\'zgartirish""", """👤 Смени имени"""]
    settings_desc = ["""Sozlamalar ⚙️""", """Настройки ⚙️"""]
    your_phone_number = [
        """📌 Sizning telefon raqamingiz: [] 📌""",
        """📌 Ваш номер телефона: [] 📌""",
    ]
    send_new_phone_number = [
        (
            """Yangi telefon raqamingizni yuboring!\n"""
            """<i>Jarayonni bekor qilish uchun """
            """"🔙 Ortga" tugmasini bosing.</i>"""
        ),
        (
            """Отправьте свой новый номер телефона!\n"""
            """<i>Нажмите кнопку "🔙 Назад", """
            """чтобы отменить процесс.</i>"""
        ),
    ]
    number_is_logged = [
        (
            "Bunday raqam bilan ro'yxatdan o'tilgan, "
            "boshqa telefon raqam kiriting"
        ),
        "Этот номер уже зарегистрирован. Введите другой номер",
    ]
    number_is_incorrect = [
        "Telefon raqami noto'g'ri kiritildi. Qaytadan yuboring",
        "Номер телефона введен неверно. Отправьте заново",
    ]
    incorrect_city = [
        "Bunday shahar topilmadi. Ro'yxatdan birini tanlang",
        "Такой город не найден. Выберите один из списка",
    ]
    changed_your_phone_number = [
        """Sizning telefon raqamingiz muvaffaqiyatli o\'zgartirildi! ♻️""",
        """Ваш номер телефона успешно изменен! ♻️""",
    ]
    your_name = ["""Sizning ismingiz: """, """Ваше имя: """]
    send_new_name = [
        (
            """Ismingizni o'zgartirish uchun, yangi ism kiriting:\n"""
            """<i>Jarayonni bekor qilish uchun """
            """"🔙 Ortga" tugmasini bosing.</i>"""
        ),
        (
            """Чтобы изменить свое имя, введите новое:\n"""
            """<i>Нажмите кнопку "🔙 Назад", """
            """чтобы отменить процесс.</i>"""
        ),
    ]
    changed_your_name = [
        """Sizning ismingiz muvaffaqiyatli o'zgartirildi!""",
        """Ваше имя успешно изменено!""",
    ]


    cheque_info = [
        "{car_phone}\n{car_firstname}\n{brand} {model} {color}\n{autonum}\n{amount}", 
        "{car_phone}\n{car_firstname}\n{brand} {model} {color}\n{autonum}\n{amount}", 
        ]

    order_history = ["Buyurtmalar tarixi 📑", "История заказов 📑"]

    select_year_of_order = [
        "🗓 Buyurtma yilini tanlang", 
        "🗓 Выберите год заказа"
        ]
    
    select_month_of_order = [
        "📆 Buyurtma oyini tanlang\n\n<i>Yil: {}</i>", 
        "📆 Выберите месяц заказа\n\n<i>Год: {}</i>"
        ]

    select_day_of_order = [
        "📅 Buyurtma kunini tanlang\n\n<i>Yil: {}\nOy: {}</i>", 
        "📅 Выберите день заказа\n\n<i>Год: {}\nМесяц: {}</i>"
        ]

    not_available_orders_yet = [
        "🆓 Hozircha hech qanday buyurtma mavjud emas", 
        "🆓 Пока нет доступных заказов"
        ]

    january = ["Yanvar", "Январь"]

    february = ["Fevral", "Февраль"]

    march = ["Mart", "Март"]
    
    april = ["Aprel", "Апрель"]

    may = ["May", "Май"]

    june = ["Iyun", "Июнь"]

    july = ["Iyul", "Июль"]

    august = ["Avgust", "Август"]

    september = ["Sentabr", "Сентябрь"]

    october = ["Oktabr", "Октябрь"]

    november = ["Noyabr", "Ноябрь"]

    december = ["Dekabr", "Декабрь"]

    let_order = ["Buyurtma berish 🚖", "Заказать 🚖"]

    order = ["Buyurtma", "Заказ"]

    # "select address or location": [
    #     "🔘 <u>Manzil tanlash 🔎</u> tugamasini bosing va manzilni kiriting, natijani bosing\n<b>YOKI</b>\n📍 Lokatsiya yuboring", 
    #     "🔘 Нажмите <u>Выбрать адрес 🔎</u> и введите адрес, нажмите результат\n<b>ИЛИ</b>\n📍 Отправьте локация"
    # ]

    select_address_or_location = [
        "<b>🚖 Jo'nab ketish manzilini tanlang</b>",
        "<b>🚖 Выберите адрес подачи</b>"
    ]

    search_addresses = ["Manzil tanlash 🔎", "Выбрать адрес 🔎"]

    send_location = ["📍 Lokatsiya yuborish", "📍 Отправить местоположение"]

    select_point_a = ["<b>🔎</b>", "<b>🔎</b>"]

    select_point_b = ["<b>🅱️ Borish manzilingizni kiriting</b>", "<b>🅱️ Выберите точку поездки</b>"]

    city = ["Shahar", "Город"]

    not_found = ["🙅‍♂️ Mavjud emas", "🙅‍♂️ Не найдено"]

    type_house_number = ["🏘 Uy raqamini kiriting", "🏘 Введите номер дома"]

    point_a = ["🏠 Qayerdan", "🏠 Откуда"]
    
    point_b = ["🏡 Qayerga", "🏡 Куда"]

    confirm_order = [
        "☑️ Ma'lumotlarni tasdiqlang", 
        "☑️ Подтвердите информацию"
        ]

    confirm = ["✅ Tasdiqlash", "✅ Подтвердить"]

    skip = ["O'tkazib yuborish", "Пропустить"]

    change_point_a = ["🅰️ Manzilni o'zgartirish", "Изменить адрес 🅰️"]

    change_point_b = ["🅱️ Borish manzilingizni o'zgartirish", "Изменить точку поездки 🅱️"]

    price = ["💰 Narx", "💰 Цена"]

    distance = ["🚕 Masofa", "🚕 Дистанция"]

    invalid_location = ["⛔️ Lokatsiya xato", "⛔️ Недопустимое местоположение"]

    cancel_order = ["❌ Buyurtmani bekor qilish", "❌ Отменить заказ"]

    order_in_process = ["🆗 Buyurtma jarayonda", "🆗 Заказ в процессе"]

    your_order_is_in_moderation = [
        "✔️ Buyurtmangiz moderatsiyada", 
        "✔️ Ваш заказ на модерации"
        ]

    car = ["🚖 Mashina", "🚖 Машина"]

    number = ["🔢 Raqami", "🔢 Номер"]

    arrival_time = ["⌛️ Kelish vaqti", "⌛️ Время подъезда"]

    minute = ["minut", "минут"]

    driver = ["🚕 Haydovchi", "🚕 Водитель"]

    driver_is_here = [
        "❕ Haydovchi yetib keldi", 
        "❕Водитель прибыл"
        ]

    order_is_in_execution = [
        "✅ Buyurtma amalga oshmoqda", 
        "✅ Заказ находится в исполнении"
        ]

    your_order_is_cancelled = [
        "❌ Buyurtmangiz bekor qilindi", 
        "❌ Ваш заказ отменен"]

    amount = ["💵 Miqdor", "💵 Сумма"]

    meter = ["m", "м"]

    standtime = ["🅿️ Vaqt", "🅿️ Стоянка"]

    min = ["min.", "мин."]

    sek = ["sek.", "сек."]

    waittime = ["🚖 Kutish vaqti", "🚖 Время ожидания"]

    driver_info = ["👨‍✈️ Haydovchi haqida ma'lumot", "👨‍✈️ Информация о водителе"]
    
    driver_name = ["👨‍✈️ Haydovchi ismi", "👨‍✈️ Имя  водителя"]

    name = ["Ism", "Имя"]

    phone = ["📱 Telefon", "📱 Телефон"]

    loading = ["Yuklanmoqda... ⏳", "Загрузка... ⏳"]

    balance = ["Bonus 💰", "Бонусы 💰"]

    your_balance = [
        "Sizda <b>{}</b> so'm bonus mavjud 💳", 
        "Ваш бонус {} сум 💳"]

    finish_text = [
        "🏁 Sizning buyurtmangiz yakunlandi", 
        "🏁 Ваш заказ выполнен"]

    leave_feedback = [
        "Fikr qoldirish 📨", 
        "Оставить отзыв 📨"
        ]

    write_your_feedback = [
        "Оставляйте свои комментарии и отзывы 📝", 
        "Оставляйте свои комментарии и отзывы 📝"
        ]

    your_feedback_accepted = [
        "Sizning murojaatingiz qabul qilindi ✅.\nOperator javobini kuting 👩‍💻", 
        "Ваш отзыв принят ✅.\nДождитесь ответа оператора 👩‍💻"
        ]

    select_city = [
        "Shaharni tanlang", 
        "Выберите город"
        ]

    incorrect_city = [
        "Noto'g'ri shahar. Belgilangan shaharlardan birini tanlang", 
        "Неправильный город. Выберите один из указанных городов"
        ]

    change_city = [
        "🏙 Shaharni o'zgartirish", 
        "🏙 Изменить город"
        ]

    change_favorite_addresses = [
        "Sevimli manzillarni o'zgartirish ⭐",
        "Изменить избранные адреса ⭐"
        ]

    favorite_addresses = [
        "⭐ Sevimli manzillar",
        "⭐ Избранные адреса"
        ]

    favorite_address_add = [
        "Yangi manzil qo'shish ➕",
        "Добавить адрес ➕"
        ]

    favorite_address_name = [
        "Manzil nomini kiriting",
        "Введите название адреса"
        ]

    favorite_address_location = [
        "Manzilning joylashuvini yuboring 📍",
        "Отправьте местоположение адреса 📍"
        ]

    favorite_address_edit_prompt = [
        "Joriy manzil: {}\nYangi lokatsiyani yuboring 📍",
        "Текущий адрес: {}\nОтправьте новое местоположение 📍"
        ]

    favorite_address_no_addresses = [
        "Hozircha saqlangan manzillar yo'q",
        "Пока нет сохраненных адресов"
        ]

    favorite_address_added = [
        "Sevimli manzil qo'shildi ✅",
        "Избранный адрес добавлен ✅"
        ]

    favorite_address_updated = [
        "Sevimli manzil yangilandi ✅",
        "Избранный адрес обновлен ✅"
        ]

    current_city = [
        "Joriy shahar: ", 
        "Текущий город: "
        ]

    changed_your_city = [
        "Shahar yangilandi", 
        "Город обновлен"
        ]

    baggage = ["🛄 Yukxona", "🛄 Багаж"]

    you_are_blocked = [
        "🚫 Siz qora ro'yxatdasiz va buyurtmani amalga oshira olmaysiz!", 
        "🚫 Вы в черном списке и не можете выполнить заказ!"
        ]

    number_is_incorrect = [
        "Telefon raqam noto'g'ri formatda kiritildi.\nIltimos quyidagi formatda kiriting:\n\n+998901234567", 
        "Номер телефон введен в неправильном формате.\nПожалуйста, введите в этом формате:\n\n+998901234567"
        ]

    message_from_admin = [
        "🧑🏻‍💻 Admin tomonidan xabar:\n\n{}\n\nXabarga javob qaytarish uchun <u>Fikr qoldirish 📨</u> bo'limiga kiring", 
        "🧑🏻‍💻 Сообщение от администратора:\n\n{}\n\nНажмите кнопку <u>Оставить отзыв 📨</u>, чтобы отправить ответ"
        ]

    leave_your_feedback = [
        "Haydovchi xizmatini baholang va fikringizni qoldiring. " \
            "Sizning bahoyingiz xizmat sifatini yaxshilashga yordam beradi. 👇",
        "Оцените работу водителя и оставьте отзыв. " \
            "Ваша оценка помогает нам улучшать качество сервиса. 👇"
    ]

    continue_ = [
        "Davom etish ➡️",
        "Продолжать ➡️"
    ]

    select_reason_of_rating = [
        "😔 Xizmatni past baholaganingiz sababini quyidagi variantlar orasidan belgilang.",
        "😔 Спасибо за вашу оценку. Пожалуйста, выберите основную причину такой оценки."
    ]

    rating_compleation = [
        "✅ Bahoyingiz va fikr-mulohazangiz qabul qilindi. Xizmatimizni yaxshilashga yordam berganingiz uchun rahmat!",
        "✅ Ваша оценка и отзыв успешно отправлены. Спасибо, что помогаете нам улучшать качество сервиса!"
    ]

    another = [
        "Boshqa",
        "Другой"
    ]

    select_pre_order_date = [
        "🚕 Oldindan buyurtma berish uchun safar sanasi va vaqtini tanlang.",
        "🚕 Выберите дату для предварительного заказа."
    ]

    type_pre_order_time = [
        "🕒 Safar vaqtini <code>HH:MM</code> formatida kiriting. kiriting\nMasalan: <b>09:30</b> yoki <b>18:45</b>",
        "🕒 Укажите время поездки в формате <code>HH:MM</code>. Например: <b>09:30</b> или <b>18:45</b>"
    ]

    service_is_not_selected = [
        "Siz hali shaharni tanlamadingiz. Buyurtma berish uchun sozlamalar orqali shaharni tanlang.",
        "Вы еще не выбрали город. Пожалуйста, выберите город в настройках, чтобы оформить заказ."
    ]

    pre_order_time = [
        "🕔 Buyurtma berish vaqti",
        "🕔 Время предварительного заказа"
    ]

    change_pre_order_time = [
        "🔄 Vaqtni o'zgartirish",
        "🔄 Изменить время"
    ]

    get_driver_location = [
        "🗺 Haydovchi joylashuvi",
        "🗺 Получить координаты водителя"
    ]

    feedback_too_long = [
        "❌ Fikr-mulohazangiz juda uzun. Iltimos, 2500 ta belgidan kamroq yozing.",
        "❌ Ваш отзыв слишком длинный. Пожалуйста, введите меньше 2500 символов."
    ]

    order_time = [
        "Buyurtma sanasi",
        "Дата заказа"
    ]

    select_passengers_count = [
        "👥 Yo'lovchilar sonini tanlang",
        "👥 Выберите количество пассажиров"
    ]

    change_passengers_count = [
        "🔄 Yo'lovchilar sonini o'zgartirish",
        "🔄 Изменить количество пассажиров"
    ]

    passengers_count = [
        "👥 Yo'lovchilar soni",
        "👥 Количество пассажиров"
    ]

    created_pre_order_order = [
        "Toshkent ↔️ Bekobod yo'nalishida sizga buyurtma yaratildi.",
        "Для вас создано бронирование на маршруте Ташкент ↔️ Бекабад."
    ]

    _ = [
        "",
        ""
    ]

    _ = [
        "",
        ""
    ]