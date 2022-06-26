import vk_api.vk_api


class ProfileBot:
    """Отражает сущность профиля-бота ВКонтакте."""

    def __init__(self, access_token):
        """
        :param access_token: токен для доступа к профилю ВКонтакте
        """
        self.vk_session = vk_api.VkApi(token=access_token)
        self.vk_api = self.vk_session.get_api()

    def add_friend(self, friend_id):
        """
        Выполняет добавление в друзья.
        :param friend_id: id пользователя ВКонтакте
        """
        try:
            self.vk_api.friends.add(user_id=friend_id)
        except Exception as exception:
            print(exception)

    def get_friend_requests(self, need_viewed=True):
        """
        Возвращает запросы в друзья.
        :param need_viewed: нужно ли вернуть просмотренные запросы
        :return: словарь с информацией о запросах
        """
        try:
            return self.vk_api.friends.get_requests(need_viewed=need_viewed)
        except Exception as exception:
            print(exception)

    def add_chat_user(self, user_id, chat_id):
        """
        Добавляет пользователя в беседу.
        :param user_id: id пользователя ВКонтакте
        :param chat_id: id беседы ВКонтакте
        """
        try:
            self.vk_api.messages.add_chat_user(user_id=user_id, chat_id=chat_id)
        except Exception as exception:
            print(exception)

    def remove_chat_user(self, user_id, chat_id):
        """
        Удаляет пользователя из беседы.
        :param user_id: id пользователя ВКонтакте
        :param chat_id: id беседы ВКонтакте
        """
        try:
            self.vk_api.messages.remove_chat_user(user_id=user_id, chat_id=chat_id)
        except Exception as exception:
            print(exception)

    def are_friends(self, user_id):
        """
        Проверяет, является ли пользователь другом.
        :param user_id: id пользователя ВКонтакте
        :return: True - да, False - нет
        """
        try:
            are_friends = False
            friend_status = self.vk_api.friends.are_friends(user_ids=[user_id])[0]['friend_status']
            if friend_status == 3:
                are_friends = True
            return are_friends
        except Exception as exception:
            print(exception)
