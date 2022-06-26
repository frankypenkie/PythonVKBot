from database import database
from character import Character
from questionnaire import Questionnaire


class Player:
    """Отражает сущность игрока."""

    def __init__(self, vk_id):
        """
        :param vk_id: id пользователя ВКонтакте
        """
        self.id = vk_id
        self.mode_list = []
        self.character = None
        self.messages_permission = 1
        self.admin = 0

    def load(self):
        """
        Извлекает из базы данных информацию об игроке.
        """
        player_info = database.execute_query('SELECT * '
                                             'FROM StalkerBot.player '
                                             'WHERE id = %(id)s',
                                             id=self.id)
        player_rights = database.execute_query('SELECT * '
                                               'FROM StalkerBot.right '
                                               'WHERE player_id = %(player_id)s',
                                               player_id=self.id)
        self.mode_list = []
        for mode in player_info['mode'].split('*'):
            self.mode_list.append(mode.lower())
        self.messages_permission = player_info['messages_permission']
        self.admin = player_rights['admin']
        self.character = Character(self.id)
        self.character.load()

    def is_saved(self):
        """
        Проверяет, есть ли игрок в базе данных.
        :return: True - есть, False - нет
        """
        player_id = database.execute_query('SELECT id '
                                           'FROM StalkerBot.player '
                                           'WHERE id = %(player_id)s',
                                           player_id=self.id)
        if player_id is not None:
            return True
        return False

    def insert(self):
        """
        Вносит в базу данных игрока и связанные с ним сущности.
        """
        database.execute_query('INSERT INTO StalkerBot.player(id) '
                               'VALUES (%(id)s)',
                               id=self.id)
        database.execute_query('INSERT INTO StalkerBot.right(player_id) '
                               'VALUES (%(player_id)s)',
                               player_id=self.id)
        Character.insert(self.id)
        Questionnaire.insert(self.id)

    def update(self, updated_property, value):
        """
        Обновляет поле таблицы player в базе данных.
        :param updated_property: название поля
        :param value: значение
        """
        database.execute_query('UPDATE StalkerBot.player '
                               f'SET {updated_property} = %(value)s '
                               'WHERE id = %(id)s',
                               value=value,
                               id=self.id)

    def set_mode(self, value):
        self.update('mode', value)

    def set_messages_permission(self, value):
        self.messages_permission = value
        self.update('messages_permission', self.messages_permission)

    def set_admin(self, value):
        database.execute_query('UPDATE StalkerBot.right '
                               'SET admin = %(value)s '
                               'WHERE player_id = %(player_id)s',
                               value=value,
                               player_id=self.id)

    def get_questionnaire(self):
        """
        Извлекает из базы данных id анкеты игрока.
        :return: объект анкеты
        """
        questionnaire_id = database.execute_query('SELECT questionnaire_id '
                                                  'FROM StalkerBot.player_questionnaire '
                                                  'WHERE player_id = %(player_id)s',
                                                  player_id=self.id)['questionnaire_id']
        return Questionnaire(questionnaire_id)
