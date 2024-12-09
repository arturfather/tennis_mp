import datetime, telebot, json, time, random, re, locale
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from telebot import types
from jsons_handlers.jsons_handlers import json_reader, json_writer

ENV = 'UAT'


# static files/variable difinition
gms = 'jsons_data/games.json'
sch_file = 'jsons_data/schedule.json'
msg_file = 'jsons_data/msg_file.json'
tnk_file = 'jsons_data/tnk.json'
log_file = 'logs/log.txt'

alwd_members = ['creator', 'administrator', 'member']
admin_members = ['creator', 'administrator']
alwd_group = [-1001837008506] if ENV == 'UAT' else [-1001598215777]
grpID = -1001837008506 if ENV == 'UAT' else -1001598215777  # чат для записи и болталка

bot_name_val = '@TT_mp_uat_bot' if ENV == 'UAT' else '@TT_mp_bot'
grp_for_chat_link = 'https://t.me/+UagC-5vXZpA3NjBi' if ENV == 'UAT' else 'https://t.me/tennis_mp'

# -1001837008506 UAT grp volleyball #болталка и группа для записи в ЮАТЕ!
# -1001836885665 PRD grp volleyball болталка
# -1001919608124 PRD grp volleyball для записи
# -1001536861033 PRD grp soccer PRD bot
# -1001828324804 UAT grp soccer PRD bot + UAT bot;


lock_holder = None


def format_date1(date_str):
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    date_obj = datetime.strptime(date_str, '%d.%m.%Y')
    formatted_date = date_obj.strftime('%d.%m %a').upper()
    return formatted_date


def filter_past_dates(date_str):
    date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
    return date_obj >= datetime.now().date()


def log_any_incm(message):
    now = datetime.now()
    user = bot.get_chat(message.from_user.id)
    username = user.username if user.username else ''
    first_name = user.first_name if user.first_name else ''
    last_name = user.last_name if user.last_name else ''
    full_name = first_name + ' ' + last_name

    log = str(now) + ' || GROUP ID:' + str(message.chat.id) + '|| GROUP_msg: userID:' + str(message.from_user.id) + '|| nick: @' + str(username) + '|| fname:' + str(full_name) + '|| message:' + str(message.text)
    print(log)
    with open(log_file, 'a', encoding='utf-8') as file: file.write(log + '\n')



def games_extract(message, desc_input_to_games):
    print('------', datetime.now(), 'userID:', message.from_user.id, 'function games_extract - triggered------')

    gms_json_data = json_reader(gms)
    game_data = next((g for g in gms_json_data if g['desc'] == desc_input_to_games), None)
    gmdesc = game_data['desc']
    gmid = game_data['id']
    dateID = game_data['date']
    timeID = game_data['time']
    priceID = game_data['price']
    locationID = game_data['location']
    pl_IDs = game_data['players']
    rpl_IDs = game_data['reserved_players']
    players_list = "\n".join([f"{i + 1}. {'&#9989;' if player[2] else ''} {player[0].strip()}" for i, player in enumerate(pl_IDs)])
    res_pl_list = "\n".join([f"{i + 1}. {'&#9989;' if rplayer[2] else ''} {rplayer[0].strip()}" for i, rplayer in enumerate(rpl_IDs)])
    maxpl = game_data['max_players']
    maxrsrv = game_data['max_reservations']
    dur = game_data['duration_mins']
    sts = game_data['status']

    appl_list_main_msg = (
        f'<b>🗓{format_date1(dateID)} 🕖 {timeID}⏳{dur}мин </b>\n'
        f'<u>🏓 Настольный теннис 🏓</u>\n\n'
        f'📍 {locationID}\n'
        f'&#128176; Стоимость: {priceID}\n'
        f'&#128179; Оплата только безнал\n'
        f'&#9997; Запись/отмена через бота\n\n'
        f'{players_list}\n\n'
        '-----------\n'
        f'<b>Резерв</b>\n'
        f'{res_pl_list}\n\n'
        '-----------\n'
        f'все вопросы {bot_name_val}\n\n'
        '#УВАЖЕНИЕ'
    )


    # n &  # 9989; - оплачено

    text_appl_err3 = '<b>К сожалению уже записано максимальное количество игроков в основу (' + str(maxpl) + ') и резерв (' + str(maxrsrv) + ') &#128532;</b>\n_______________________'

    return gms_json_data, game_data, gmid, gmdesc, dateID, timeID, priceID, locationID, pl_IDs, rpl_IDs, players_list, res_pl_list, maxpl, maxrsrv, dur, sts, appl_list_main_msg, text_appl_err3


def extract_msg_metadata(message):
    print('------', datetime.now(), ' function extract_msg_metadata - triggered------')
    # Use the user_context instance instead of global variables
    user = bot.get_chat(message.from_user.id)
    username = user.username if user.username else ''
    first_name = user.first_name if user.first_name else ''
    last_name = user.last_name if user.last_name else ''
    full_name = first_name + ' ' + last_name

    return user, username, first_name, last_name, full_name


def code_execution_lock(message):
    print('------', datetime.now(), 'code_execution_lock is triggerred for ', message.from_user.id)
    global lock_holder

    random_value = round(random.uniform(0.5, 1.0), 2)
    time.sleep(random_value)
    if lock_holder == None or lock_holder == message.from_user.id:
        lock_holder = message.from_user.id
        print('------', datetime.now(), 'user set his userID no-lock', lock_holder)
        print('------', datetime.now(), 'file not locked for', lock_holder)
    elif lock_holder != message.from_user.id:
        while lock_holder != None:
            print('------', datetime.now(), 'file is locked by', lock_holder)
            time.sleep(0.7)


class UserContext:
    def __init__(self):
        # define_user_based_inputs
        self.usr_prm = None
        self.usr_desc_inp = None


# Create an instance of UserContext
CurUsrCont = UserContext()


def schedule_refresher():
    global cr_mn_id, cr_mn_str, nx_mn_str, repl_txt2, schd, upcoming_games_list, keyboard3, future_events
    schd = json_reader(sch_file)

    # dates, months managements
    cr_mn_id = datetime.now().month
    cr_year = str(datetime.now().year)
    nxt_year = str(datetime.now().year + 1)
    months = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь', 13: 'Январь'}
    day_translation = {'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб', 'Sun': 'Вс'}
    cr_mn_str = months[cr_mn_id]
    nx_mn_str = months[cr_mn_id + 1]

    # all upcoming list
    future_events = []
    for year, months in schd.items():
        for month_events in months:
            for event in month_events:
                event_datetime_str = f"{event[0]} {event[1]}"
                event_datetime = datetime.strptime(event_datetime_str, "%d.%m.%Y %H:%M")

                if event_datetime > datetime.now():
                    future_events.append(event[3])
    # all upcoming list

    if cr_mn_id == 12:
        upcoming_games_list = schd[cr_year][cr_mn_id - 1] + schd[nxt_year][0]
    else:
        upcoming_games_list = schd[cr_year][cr_mn_id - 1] + schd[cr_year][cr_mn_id]

    if cr_mn_id == 12:
        curr_mn_games_list = schd[cr_year][cr_mn_id - 1]
        next_mn_games_list = schd[nxt_year][0]
    else:
        curr_mn_games_list = schd[cr_year][cr_mn_id - 1]
        next_mn_games_list = schd[cr_year][cr_mn_id]

    upcoming_games_list = [', '.join([format_date1(date), time, location]) for date, time, location, gdesc in upcoming_games_list if filter_past_dates(date)]  # upcoming_games_list is used for 3 buttons - ЗАПИСАТЬСЯ/ТЕКУЩИЙ СПИСОК/ОТМЕНА. this list consists of 2 mothns: current and next. past dates are excluded
    upcoming_games_list.sort()
    upcoming_games_list.append('Главное меню 📱')

    curr_mn_schedule_games_list = [', '.join([format_date1(date), time, location]) for date, time, location, gdec in curr_mn_games_list]
    next_mn_schedule_games_list = [', '.join([format_date1(date), time, location]) for date, time, location, gdesc in next_mn_games_list]

    curr_mn_schedule_games_list.sort()
    next_mn_schedule_games_list.sort()

    if cr_mn_id == 12:
        repl_txt2 = ("<u>🤩 Расписание тренировок (игр) 🤩</u>\n\n<b>" + cr_mn_str + ", " + cr_year + "</b>" + "\n" + "\n".join(item for item in curr_mn_schedule_games_list if item) + "\n\n<b>" + nx_mn_str + ", " + nxt_year + "</b>\n" + "\n".join(item for item in next_mn_schedule_games_list if item))
    else:
        repl_txt2 = ("<u>🤩 Расписание тренировок (игр) 🤩</u>\n\n<b>" + cr_mn_str + "</b>" + "\n" + "\n".join(item for item in curr_mn_schedule_games_list if item) + "\n\n<b>" + nx_mn_str + "</b>\n" + "\n".join(item for item in next_mn_schedule_games_list if item))

    # create the custom keyboard3
    keyboard3 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons3 = [KeyboardButton(text=tr) for tr in upcoming_games_list]
    keyboard3.add(*buttons3)
    # create the custom keyboard3


schedule_refresher()

bt_tkn = json_reader(tnk_file)['bot_tkn_UAT'] if ENV == 'UAT' else json_reader(tnk_file)['bot_tkn_PRD']
bot = telebot.TeleBot(bt_tkn)


commands = [types.BotCommand('start', 'Ну что начнем? Нажимай!'), types.BotCommand('admin', 'Команды админа')]

bot.set_my_commands(commands)
but1_text = 'ℹ Общая информация'
but2_text = '🗓 Расписание тренировок'
but3_text = '📍 Локация площадок и парковка'
but4_text = '✍ Записаться на тренировку'
but5_text = '💰 Реквизиты оплаты'
but6_text = '❌ Отменить запись'
but7_text = '🧐 Текущий список'


addg = None
usr_prm = None
user_contexts = {}




repl_txt1 = (
    f'<b>ℹ️ Общая информация</b> \n \n'
    f'1. Собираемся и играем в настольный теннис (на данный момент ГБУ№93, м. Крылатское\n\n'
    f'2. Возраст: 14+ \n \n'
    f'3. Уровень - любой. Рады всем :) \n \n'
    f'4. Стоимость: 700₽/час (за один стол)\n\n'
    f'5. Для того чтобы записаться или отменить запись: вступите в чат настольного тенниса по ссылке ниже и напишите боту {bot_name_val}, далее используйте кнопки:\n\n'
    f'<b>{but4_text}</b>\n <b>{but6_text}</b>.\n\n'
    f'🏐У нас дружная атмосфера - рады всем.🏐\n \n'
    f'<a href="{grp_for_chat_link}">Чат 🎾 большого и 🏓 настольного тенниса в телеграм Мякинино парк</a> \n \n'
    f'По всем остальным вопросам пишите личным сообщением @arturfather)'
)


#список локация
repl_txt3 = (
    f'<b>➡️ ГБУ №93</b> - <i>текущая локация настольный теннис</i> ️\n \n'
    f'Парковка у здания спорт комплекса (во дворах - бесплатная)\n'
    f'📍 <a href="https://yandex.ru/maps/org/gbu_sportivnaya_shkola_93_na_mozhayke_otdeleniye_nastolnogo_tennisa/1114209373">Месторасположение комплекса</a>\n\n'
    f'Большое количество профессиональных столов, душевые, переодевалки\n\n'
    f'  =========================\n\n'
    # f'<b>➡️ ТЦ Капитолий</b> ️\n \n'
    # f'Парковка на территории ТЦ Капитолий (бесплатная). \n'
    # f'📍 <a href="https://yandex.ru/maps/-/CDaCeNmh">Месторасположение парковки и ТЦ</a>\n\n'
    # f'4 больших площадки, мягкий паркет, душевые, переодевалки\n \n'
    # f'  =========================\n\n'
    # f'<b>➡️ 2х2 team</b> - <i>текущая локация пляжный волейбол</i> ️\n \n'
    # f'Парковка вдоль улицы Лыковская (бесплатно). \n'
    # f'📍 <a href="https://yandex.ru/maps/-/CDFuRBla">Месторасположение парковки и площадок</a>\n\n'
    # f'6 кортов, хорошее освещение, подогреваемый песок, душевые, переодевалки\n\n'
)

repl_txt4 = None
repl_txt6 = None

repl_err2 = '_______________________\n<b>Максимальное количество игроков записано, поэтому записал тебя в резерв.\n\nПеренесу из резерва в основной список автоматически, следите за обновлениями</b>'


repl_err5 = (
    f'К сожалению ты не являешься участником группы.'
    f'Пожалуйста, вступите в <a href="{grp_for_chat_link}">группу</a> для записи/отмены записи на тренировку &#9940;'
)

repl_txt15 = '<b>Готово! Записал тебя на следующую тренировку ☺\n\n❗ПОЖАЛУЙСТА, НЕ ОПАЗДЫВАЙТЕ❗️</b>'
repl_err7 = 'OK &#128076;'
repl_txt16 = '<b>Готово! Одна твоя запись отменена ❌</b>'
rerepl_err8 = '<b>Не нашел твоей записи на тренировку 😕</b>'
repl_txt17 = 'Пиши мне напрямую \n' + bot_name_val + '\nБуду рад помочь &#128522; \n\n<i>сообщение удалится через {count}сек</i>'
repl_txt18 = 'Привет!\n\n Я бот 🏓 Настольный теннис🏓 Мякинино парк. Чем могу помочь? 😊\n\n Воспользуйтесь кнопочками внизу ↘️'
repl_txt19 = 'Пожалуйста, выберите дату тренировки'

bot_greeting_msg = ENV + '!!! '+ bot_name_val + ' has started working.' + ENV


# add game txts
help_for_adder_game = 'Окей, для того чтобы добавить новую треню пришли мне текст в формате:\n\n-----------------------------------\n<b>add\nДД.ММ.ГГГГ\nЧЧ:ММ\nXX\nYY\nZZ\nЦена\nМесто</b>\n-----------------------------------\nДД.ММ.ГГГГ - дата новой трени\nЧЧ:ММ - время начала\nXX- продолжительность (мин)\nYY - максимальное количество в основной список (обычно 18), \nZZ - максимальное кол-во в резерв (обычно 8)\nЦена - описание стоимости словами (макс 15 символов)\nМесто - локация кратко (макс 25 символов)\n⚠Все параметры новой строкой без пробелов. Ни в начале строки, ни в кноце строки не должно быть пробелов!⚠\n\n==========================\nПример 1:\n\n<b>add\n01.01.2024\n20:00\n90\n18\n8\n300-500руб/чел\nТЦ Шапито</b>\n\nто есть, тренировка 1 янв 2024, начало в 20:00, продолжительность 90 минут. Максимальное количество игроков - 18 а в резерв - 8 (если выпишуться из основного списка). Стоимость игры - 300-500руб\чел. Локация площадки - ТЦ Шапито\n\n==========================\nПример 2:\n\n<b>add\n10.12.2023\n09:00\n120\n10\n0\nБесплатно\nМневники</b>\n\nто есть, тренировка 10 дек 2023, начало в 09:00, продолжительность 120 минут. Максимальное количество игроков - 10 а в резерв - 0. Стоимость игры - Бесплатно. Локация площадки - Мневники'

adder_game_err = 'Неверный формат. Для получения справки по команде добавления напиши мне <b>add help</b>'
adder_game_succ = 'Готово, добавил тренировку в расписание! Посмотрите расписание 😊'
prev_date_add_attempt = 'Прости, но я не могу вернуться в прошлое...'

# remove game txts
rmv_game_err = 'Неверный формат или указанная дата не найдена. Для получения справки по команде удаления напиши мне <b>remove help</b>'
rmv_game_succ = 'Готово, удалил тренировку из расписания! Посмотрите расписание 😊'
help_for_remover_game = 'Окей, для того чтобы удалить тренировку из расписание, просто пришли мне тренировку в формате ниже:\n\n'

admin_help = '<b>Команды админа</b>\n\n <b><i><u>add help</u></i></b> - справка по команде добавления тренировки \n\n <b><i><u>remove help</u></i></b> - справка по команде удаления тренировки\n\n <i>остальные команды в разработке</i>\n\n===================== \n для того чтобы отправить мне команду, просто отправьте мне её сообщением'

# create the custom keyboard1
keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(*[KeyboardButton(text=text) for text in [but1_text, but2_text, but3_text, but4_text, but6_text, but7_text]])
# create the custom keyboard1




################################################################## Define static variables


# Define a function to handle ANY message
@bot.message_handler(func=lambda message: True)
def MSG_HANDLER(message):
    schedule_refresher()
    log_any_incm(message)
    print('------', datetime.now(), 'entered to INCOME msg handler------')

    user_id = message.from_user.id
    if user_id not in user_contexts:
        # If not, create a new instance and initialize it
        user_contexts[user_id] = UserContext()
    CurUsrCont = user_contexts[user_id]

    user, username, first_name, last_name, full_name = extract_msg_metadata(message)
    print('------', datetime.now(), 'AT THE START OF MSG HANDLER: username=', username, ' | CurUsrCont.usr_prm=', CurUsrCont.usr_prm, ' | CurUsrCont.usr_desc_inp=', CurUsrCont.usr_desc_inp, ' | lock_holder=', lock_holder)

    response_dict = {but1_text: repl_txt1,
                     but2_text: repl_txt2,
                     but3_text: repl_txt3,
                     but4_text: 'function',
                     but6_text: 'function',
                     but7_text: 'function'}

    if message.text in ['/start', '/start' + bot_name_val, bot_name_val, bot_name_val + ' ']:
        start_handler(message)

    elif message.chat.type == 'private' and message.text == 'Главное меню 📱':  # dont move this piece of block lower
        bot.send_message(message.chat.id, "С чего начнем мой юный друг 🐣", reply_markup=keyboard1, parse_mode='HTML')
        CurUsrCont.usr_prm = None
        CurUsrCont.usr_desc_inp = None


    elif message.chat.type == 'private' and message.text == but4_text:
        CurUsrCont.usr_prm = 'a'
        bot.send_message(message.chat.id, repl_txt19, reply_markup=keyboard3, parse_mode='HTML')

    elif message.chat.type == 'private' and message.text == but6_text:
        CurUsrCont.usr_prm = 'd'
        bot.send_message(message.chat.id, repl_txt19, reply_markup=keyboard3, parse_mode='HTML')

    elif message.chat.type == 'private' and message.text == but7_text:
        CurUsrCont.usr_prm = 'l'
        bot.send_message(message.chat.id, repl_txt19, reply_markup=keyboard3, parse_mode='HTML')

    elif message.chat.type == 'private' and message.text in [but1_text, but2_text, but3_text, but5_text]:
        bot.send_message(chat_id=message.chat.id, text=response_dict[message.text], parse_mode='HTML', disable_web_page_preview=True)

    elif message.chat.type == 'private' and 'add' in message.text and (bot.get_chat_member(grpID, user.id)).status in admin_members:
        add_game_handler(message)

    elif message.chat.type == 'private' and 'remove' in message.text and (bot.get_chat_member(grpID, user.id)).status in admin_members:
        remove_game_handler(message)

    elif message.chat.type == 'private' and 'stat' in message.text and (bot.get_chat_member(grpID, user.id)).status in admin_members:
        statist_handler(message)

    elif message.chat.type == 'private' and message.text == '/admin' and (bot.get_chat_member(grpID, user.id)).status in admin_members:
        bot.send_message(message.chat.id, text=admin_help, parse_mode='HTML')

    elif message.text in upcoming_games_list and CurUsrCont.usr_prm:
        print('------', datetime.now(), 'specific date elif block start------')
        CurUsrCont.usr_desc_inp = message.text
        print('------', datetime.now(), 'username=', username, ' | CurUsrCont.usr_prm=', CurUsrCont.usr_prm, ' | CurUsrCont.usr_desc_inp=', CurUsrCont.usr_desc_inp)

        if CurUsrCont.usr_prm == 'a':
            application_handler(message, CurUsrCont)  # go to application handler
        elif CurUsrCont.usr_prm == 'd':
            cancellation_handler(message, CurUsrCont)  # go to remove application handler
        elif CurUsrCont.usr_prm == 'l':
            inquiry_handler(message, CurUsrCont)  # go to share list handler
        # elif CurUsrCont.usr_prm == 'm': money_text_handler(message, CurUsrCont)  # go to add money-marker handler

    print('------', datetime.now(), 'AT THE END OF MSG HANDLER: username=', username, ' | CurUsrCont.usr_prm=', CurUsrCont.usr_prm, ' | CurUsrCont.usr_desc_inp=', CurUsrCont.usr_desc_inp, ' | lock_holder=', lock_holder)


################################HANDLERS ############################################################

# application to training request handler
def application_handler(message, CurUsrCont):
    print('------', datetime.now(), 'entered to application function------')

    code_execution_lock(message)  # lock file based on userID

    # extract some values from functions
    user, username, first_name, last_name, full_name = extract_msg_metadata(message)
    gms_json_data, game_data, gmid, gdesc, dateID, timeID, priceID, locationID, pl_IDs, rpl_IDs, players_list, res_pl_list, maxpl, maxrsrv, dur, sts, appl_list_main_msg, text_appl_err3 = games_extract(message, CurUsrCont.usr_desc_inp)

    print('------', datetime.now(), 'within application  handler function - username=', username, ' | CurUsrCont.usr_prm=', CurUsrCont.usr_prm, ' | CurUsrCont.usr_desc_inp=', CurUsrCont.usr_desc_inp)

    if (bot.get_chat_member(grpID, user.id)).status not in alwd_members: text_apply_msg = repl_err5  # user not present in group. err5
    elif len(pl_IDs) >= maxpl and len(rpl_IDs) >= maxrsrv:  text_apply_msg = text_appl_err3  # no space in main / reservation lists. err3
    

    else:
        if len(pl_IDs) < maxpl:  # to add to the reserve list
            game_data['players'].append(['@' + username + ' ' + full_name, user.id, False])
            text_apply_msg = repl_txt15
        elif len(pl_IDs) >= maxpl and len(rpl_IDs) < maxrsrv:  # to add to the reserve list
            game_data['reserved_players'].append(['@' + username + ' ' + full_name, user.id, False])
            text_apply_msg = repl_err2

        json_writer(gms, gms_json_data)

        gms_json_data, game_data, gmid, gmdesc, dateID, timeID, priceID, locationID, pl_IDs, rpl_IDs, players_list, res_pl_list, maxpl, maxrsrv, dur, sts, appl_list_main_msg, text_appl_err3 = games_extract(message, CurUsrCont.usr_desc_inp)

    if text_apply_msg == repl_err5: bot.send_message(chat_id=message.chat.id, text=text_apply_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)  # - user not in grp. err5
    
    elif text_apply_msg == text_appl_err3:# no space in main/reserv lists. err3
        bot.send_message(chat_id=message.chat.id, text=appl_list_main_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)
        bot.send_message(chat_id=message.chat.id, text=text_apply_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)
          
    
    else:
        bot.send_message(chat_id=message.chat.id, text=appl_list_main_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)
        bot.send_message(chat_id=message.chat.id, text=text_apply_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)

        main_applic_msg = bot.send_message(chat_id=grpID, text=appl_list_main_msg, parse_mode='HTML', disable_web_page_preview=True)

        # removing prev msg identified by 'GMDESC' in grpID
        msg_data = json_reader(msg_file)

        if gmdesc in msg_data:
            print('i going to remove msg initiated from application_handler')
            try:
                bot.delete_message(chat_id=grpID, message_id=msg_data[gmdesc])
            except:
                print('meesage for removal not found')

        msg_data[gmdesc] = main_applic_msg.message_id
        json_writer(msg_file, msg_data)
        # removing prev msg identified by 'GMDESC' in grpID

    CurUsrCont.usr_prm = None
    CurUsrCont.usr_desc_inp = None
    global lock_holder
    lock_holder = None


# cancellation from training request handler
def cancellation_handler(message, CurUsrCont):
    print('------', datetime.now(), 'entered to cancellation function------')

    code_execution_lock(message)

    user, username, first_name, last_name, full_name = extract_msg_metadata(message)
    gms_json_data, game_data, gmid, gmdesc, dateID, timeID, priceID, locationID, pl_IDs, rpl_IDs, players_list, res_pl_list, maxpl, maxrsrv, dur, sts, appl_list_main_msg, text_appl_err3 = games_extract(message, CurUsrCont.usr_desc_inp)

    print('------', datetime.now(), 'within application  handler function - username=', username, ' | CurUsrCont.usr_prm=', CurUsrCont.usr_prm, ' | CurUsrCont.usr_desc_inp=', CurUsrCont.usr_desc_inp)

    if (bot.get_chat_member(grpID, user.id)).status not in alwd_members:
        text_cancl_msg = repl_err5  # user not in group. err5

    elif not (any(user.id in player for player in game_data['players'])) and not (any(user.id in reserved_player for reserved_player in game_data['reserved_players'])):
        text_cancl_msg = rerepl_err8  # application to cancel not found

    elif any(user.id in player for player in game_data['players']) or any(user.id in reserved_player for reserved_player in game_data['reserved_players']):
        text_cancl_msg = repl_txt16
        # Remove one occurrence from the reserved_players list (from bottom to top)
        for i in range(len(game_data['reserved_players']) - 1, -1, -1):
            if user.id in game_data['reserved_players'][i]:
                del game_data['reserved_players'][i]
                break
        else:  # If no match found in reserved_players, remove one occurrence from players list (from bottom to top)
            for i in range(len(game_data['players']) - 1, -1, -1):
                if user.id in game_data['players'][i]:
                    del game_data['players'][i]
                    break
        while len(game_data['players']) < maxpl and len(game_data['reserved_players']) > 0:
            player_to_move = game_data['reserved_players'].pop(0)
            game_data['players'].append(player_to_move)

    json_writer(gms, gms_json_data)

    gms_json_data, game_data, gmid, gmdesc, dateID, timeID, priceID, locationID, pl_IDs, rpl_IDs, players_list, res_pl_list, maxpl, maxrsrv, dur, sts, appl_list_main_msg, text_appl_err3 = games_extract(message, CurUsrCont.usr_desc_inp)

    # cancellation from training request handler

    # send final message of cancel_application
    if text_cancl_msg == repl_err5: bot.send_message(chat_id=message.chat.id, text=text_cancl_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)  # user not in group. err5
    
    elif text_cancl_msg == rerepl_err8: # application of user not found. personal reply repl_err8
        bot.send_message(chat_id=message.chat.id, text=appl_list_main_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)
        bot.send_message(chat_id=message.chat.id, text=text_cancl_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)  
    
    elif text_cancl_msg in repl_txt16:  # succesfully removed. clr_scc1
        bot.send_message(chat_id=message.chat.id, text=appl_list_main_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)
        bot.send_message(chat_id=message.chat.id, text=text_cancl_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)

        main_cncl_msg = bot.send_message(chat_id=grpID, text=appl_list_main_msg, parse_mode='HTML', disable_web_page_preview=True)

        # removing prev msg identified by 'GMDESC' in grpID
        msg_data = json_reader(msg_file)
        if gmdesc in msg_data:
            try:
                bot.delete_message(chat_id=grpID, message_id=msg_data[gmdesc])
            except:
                print('meesage for removal not found')
        msg_data[gmdesc] = main_cncl_msg.message_id
        json_writer(msg_file, msg_data)
        # removing prev msg identified by 'GMDESC' in grpID

    CurUsrCont.usr_prm = None
    CurUsrCont.usr_desc_inp = None
    global lock_holder
    lock_holder = None


# inquiry of training request handler
def inquiry_handler(message, CurUsrCont):
    print('------', datetime.now(), 'entered to inquiry function------')
    print('------', datetime.now(), 'CurUsrCont.usr_desc_inp WITHIN inquirt function =', CurUsrCont.usr_desc_inp)
    user, username, first_name, last_name, full_name = extract_msg_metadata(message)

    gms_json_data, game_data, gmid, gmdesc, dateID, timeID, priceID, locationID, pl_IDs, rpl_IDs, players_list, res_pl_list, maxpl, maxrsrv, dur, sts, appl_list_main_msg, text_appl_err3 = games_extract(message, CurUsrCont.usr_desc_inp)

    if (bot.get_chat_member(grpID, user.id)).status not in alwd_members:
        bot.send_message(chat_id=message.chat.id, text=repl_err5, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)  # user not in group.err5
    else:
        bot.send_message(chat_id=message.chat.id, text=appl_list_main_msg, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard1)

    CurUsrCont.usr_prm = None
    CurUsrCont.usr_desc_inp = None


# start msg handler
def start_handler(message):
    print('------', datetime.now(), 'entered to start function------')
    if message.chat.id in alwd_group:
        # delete initiator message
        try:
            # Attempt to remove. Handler added in case if initiator has removed a message himself
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            now = datetime.now()
            error_description = str(e)
            log = f"{now} || Unable to delete user's message /start. Reason: {error_description} user: {message.from_user.id}"
            print(log)
            with open(log_file, 'a', encoding='utf-8') as file:
                file.write(log + '\n')

        # reply to user in group chat and make countdown timer
        msg_repl_priv_start = bot.send_message(chat_id=message.chat.id, text=repl_txt17.format(count=3), parse_mode='HTML')
        time.sleep(2)
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg_repl_priv_start.message_id, text=repl_txt17.format(count=2), parse_mode='HTML')
        time.sleep(2)
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg_repl_priv_start.message_id, text=repl_txt17.format(count=1), parse_mode='HTML')
        time.sleep(2)

        # remove own message
        bot.delete_message(chat_id=message.chat.id, message_id=msg_repl_priv_start.message_id)


    elif message.chat.type == 'private':
        bot.send_message(message.chat.id, repl_txt18, reply_markup=keyboard1, parse_mode='HTML')


# new game handler
def add_game_handler(message):
    print('------ENTERED TO ADD_GAME_HANDLER')
    pattern = r'add\n(\d{2}\.\d{2}\.\d{4})\n(\d{2}:\d{2})\n(\d{2,3})\n(\d{1,2})\n(\d{1})\n(.{0,20})\n(.{0,25})$'
    match = re.match(pattern, message.text)

    if match:
        new_dt, new_tm, new_dur, new_max_players, new_max_reservations, new_price, new_loc = match.groups()  # parse data from user input
        mnth = int(new_dt.split('.')[1])
        yr = (new_dt.split('.')[2])

    # add help request
    if message.text == 'add help':
        bot.send_message(chat_id=message.from_user.id, text=help_for_adder_game, parse_mode='HTML', disable_web_page_preview=True)

    # prev date attempt error
    elif match and datetime.strptime(new_dt, '%d.%m.%Y').replace(hour=23, minute=55, second=55) < datetime.now():
        bot.send_message(chat_id=message.from_user.id, text=prev_date_add_attempt, parse_mode='HTML', disable_web_page_preview=True)

    # adding new game
    elif match:
        print('------ADDING NEW GAME')
        code_execution_lock(message)

        # GAMES JSON UPDATE
        gms_json_data = json_reader(gms)  # get data from games file

        if gms_json_data == []:
            latest_id = 0
        else:
            latest_id = max(gms_json_data, key=lambda x: x.get('id', 0)).get('id', 0)  # define latest id
        new_id = latest_id + 1  # define new ID
        new_game = {
            "date": new_dt,
            "desc": str(format_date1(new_dt)) + ', ' + str(new_tm) + ', 📍' + str(new_loc),
            "duration_mins": new_dur,
            "id": new_id,
            "location": new_loc,
            "max_players": int(new_max_players),
            "max_reservations": int(new_max_reservations),
            "players": [],
            "price": new_price,
            "reserved_players": [],
            "status": "new",
            "time": new_tm
        }  # define new game object
        gms_json_data.append(new_game)  # append new game to gms_json_data object
        json_writer(gms, gms_json_data)  # write to file

        # SCHEDULE JSON UPDATE
        schedule_refresher()
        if schd[yr] == []:
            schd[yr][0].append([new_dt, new_tm, "📍" + new_loc, str(format_date1(new_dt)) + ', ' + str(new_tm) + ', 📍' + str(new_loc)])
        else:
            schd[yr][mnth - 1].append([new_dt, new_tm, "📍" + new_loc, str(format_date1(new_dt)) + ', ' + str(new_tm) + ', 📍' + str(new_loc)])
        json_writer(sch_file, schd)
        schedule_refresher()

        'get data about user-game adder'
        user, username, first_name, last_name, full_name = extract_msg_metadata(message)

        bot.send_message(chat_id=message.from_user.id, text=adder_game_succ, parse_mode='HTML', disable_web_page_preview=True)
        bot.send_message(chat_id=grpID,
                         text='Пользователь <b>' + full_name + ' (@' + username + ')</b> добавил новую тренировку ✅\n\n 🗓' + format_date1(new_dt) + " 🕖 " + new_tm + ", 📍" + new_loc + '\n\nЗаписаться  / отменить запись - через бота:\n<b>' + bot_name_val + '</b>', parse_mode='HTML', disable_web_page_preview=True)

    # error - format not matched
    else:
        bot.send_message(chat_id=message.from_user.id, text=adder_game_err, parse_mode='HTML', disable_web_page_preview=True)

    global lock_holder
    lock_holder = None


# remove game hander
def remove_game_handler(message):
    if message.text == 'remove help':
        schedule_refresher()

        # help_for_remover_game =  ('Окей, для того чтобы удалить тренировку из расписание, просто пришли мне любую строку ниже:\n\n\n' + '\n'.join(f'```copy remove {item}```\n\n' for i, item in enumerate(future_events)))
        help_for_remover_game = 'Окей, для того чтобы удалить тренировку из расписание, просто пришли мне тренировку которую нужно удалить из списка ниже. Для того чтобы скопировать строку - нажми на неё\n\n\n' + '\n'.join(f'<code>remove {item}</code>\n\n' for i, item in enumerate(future_events))

        bot.send_message(chat_id=message.from_user.id, text=help_for_remover_game, parse_mode='HTML', disable_web_page_preview=True)
    else:
        gm_to_remove = message.text.replace('remove ', '')
        if gm_to_remove in future_events:

            print('------ entered to removal game in schd sub-module')
            for year, months in schd.items():
                for month_index in range(len(months)):
                    schd[year][month_index] = [item for item in schd[year][month_index] if item[3] != gm_to_remove]
            json_writer(sch_file, schd)

            gms_data = json_reader(gms)
            gms_data = [item for item in gms_data if item['desc'] != gm_to_remove]
            json_writer(gms, gms_data)

            user, username, first_name, last_name, full_name = extract_msg_metadata(message)

            bot.send_message(chat_id=message.from_user.id, text=rmv_game_succ, parse_mode='HTML', disable_web_page_preview=True)
            bot.send_message(chat_id=grpID,
                             text='Пользователь <b>' + full_name + ' (@' + username + ')</b> удалил тренировку ❌\n\n' + gm_to_remove, parse_mode='HTML', disable_web_page_preview=True)

    global lock_holder
    lock_holder = None
    schedule_refresher()


def statist_handler(message):
    print('------ENTERED TO STATIST_HANDLER')
    games_data = json_reader('games.json')

    # Initialize a dictionary to store player counts by user ID
    player_counts_by_id = {}

    # Iterate through each game
    for game in games_data:
        # Initialize a set to store players for the current game
        players_in_game = set()
        # Extract players for the current game
        players = game['players']
        # Update player counts in the dictionary, considering only unique players per game
        for player_info in players:
            user_id = player_info[1]
            if user_id not in players_in_game:
                if user_id not in player_counts_by_id:
                    player_counts_by_id[user_id] = (player_info[0], 0)
                player_counts_by_id[user_id] = (player_info[0], player_counts_by_id[user_id][1] + 1)
                players_in_game.add(user_id)

    # Sort the dictionary items by values
    sorted_player_counts = sorted(player_counts_by_id.items(), key=lambda x: x[1][1], reverse=True)

    # Print the sorted player counts
    stat_msg = '✅ Начиная с ' + str(games_data[0]['date']) + ' сыграно игр: ' + str(games_data[-1]['id']) + '\n\n✅ Самые активные участники:\n'

    cnt = 1
    for k, v in sorted_player_counts:
        stat_msg += str(cnt) + '. ' + str(v).replace('(', '').replace(')', '').replace("'", '').replace(',', ':') + '\n'
        cnt += 1

    bot.send_message(chat_id=message.from_user.id, text=stat_msg, parse_mode='HTML', disable_web_page_preview=True)


############################################################################################


# UAT-CHECK
bot.send_message(chat_id=527520543, text=bot_greeting_msg)

bot.polling()

