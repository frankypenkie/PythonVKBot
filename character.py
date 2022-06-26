from database import database
from location import Location


class Character:
    """Отражает сущность персонажа."""

    def __init__(self, player_id):
        """
        :param player_id: id игрока-владельца персонажа
        """
        self.player_id = player_id
        self.first_name = ''
        self.second_name = ''
        self.patronymic = ''
        self.moniker = ''
        self.age = 0
        self.creation_time = None
        self.location = None

    def load(self):
        """
        Извлекает из базы данных информацию о персонаже.
        """
        character_info = database.execute_query('SELECT * '
                                                'FROM StalkerBot.character '
                                                f'WHERE player_id = %(player_id)s',
                                                player_id=self.player_id)
        self.first_name = character_info['first_name']
        self.second_name = character_info['second_name']
        self.patronymic = character_info['patronymic']
        self.moniker = character_info['moniker']
        self.age = character_info['age']

        if character_info['location_id'] is not None:
            self.location = Location(character_info['location_id'])
            self.location.load()

    @staticmethod
    def insert(player_id):
        """
        Вносит персонажа в базу данных.
        :param player_id: id игрока-владельца персонажа
        """
        database.execute_query('INSERT INTO StalkerBot.character(player_id) '
                               'VALUES(%(player_id)s)',
                               player_id=player_id)

    def update(self, updated_property, value):
        """
        Обновляет поле таблицы character в базе данных.
        :param updated_property: название поля
        :param value: значение
        """
        database.execute_query('UPDATE StalkerBot.character '
                               f'SET {updated_property} = %(value)s '
                               'WHERE player_id = %(player_id)s',
                               value=value,
                               player_id=self.player_id)

    def set_location_id(self, value):
        self.update('location_id', value)

    def set_first_name(self, value):
        self.first_name = value
        self.update('first_name', self.first_name)

    def set_second_name(self, value):
        self.second_name = value
        self.update('second_name', self.second_name)

    def set_patronymic(self, value):
        self.patronymic = value
        self.update('patronymic', self.patronymic)

    def set_moniker(self, value):
        self.moniker = value
        self.update('moniker', self.moniker)

    def set_age(self, value):
        if (not value.isdigit()) or (int(value) < 18 or int(value) > 70):
            return 'Возраст должен быть целым числом от 18 до 70'
        self.age = value
        self.update('age', self.age)

    def set_biography(self, value):
        self.update('biography', value)

    def set_appearance(self, value):
        self.update('appearance', value)

    def set_hallmarks(self, value):
        self.update('hallmarks', value)

    def get_biography(self):
        return database.execute_query('SELECT biography '
                                      'FROM StalkerBot.character '
                                      'WHERE player_id = %(player_id)s',
                                      player_id=self.player_id)['biography']

    def get_appearance(self):
        return database.execute_query('SELECT appearance '
                                      'FROM StalkerBot.character '
                                      'WHERE player_id = %(player_id)s',
                                      player_id=self.player_id)['appearance']

    def get_hallmarks(self):
        return database.execute_query('SELECT hallmarks '
                                      'FROM StalkerBot.character '
                                      'WHERE player_id = %(player_id)s',
                                      player_id=self.player_id)['hallmarks']

    def get_general_info(self, need_location=False):
        """
        :param need_location: нужно ли вернуть название локации
        :return: строку с информацией
        """
        info_string = '1. Фамилия:\n' \
                      f'{self.second_name}\n\n' \
                      '2. Имя:\n' \
                      f'{self.first_name}\n\n' \
                      '3. Отчество:\n' \
                      f'{self.patronymic}\n\n' \
                      '4. Прозвище:\n' \
                      f'{self.moniker}\n\n' \
                      '5. Возраст:\n' \
                      f'{self.age}'
        if need_location:
            info_string += '\n\n6. Локация:\n' \
                           f'{self.location.name}'
        return info_string
