import vk_api.vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotEvent, VkBotMessageEvent
from bot_good_longpool import BotGoodLongPoll
from keyboard import Button, Keyboard
from player import Player
from questionnaire import Questionnaire
from location import Location
from config import start_message, create_character_message, reset_code, admin_code
import json
import random


class GroupBot:
    """Отражает сущность группы-бота ВКонтакте."""

    def __init__(self, access_token, group_id, profile_bot):
        """
        :param access_token: токен для доступа к группе ВКонтакте
        :param group_id: id группы из ВКонтакте
        """
        self.vk_session = vk_api.VkApi(token=access_token)
        self.longpoll = BotGoodLongPoll(self.vk_session, group_id)
        self.vk_api = self.vk_session.get_api()
        self.profile_bot = profile_bot

    def main(self):
        """
        Запускает цикл прослушивания событий группы.
        Отправляет ответы пользователю.
        """
        for event in self.longpoll.listen():
            try:
                # Инициализация переменной vk_user_id и присвоение ей значения в зависимости от класса события.
                vk_user_id = 0
                if event.__class__ is VkBotMessageEvent:
                    vk_user_id = event.object.message['from_id']
                if event.__class__ is VkBotEvent:
                    vk_user_id = event.object['user_id']

                # Инициализация игрока
                player = Player(vk_user_id)
                if not player.is_saved():
                    player.insert()
                player.load()

                # Инициализация главных кнопок и клавиатур
                go_back_btn = Button('Назад', 'Красный', 'go_back')
                view_character_info_btn = Button('Информация о персонаже', 'Синий', 'view_character_info')
                go_over_btn = Button('Переход', 'Синий', 'go_over')
                moderation_options_btn = Button('Администрирование', 'Синий', 'moderation_options')
                player_main_keyboard = Keyboard([
                    [view_character_info_btn],
                    [go_over_btn]
                ])
                moder_main_keyboard = Keyboard([
                    [view_character_info_btn],
                    [go_over_btn],
                    [moderation_options_btn]
                ])

                # Инициализация главной клавиатуры в зависимости от прав игрока
                main_keyboard = player_main_keyboard
                if player.admin:
                    main_keyboard = moder_main_keyboard

                if event.type == VkBotEventType.MESSAGE_NEW:

                    # Инициализация клавиатуры опций модератора
                    check_questionnaire_btn = Button('Проверка', 'Синий', 'check_questionnaire')
                    moderation_options_keyboard = Keyboard([
                        [check_questionnaire_btn],
                        [go_back_btn]
                    ])

                    # Инициализация клавиатуры просмотра информации
                    general_info_btn = Button('Общая', 'Зеленый', 'general_info')
                    biography_btn = Button('Биография', 'Зеленый', 'biography')
                    appearance_btn = Button('Внешность', 'Зеленый', 'appearance')
                    hallmarks_btn = Button('Отличительные черты', 'Зеленый', 'hallmarks')
                    info_keyboard = Keyboard([
                        [general_info_btn, biography_btn, appearance_btn],
                        [hallmarks_btn],
                        [go_back_btn]
                    ])

                    # Инициализация переменных с информацией о сообщении
                    message_object = event.object.message
                    message_text = message_object['text']
                    command = str()
                    if 'payload' in message_object:
                        command = str(json.loads(message_object['payload'])['command'])

                    if message_text == reset_code:
                        questionnaire = player.get_questionnaire()
                        questionnaire.set_formed(False)
                        questionnaire.set_confirmed(False)
                        player.set_mode('start*first_messages')
                        player.load()
                        command = 'start'
                    elif message_text == admin_code:
                        player.set_mode('default')
                        player.set_admin(True)
                        self.send_message(player.id, 'Теперь вы администратор.', moder_main_keyboard)

                    if message_text.lower() == 'скинуть':
                        player.set_mode('start*first_messages')
                        self.send_message(player.id, 'Клавиатура и режим были сброшены.')

                    if not self.profile_bot.are_friends(vk_user_id):

                        # Проверка наличия запроса в друзья от игрока
                        friend_requests_ids = self.profile_bot.get_friend_requests()['items']
                        is_request_sent = False
                        for user_id in friend_requests_ids:
                            if player.id == user_id:
                                is_request_sent = True
                                break

                        if is_request_sent:
                            self.profile_bot.add_friend(player.id)
                        else:
                            keyboard = Keyboard()
                            if f'{player.mode_list[0]}*{player.mode_list[1]}' == 'start*first_messages':
                                keyboard.add_button(Button('Начать', 'Синий', 'start'))
                            self.send_message(player.id, 'Чтобы продолжить необходимо добавить в друзья данный профиль: '
                                                         'https://vk.com/tommybarista', keyboard)

                    elif player.mode_list[0] == 'default':

                        if command == 'view_character_info':
                            player.set_mode('view_character_info')
                            self.send_message(player.id, 'Какую информацию вы хотите посмотреть?', info_keyboard)

                        elif command == 'go_over':
                            # Формирование клавиатуры с соседними локациями персонажа.
                            keyboard = Keyboard()
                            for location_id in player.character.location.nearby_locations:
                                location = Location(location_id)
                                location.load()
                                location_btn = Button(location.name, 'Зеленый', location_id)
                                keyboard.add_button(location_btn)
                            keyboard.add_button(go_back_btn)
                            player.set_mode('choice_location_to_go_over')
                            self.send_message(player.id, 'Выберите локацию.', keyboard)

                        elif command == 'moderation_options':
                            player.set_mode('moderation')
                            self.send_message(player.id, 'Опции администратора.', moderation_options_keyboard)

                    elif player.mode_list[0] == 'view_character_info':

                        if command == 'general_info':
                            self.send_message(player.id, player.character.get_general_info(need_location=True), info_keyboard)

                        elif command == 'biography':
                            self.send_message(player.id, player.character.get_biography(), info_keyboard)

                        elif command == 'appearance':
                            self.send_message(player.id, player.character.get_appearance(), info_keyboard)

                        elif command == 'hallmarks':
                            self.send_message(player.id, player.character.get_hallmarks(), info_keyboard)

                        elif command == 'go_back':
                            player.set_mode('default')
                            self.send_message(player.id, 'Главное меню.', main_keyboard)

                    elif player.mode_list[0] == 'choice_location_to_go_over':

                        if command == 'go_back':
                            player.set_mode('default')
                            self.send_message(player.id, 'Главное меню.', main_keyboard)
                        elif command != '':
                            self.profile_bot.remove_chat_user(player.id, player.character.location.chat_id)
                            location = Location(command)
                            location.load()
                            player.character.set_location_id(location.id)
                            self.profile_bot.add_chat_user(player.id, location.chat_id)
                            player.set_mode('default')
                            self.send_message(player.id, f'Вы сменили локацию на {location.name}.', main_keyboard)

                    elif player.mode_list[0] == 'moderation':

                        if command == 'check_questionnaire':
                            questionnaire = Questionnaire.get_questionnaire_for_check()
                            if questionnaire is None:
                                self.send_message(player.id, 'Анкет для проверки нет.', moderation_options_keyboard)
                            else:
                                # Инициализация клавиатуры и кнопок для вердикта по анкете
                                approve_questionnaire_btn = Button('Одобрить', 'Зеленый', 'approve_questionnaire')
                                reject_questionnaire_btn = Button('Отказать', 'Красный', 'reject_questionnaire')
                                verdict_questionnaire_keyboard = Keyboard([
                                    [reject_questionnaire_btn, approve_questionnaire_btn]
                                ])
                                player.set_mode('moderation*check_questionnaire')
                                questionnaire.set_checker(player.id)
                                owner = Player(questionnaire.get_owner_id())
                                owner.load()
                                self.send_message(player.id, owner.character.get_general_info())
                                self.send_message(player.id, '\n\n6. Биография:\n' +
                                                  owner.character.get_biography())
                                self.send_message(player.id, '\n\n7. Внешность:\n' +
                                                  owner.character.get_appearance())
                                self.send_message(player.id, '\n\n8. Отличительные черты:\n' +
                                                  owner.character.get_hallmarks(),
                                                  verdict_questionnaire_keyboard)

                        elif command == 'go_back':
                            player.set_mode('default')
                            self.send_message(player.id, 'Обычный режим.', main_keyboard)

                        elif player.mode_list[1] == 'check_questionnaire':

                            if command == 'approve_questionnaire':
                                north_locations_btn = Button('Север', 'Зеленый', 'north')
                                central_locations_btn = Button('Центр', 'Зеленый', 'central')
                                east_locations_btn = Button('Восток', 'Зеленый', 'east')
                                west_locations_btn = Button('Запад', 'Зеленый', 'west')
                                south_locations_btn = Button('Юг', 'Зеленый', 'south')
                                keyboard = Keyboard([
                                    [north_locations_btn],
                                    [west_locations_btn, central_locations_btn, east_locations_btn],
                                    [south_locations_btn]
                                ])
                                player.set_mode('moderation*check_questionnaire*choice_side')
                                self.send_message(player.id, 'Выберите сторону.', keyboard)

                            elif command == 'reject_questionnaire':
                                questionnaire = Questionnaire.get_questionnaire_by_checker(player.id)
                                questionnaire.delete_checker()
                                owner = Player(questionnaire.get_owner_id())
                                owner.set_mode('start')
                                create_character_btn = Button('Создать персонажа', 'Зеленый', 'create_character')
                                keyboard = Keyboard([[create_character_btn]])
                                self.send_message(questionnaire.get_owner_id(), 'Вам было отказано по анкете.', keyboard)

                            elif player.mode_list[2] == 'choice_side':

                                player.set_mode('moderation*check_questionnaire*choice_location')
                                go_back_btn.payload = 'approve_questionnaire'
                                keyboard = Keyboard()

                                if command == 'north':
                                    generators_btn = Button('Генераторы', 'Зеленый', 'choice_location')
                                    chernobyl_nuclear_power_plant_btn = Button('ЧАЭС', 'Зеленый', 'choice_location')
                                    zaton_btn = Button('Затон', 'Зеленый', 'choice_location')
                                    hospital_btn = Button('Госпиталь', 'Зеленый', 'choice_location')
                                    central_pripyat_btn = Button('Центральная Припять', 'Зеленый', 'choice_location')
                                    jupiters_surroundings_btn = Button('Окрестности Юпитера', 'Зеленый', 'choice_location')
                                    keyboard = Keyboard([
                                        [generators_btn, chernobyl_nuclear_power_plant_btn, zaton_btn],
                                        [hospital_btn],
                                        [central_pripyat_btn],
                                        [jupiters_surroundings_btn],
                                        [go_back_btn]
                                    ])

                                elif command == 'west':
                                    amber_btn = Button('Янтарь', 'Зеленый', 'choice_location')
                                    dead_city_btn = Button('Мёртвый город', 'Зеленый', 'choice_location')
                                    limansk_btn = Button('Лиманск', 'Зеленый', 'choice_location')
                                    keyboard = Keyboard([
                                        [amber_btn, limansk_btn],
                                        [dead_city_btn],
                                        [go_back_btn]
                                    ])

                                elif command == 'central':
                                    army_depots_btn = Button('Армейские склады', 'Зеленый', 'choice_location')
                                    bar_btn = Button('Бар "100 рентген"', 'Зеленый', 'choice_location')
                                    wild_territory_btn = Button('Дикая территория', 'Зеленый', 'choice_location')
                                    red_forest_btn = Button('Рыжий лес', 'Зеленый', 'choice_location')
                                    radar_btn = Button('Радар', 'Зеленый', 'choice_location')
                                    keyboard = Keyboard([
                                        [red_forest_btn, radar_btn],
                                        [army_depots_btn],
                                        [bar_btn],
                                        [wild_territory_btn],
                                        [go_back_btn]
                                    ])

                                elif command == 'east':
                                    vehicles_cemetery_btn = Button('Кладбище техники', 'Зеленый', 'choice_location')
                                    dark_valley_btn = Button('Тёмная долина', 'Зеленый', 'choice_location')
                                    eastern_pripyat_btn = Button('Восточная Припять', 'Зеленый', 'choice_location')
                                    keyboard = Keyboard([
                                        [vehicles_cemetery_btn],
                                        [dark_valley_btn],
                                        [eastern_pripyat_btn],
                                        [go_back_btn]
                                    ])

                                elif command == 'south':
                                    cordon_btn = Button('Кордон', 'Зеленый', 'choice_location')
                                    swamps_btn = Button('Болота', 'Зеленый', 'choice_location')
                                    dark_hollow_btn = Button('Тёмная лощина', 'Зеленый', 'choice_location')
                                    agro_industry_btn = Button('НИИ Агропром', 'Зеленый', 'choice_location')
                                    dump_btn = Button('Свалка', 'Зеленый', 'dump')
                                    keyboard = Keyboard([
                                        [cordon_btn, swamps_btn, dump_btn],
                                        [agro_industry_btn, dark_hollow_btn],
                                        [go_back_btn]
                                    ])

                                self.send_message(player.id, 'Выберите локацию.', keyboard)

                            elif player.mode_list[2] == 'choice_location':

                                location = Location.get_location_by_name(message_text)
                                if location is not None:
                                    questionnaire = Questionnaire.get_questionnaire_by_checker(player.id)
                                    questionnaire.set_confirmed(True)
                                    questionnaire.delete_checker()
                                    location = Location.get_location_by_name(message_text)
                                    owner = Player(questionnaire.get_owner_id())
                                    owner.load()
                                    owner.character.set_location_id(location.id)
                                    self.profile_bot.add_chat_user(owner.id, location.chat_id)
                                    self.send_message(owner.id, 'Вам была одобрена анкета.', player_main_keyboard)
                                    player.set_mode('moderation')
                                    self.send_message(player.id, 'Вы одобрили анкету.', moderation_options_keyboard)

                    elif player.mode_list[0] == 'start':

                        if player.mode_list[1] == 'first_messages':

                            if command == 'start':
                                create_character_btn = Button('Создать персонажа', 'Зеленый', 'create_character')
                                keyboard = Keyboard([[create_character_btn]])
                                self.send_message(player.id, start_message, keyboard)
                            elif command == 'create_character':
                                continue_create_character_btn = Button('Продолжить', 'Зеленый', 'continue_create_character')
                                keyboard = Keyboard([[continue_create_character_btn]])
                                self.send_message(player.id, create_character_message, keyboard)
                            elif command == 'continue_create_character':
                                player.set_mode('start*get_second_name')
                                self.send_message(player.id, 'Фамилия:')

                        elif player.mode_list[1] == 'get_second_name':

                            if len(message_text) > 50:
                                self.send_message(player.id,
                                                  'Фамилия превышает 50 символов.\n\n'
                                                  'Повторите ввод:')
                            else:
                                player.character.set_second_name(message_text)
                                player.set_mode('start*get_first_name')
                                self.send_message(player.id, 'Имя:')

                        elif player.mode_list[1] == 'get_first_name':

                            if len(message_text) > 50:
                                self.send_message(player.id,
                                                  'Имя превышает 50 символов.\n\n'
                                                  'Повторите ввод:')
                            else:
                                player.character.set_first_name(message_text)
                                player.set_mode('start*get_patronymic')
                                self.send_message(player.id, 'Отчество:')

                        elif player.mode_list[1] == 'get_patronymic':

                            if len(message_text) > 50:
                                self.send_message(player.id,
                                                  'Отчество превышает 50 символов.\n\n'
                                                  'Повторите ввод:')
                            else:
                                player.character.set_patronymic(message_text)
                                player.set_mode('start*get_moniker')
                                self.send_message(player.id, 'Прозвище:')

                        elif player.mode_list[1] == 'get_moniker':

                            if len(message_text) > 50:
                                self.send_message(player.id,
                                                  'Прозвище превышает 50 символов.\n\n'
                                                  'Повторите ввод:')
                            else:
                                player.character.set_moniker(message_text)
                                player.set_mode('start*get_age')
                                self.send_message(player.id, 'Возраст:')

                        elif player.mode_list[1] == 'get_age':

                            player_answer = player.character.set_age(message_text)
                            if player_answer is not None:
                                self.send_message(player.id, player_answer)
                            else:
                                player.set_mode('start*get_biography')
                                self.send_message(player.id, 'Биография:')

                        elif player.mode_list[1] == 'get_biography':

                            if len(message_text) > 4000:
                                self.send_message(player.id,
                                                  'Биография превышает 4000 символов.'
                                                  '\n\nПовторите ввод:')
                            else:
                                player.character.set_biography(message_text)
                                player.set_mode('start*get_appearance')
                                self.send_message(player.id, 'Внешность:')

                        elif player.mode_list[1] == 'get_appearance':
                            if len(message_text) > 4000:
                                self.send_message(player.id,
                                                  'Описание внешности превышает 4000 символов.\n\n'
                                                  'Повторите ввод:')
                            else:
                                player.character.set_appearance(message_text)
                                player.set_mode('start*get_hallmarks')
                                self.send_message(player.id, 'Отличительные признаки:')

                        elif player.mode_list[1] == 'get_hallmarks':

                            if len(message_text) > 4000:
                                self.send_message(player.id,
                                                  'Описание отличительных превышает 4000 символов.\n\n'
                                                  'Повторите ввод:')
                            else:
                                player.character.set_hallmarks(message_text)
                                player.set_mode('start*send_choice')
                                start_over_btn = Button('Начать заново', 'Красный', 'start_over')
                                send_questionnaire_btn = Button('Отправить', 'Зеленый', 'send_questionnaire')
                                send_choice_keyboard = Keyboard([
                                    [start_over_btn, send_questionnaire_btn]
                                ])
                                self.send_message(player.id, 'Анкета выглядит следующим образом:\n\n' +
                                                  player.character.get_general_info())
                                self.send_message(player.id, '\n\n6. Биография:\n' +
                                                  player.character.get_biography())
                                self.send_message(player.id, '\n\n7. Внешность:\n' +
                                                  player.character.get_appearance())
                                self.send_message(player.id, '\n\n8. Отличительные черты:\n' +
                                                  player.character.get_hallmarks() +
                                                  '\n\nВы хотите отправить анкету на проверку или начать заново?',
                                                  send_choice_keyboard)

                        elif player.mode_list[1] == 'send_choice':

                            if command == 'start_over':
                                player.set_mode('start*get_second_name')
                                self.send_message(player.id, 'Фамилия:')
                            elif command == 'send_questionnaire':
                                questionnaire = player.get_questionnaire()
                                questionnaire.set_formed(True)
                                questionnaire.set_sending_time()
                                player.set_mode('default')
                                self.send_message(player.id, 'Анкета была отправлена на проверку. Ожидайте ответа модератора.')

                elif event.type == VkBotEventType.MESSAGE_ALLOW:
                    questionnaire = player.get_questionnaire()
                    questionnaire.load()
                    keyboard = Keyboard()
                    if questionnaire.confirmed:
                        keyboard = main_keyboard
                    elif not questionnaire.formed:
                        player.set_mode('start*first_messages')
                        keyboard = Keyboard([[Button('Начать', 'Синий', 'start')]])
                    self.send_message(player.id, 'Мы рады, что вы снова с нами!', keyboard)
                    player.set_messages_permission(True)

                elif event.type == VkBotEventType.MESSAGE_DENY:
                    player.set_messages_permission(False)

            except Exception as exception:
                print(exception)

    def send_message(self, peer_id, message, keyboard=Keyboard()):
        """
        Отправляет сообщение пользователю ВКонтакте.
        :param peer_id: id получателя
        :param message: сообщение
        :param keyboard: клавиатура
        """
        try:
            self.vk_api.messages.send(peer_id=peer_id,
                                      message=message,
                                      keyboard=keyboard.get(),
                                      random_id=random.randint(0, 2048))
        except Exception as exception:
            print(exception)
