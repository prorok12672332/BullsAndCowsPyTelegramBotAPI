import telebot
from telebot import types
from time import sleep
from secrets import randbelow
from random import shuffle

tokenf = open('token.txt', 'r')
if tokenf.readline()[-1] == '\n':
    tokenf.seek(0)
    token = tokenf.readline()[:-1]
else:
    tokenf.seek(0)
    token = tokenf.readline()
rules = "Суть игры в следующем. Каждый из противников задумывает "\
        "четырехзначное число, все цифры которого различны\n"\
        "(первая цифра числа отлична от нуля). Необходимо разгадать"\
        " задуманное число. Выигрывает тот, кто отгадает первый.\n"\
        "Противники по очереди называют друг другу числа и сообщают"\
        " о количестве «быков» и «коров» в названном числе\n(«бык» —"\
        " цифра есть в записи задуманного числа и стоит в той же "\
        "позиции, что и в задуманном числе;\n«корова» — цифра есть в"\
        " записи задуманного числа, но не стоит в той же позиции, "\
        "что и в задуманном числе).\nНапример, если задумано число "\
        "3275 и названо число 1234, получаем в названном числе "\
        "одного «быка» и одну «корову».\nОчевидно, что число "\
        "отгадано в том случае, если имеем 4 «быка»)"


while True:
    try:
        try:
            bot = telebot.TeleBot(token)
        except Exception as e:
            print(e.args)
            print('С токеном или ботом что-то не так')
        user_dict = {}

        class User:
            def __init__(self):
                self.name = ''
                self.num1 = []
                self.num2 = []
                self.choices = []

        @bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            if call.data == 'back':
                if call.message.text == 'Какая-то ошибка':
                    bot.delete_message(call.message.chat.id,
                                       call.message.message_id)
                    try:
                        user_dict[call.message.chat.id] = None
                    except:
                        start_mes(call.message)
                        return
                else:
                    bot.edit_message_reply_markup(call.message.chat.id,
                                                  call.message.message_id)
                if user_dict[call.message.chat.id] is None:
                    start_mes(call.message)
                return

        @bot.message_handler(commands=['start', 'begin', 'старт'])
        def start_mes(message):
            try:
                # markup = types.ReplyKeyboardRemove(selective=False)
                # bot.send_message(message.chat.id,
                #                  'Добро пожаловать в бота для\nигры в "Быки и Коровы"',
                #                  reply_markup=markup)
                user_dict[message.chat.id] = User
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                   resize_keyboard=True, row_width=2)
                bt1 = types.KeyboardButton('Играть')
                bt2 = types.KeyboardButton('Правила')
                bt3 = types.KeyboardButton('Выход')
                markup.add(bt1, bt2, bt3)
                msg = bot.send_message(message.chat.id, "Выберите действие",
                                       reply_markup=markup)
                bot.register_next_step_handler(msg, answer)
                return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def gen_num():
            while True:
                aboba = [randbelow(10) for x in range(4)]
                if len(aboba) == len(set(aboba)) and aboba[0] != 0:
                    break
            return aboba

        def gen_num_hard(user1, user_id):

            def scorecalc(guess, chosen):
                bulls = cows = 0
                for g, c in zip(guess, chosen):
                    if g == c:
                        bulls += 1
                    elif g in chosen:
                        cows += 1
                return bulls, cows

            ans = user1[user_id].choices[0]
            bik, korova = 0, 0
            for i in range(4):
                if user1[user_id].num1[i] == ans[i]:
                    bik += 1
                elif user1[user_id].num1[i] in ans:
                    korova += 1
            score = (bik, korova)
            user1[user_id].choices = [
                c for c in user1[user_id].choices if scorecalc(c, ans) == score]
            return user1[user_id], bik, korova

        def bull(bik):
            if(bik == 0):
                return "ов"
            elif(bik > 1):
                return 'а'
            else:
                return ''

        def cow(korova):
            if(korova > 1):
                return 'ы'
            else:
                return ''

        def check_num(n, message):
            try:
                if not n.isdigit():
                    msg = bot.send_message(
                        message.chat.id, 'Я же сказал: "*число*"',
                        parse_mode='MarkdownV2')
                    return msg, False
                else:
                    if(len(n)) == 4:
                        if len(set(list(n))) != len(n):
                            msg = bot.send_message(message.chat.id,
                                                   "Вы ввели число, в котором есть повторяющиеся цифры")
                            return msg, False
                        elif n[0] == '0':
                            msg = bot.send_message(
                                message.chat.id, 'Число не может начинаться с 0')
                            return msg, False
                        else:
                            return 1, True
                    else:
                        msg = bot.send_message(
                            message.chat.id, "Вы ввели не четырёхзначное число")
                        return msg, False
            except:
                msg = bot.send_message(message.chat.id, 'Я же сказал: "*число*"',
                                       parse_mode='MarkdownV2')
                return msg, False

        def win_gif():
            t = randbelow(4)
            if t == 0:
                gif = open('win1.gif', 'rb')
            elif t == 1:
                gif = open('win2.gif', 'rb')
            elif t == 2:
                gif = open('win3.gif', 'rb')
            elif t == 3:
                gif = open('win3.gif', 'rb')
            return gif

        def back():
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(
                text="Главное Меню", callback_data="back")
            keyboard.add(callback_button)
            return keyboard

        def answer(message):
            try:
                if message.text == 'Играть':
                    markup = types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2)
                    bt1 = types.KeyboardButton('Против компьютера')
                    bt2 = types.KeyboardButton('Против второго\nигрока')
                    bt3 = types.KeyboardButton('<-----')
                    markup.add(bt1, bt2, bt3)
                    msg = bot.send_message(message.chat.id, 'Выберите режим игры',
                                           reply_markup=markup)
                    bot.register_next_step_handler(msg, gamemode)
                    return
                elif message.text == 'Правила':
                    keyboard = types.InlineKeyboardMarkup()
                    callback_button = types.InlineKeyboardButton(
                        text="<-----", callback_data="back")
                    keyboard.add(callback_button)
                    bot.send_message(message.chat.id, rules,
                                     reply_markup=keyboard)
                    user_dict[message.chat.id] = None
                    return
                elif message.text == "Выход":
                    markup = types.ReplyKeyboardRemove(selective=False)
                    try:
                        bot.send_message(message.chat.id, 'Пока, '
                                         + message.from_user.first_name,
                                         reply_markup=markup)
                    except:
                        bot.send_message(message.chat.id, 'Пока, '
                                         + message.from_user.username,
                                         reply_markup=markup)
                    user_dict[message.chat.id] = None
                    return
                else:
                    msg = bot.send_message(
                        message.chat.id, "Выберите действие")
                    bot.register_next_step_handler(msg, answer)
                    return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def gamemode(message):
            try:
                if message.text == 'Против компьютера':
                    markup = types.ReplyKeyboardMarkup(
                        resize_keyboard=True, row_width=2)
                    bt1 = types.KeyboardButton('Легко')
                    bt2 = types.KeyboardButton('Сложно')
                    bt3 = types.KeyboardButton('<-----')
                    markup.add(bt1, bt2, bt3)
                    msg = bot.send_message(message.chat.id, 'Выберите уровень сложности',
                                           reply_markup=markup)
                    bot.register_next_step_handler(msg, hardness)
                    return
                elif message.text == 'Против второго\nигрока':
                    markup = types.ReplyKeyboardRemove(selective=False)
                    msg = bot.send_message(
                        message.chat.id, "Игрок 2, введите своё имя", reply_markup=markup)
                    bot.register_next_step_handler(msg, vs1)
                    return
                elif message.text == '<-----':
                    start_mes(message)
                    return
                else:
                    msg = bot.send_message(
                        message.chat.id, "Выберите режим игры")
                    bot.register_next_step_handler(msg, gamemode)
                    return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def vs1(message):
            try:
                try:
                    user_dict[message.chat.id].name = str(message.text)
                except Exception as e:
                    print(e)
                    bot.send_message(message.chat.id, "Ну и чё это?")
                    msg = bot.send_message(
                        message.chat.id, 'Игрок 2, введите своё имя')
                    bot.register_next_step_handler(msg, vs1)
                    return
                if user_dict[message.chat.id].name == 'None':
                    bot.send_message(message.chat.id, "Ну и чё это?")
                    msg = bot.send_message(
                        message.chat.id, 'Игрок 2, введите своё имя')
                    bot.register_next_step_handler(msg, vs1)
                    return
                try:
                    msg = bot.send_message(message.chat.id, message.from_user.first_name
                                           + ', загадайте число')
                except:
                    msg = bot.send_message(message.chat.id, message.from_user.username
                                           + ', загадайте число')
                bot.register_next_step_handler(msg, set_num1)
                return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def set_num1(message):
            try:
                n = message.text
                msg, a = check_num(n, message)
                if not a:
                    bot.register_next_step_handler(msg, set_num1)
                    return
                user_dict[message.chat.id].num1 = list(
                    map(lambda x: int(x), list(str(n))))
                bot.send_message(message.chat.id, '|\n' * 50)
                msg = bot.send_message(message.chat.id, '\n' * 40
                                       + user_dict[message.chat.id].name
                                       + ', загадайте число')
                bot.register_next_step_handler(msg, set_num2)
                return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def set_num2(message):
            try:
                n = message.text
                msg, a = check_num(n, message)
                if not a:
                    bot.register_next_step_handler(msg, set_num2)
                    return
                user_dict[message.chat.id].num2 = list(
                    map(lambda x: int(x), list(str(n))))
                bot.send_message(message.chat.id, '|\n' * 50)
                try:
                    msg = bot.send_message(message.chat.id,
                                           message.from_user.first_name
                                           + ', попробуйте угадать число')
                except:
                    msg = bot.send_message(message.chat.id,
                                           message.from_user.username
                                           + ', попробуйте угадать число')
                bot.register_next_step_handler(msg, guessU1)
                return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def guessU1(message):
            try:
                n = message.text
                msg, a = check_num(n, message)
                if not a:
                    bot.register_next_step_handler(msg, guessU1)
                    return
                num_guess = list(map(lambda x: int(x), list(str(n))))
                bik, korova = 0, 0
                for i in range(len(num_guess)):
                    if num_guess[i] == user_dict[message.chat.id].num2[i]:
                        bik += 1
                    elif num_guess[i] in user_dict[message.chat.id].num2:
                        korova += 1
                bikstr = "бык" + bull(bik)
                korovastr = "коров" + ('а' if korova == 1 else cow(korova))
                if bik == 4:
                    try:
                        bot.send_message(
                            message.chat.id, "Выиграл " + message.from_user.first_name)
                    except:
                        bot.send_message(
                            message.chat.id, "Выиграл " + message.from_user.username)
                    bot.send_animation(message.chat.id, win_gif(), None,
                                       'text', reply_markup=back())
                    user_dict[message.chat.id] = None
                    return
                else:
                    bot.send_message(message.chat.id, "В названном числе " + str(bik) + ' '
                                     + bikstr + ' и ' + str(korova) + ' ' + korovastr)
                    msg = bot.send_message(message.chat.id, user_dict[message.chat.id].name
                                           + ', попробуйте угадать число')
                    bot.register_next_step_handler(msg, guessU2)
                    return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def guessU2(message):
            try:
                n = message.text
                msg, a = check_num(n, message)
                if not a:
                    bot.register_next_step_handler(msg, guessU2)
                    return
                num_guess = list(map(lambda x: int(x), list(str(n))))
                korova, bik = 0, 0
                for i in range(len(num_guess)):
                    if num_guess[i] == user_dict[message.chat.id].num1[i]:
                        bik += 1
                    elif num_guess[i] in user_dict[message.chat.id].num1:
                        korova += 1
                bikstr = "бык" + bull(bik)
                korovastr = "коров" + ('а' if korova == 1 else cow(korova))
                if bik == 4:
                    bot.send_message(message.chat.id, "Выиграл "
                                     + user_dict[message.chat.id].name)
                    bot.send_animation(message.chat.id, win_gif(), None,
                                       'text', reply_markup=back())
                    user_dict[message.chat.id] = None
                    return
                else:
                    bot.send_message(message.chat.id, "В названном числе " + str(bik) + ' '
                                     + bikstr + ' и ' + str(korova) + ' ' + korovastr)
                    try:
                        msg = bot.send_message(message.chat.id,
                                               message.from_user.first_name
                                               + ', попробуйте угадать число')
                    except:
                        msg = bot.send_message(message.chat.id,
                                               message.from_user.username
                                               + ', попробуйте угадать число')
                    bot.register_next_step_handler(msg, guessU1)
                    return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        # Против компьютера
        def hardness(message):
            if message.text == 'Сложно':
                user_dict[message.chat.id].name = message.text
                user_dict[message.chat.id].choices = []
                for i in range(1, 10):
                    for j in range(10):
                        for m in range(10):
                            for n in range(10):
                                num = str(i) + str(j) + str(m) + str(n)
                                if len(num) == len(set(num)):
                                    user_dict[message.chat.id].choices.append(
                                        num)
                shuffle(user_dict[message.chat.id].choices)
                user_dict[message.chat.id].num2 = list(
                    map(lambda x: int(x), list(user_dict[message.chat.id].choices[0])))
                markup = types.ReplyKeyboardRemove(selective=False)
                try:
                    msg = bot.send_message(message.chat.id, message.from_user.first_name
                                           + ', загадайте число', reply_markup=markup)
                except:
                    msg = bot.send_message(message.chat.id, message.from_user.username
                                           + ', загадайте число', reply_markup=markup)
                bot.register_next_step_handler(msg, inp_int)
                return
            elif message.text == 'Легко':
                user_dict[message.chat.id].name = message.text
                user_dict[message.chat.id].choices = []
                while True:
                    user_dict[message.chat.id].num2 = gen_num()
                    if user_dict[message.chat.id].num2 not in user_dict[message.chat.id].choices:
                        user_dict[message.chat.id].choices.append(
                            user_dict[message.chat.id].num2)
                    else:
                        break
                markup = types.ReplyKeyboardRemove(selective=False)
                try:
                    msg = bot.send_message(message.chat.id, message.from_user.first_name
                                           + ', загадайте число', reply_markup=markup)
                except:
                    msg = bot.send_message(message.chat.id, message.from_user.username
                                           + ', загадайте число', reply_markup=markup)
                bot.register_next_step_handler(msg, inp_int)
                return
            elif message.text == '<-----':
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=2)
                bt1 = types.KeyboardButton('Против компьютера')
                bt2 = types.KeyboardButton('Против второго\nигрока')
                bt3 = types.KeyboardButton('<-----')
                markup.add(bt1, bt2, bt3)
                msg = bot.send_message(message.chat.id, 'Выберите режим игры',
                                       reply_markup=markup)
                bot.register_next_step_handler(msg, gamemode)
                return
            else:
                markup = types.ReplyKeyboardMarkup(
                    one_time_keyboard=True, resize_keyboard=True, row_width=2)
                bt1 = types.KeyboardButton('Легко')
                bt2 = types.KeyboardButton('Сложно')
                bt3 = types.KeyboardButton('<-----')
                markup.add(bt1, bt2, bt3)
                msg = bot.send_message(message.chat.id, 'Выберите уровень сложности',
                                       reply_markup=markup)
                bot.register_next_step_handler(msg, hardness)
                return

        def inp_int(message):
            try:
                n = message.text
                msg, a = check_num(n, message)
                if not (a):
                    bot.register_next_step_handler(msg, inp_int)
                    return
                else:
                    msg = bot.send_message(message.chat.id,
                                           "Отлично! Введённое вами число подходит")
                user_dict[message.chat.id].num1 = n
                try:
                    msg = bot.send_message(message.chat.id, message.from_user.first_name
                                           + ', попробуйте отгадать число')
                except:
                    msg = bot.send_message(message.chat.id, message.from_user.username
                                           + ', попробуйте отгадать число')
                bot.register_next_step_handler(msg, guess)
                return
            except:
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        def guess(message):
            try:
                n = message.text
                msg, a = check_num(n, message)
                if not a:
                    bot.register_next_step_handler(msg, guess)
                    return
                num_guess = list(map(lambda x: int(x), list(str(n))))
                # Число бота
                if user_dict[message.chat.id].name == 'Сложно':
                    user_dict[message.chat.id], bik1, korova1 = gen_num_hard(
                        user_dict, message.chat.id)
                elif user_dict[message.chat.id].name == 'Легко':
                    bik1, korova1 = 0, 0
                    num_gen = gen_num()
                    nerd = list(map(lambda x: int(x), list(
                        str(user_dict[message.chat.id].num1))))
                    for i in range(4):
                        if num_gen[i] == nerd[i]:
                            bik1 += 1
                        elif num_gen[i] in nerd:
                            korova1 += 1
                bik, korova = 0, 0
                for i in range(4):
                    if num_guess[i] == user_dict[message.chat.id].num2[i]:
                        bik += 1
                    elif num_guess[i] in user_dict[message.chat.id].num2:
                        korova += 1

                bikstr = "бык" + bull(bik)
                korovastr = "коров" + ('а' if korova == 1 else cow(korova))

                bikstr1 = "бык" + ('а' if bik1 == 1 else bull(bik1))
                korovastr1 = "коров" + ('у' if korova1 == 1 else cow(korova1))

                if bik == 4:
                    bot.send_message(message.chat.id, "Вы выиграли")
                    bot.send_animation(message.chat.id, win_gif(), None,
                                       'text', reply_markup=back())
                    user_dict[message.chat.id] = None
                    return
                elif bik1 == 4:
                    str_num2 = ''
                    for x in user_dict[message.chat.id].num2:
                        str_num2 += str(x)
                    bot.send_message(
                        message.chat.id, "Вы проиграли компьютеру\n"
                        + "Компьютер загадал число " + str_num2)
                    t = randbelow(4)
                    if t == 0:
                        gif = open('lose1.gif', 'rb')
                    elif t == 1:
                        gif = open('lose2.gif', 'rb')
                    elif t == 2:
                        gif = open('lose3.gif', 'rb')
                    elif t == 3:
                        gif = open('lose4.gif', 'rb')
                    bot.send_animation(message.chat.id, gif, None, 'text',
                                       reply_markup=back())
                    gif.close()
                    user_dict[message.chat.id] = None
                    return
                else:
                    msg = bot.send_message(message.chat.id, "В названном числе " + str(bik) + ' '
                                           + bikstr + ' и ' + str(korova) + ' ' + korovastr)
                    bot.send_message(message.chat.id, "В загаданном вами числе компьютер угадал "
                                     + str(bik1) + ' ' + bikstr1 + ' и ' + str(korova1) + ' ' + korovastr1)
                    try:
                        bot.send_message(message.chat.id, message.from_user.first_name
                                         + ', попробуйте отгадать число')
                    except:
                        bot.send_message(message.chat.id, message.from_user.username
                                         + ', попробуйте отгадать число')
                    bot.register_next_step_handler(msg, guess)
                    return
            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, 'Какая-то ошибка',
                                 reply_markup=back())
                return

        bot.enable_save_next_step_handlers(delay=2)
        bot.load_next_step_handlers()
        bot.polling()

    except Exception as e:
        print(e)
        sleep(0.5)
