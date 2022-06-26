from datetime import datetime
from database import database


class Questionnaire:

    def __init__(self, questionnaire_id):
        """
        :param questionnaire_id: id анкеты
        """
        self.id = questionnaire_id
        self.formed = 0
        self.confirmed = 0
        self.sending_time = '1000-01-01 00:00:00'

    def load(self):
        """
        Извлекает из базы данных информацию об анкете.
        """
        questionnaire_info = database.execute_query('SELECT * '
                                                    'FROM StalkerBot.questionnaire '
                                                    'WHERE id = %(id)s',
                                                    id=self.id)
        self.formed = questionnaire_info['formed']
        self.confirmed = questionnaire_info['confirmed']
        self.sending_time = questionnaire_info['sending_time']

    @staticmethod
    def insert(player_id):
        """
        Вносит анкету в базу данных.
        :param player_id: id игрока-владельца
        """
        questionnaire_id = database.execute_query('INSERT INTO StalkerBot.questionnaire() VALUES()')
        database.execute_query('INSERT INTO StalkerBot.player_questionnaire(player_id, '
                               'questionnaire_id, player_role) '
                               'VALUES(%(player_id)s, %(questionnaire_id)s, "owner")',
                               player_id=player_id,
                               questionnaire_id=questionnaire_id)

    def update(self, updated_property, value):
        """
        Обновляет поле таблицы questionnaire в базе данных.
        :param updated_property: название поля
        :param value: значение
        """
        database.execute_query('UPDATE StalkerBot.questionnaire '
                               f'SET {updated_property} = %(value)s '
                               'WHERE id = %(id)s',
                               value=value,
                               id=self.id)

    def set_formed(self, value):
        self.formed = value
        self.update('formed', value)

    def set_confirmed(self, value):
        self.confirmed = value
        self.update('confirmed', value)

    def set_sending_time(self):
        self.sending_time = datetime.now().replace(microsecond=0)
        self.update('sending_time', self.sending_time)

    def set_checker(self, checker_id):
        """
        Устанавливает проверяющего анкете.
        :param checker_id: id проверяющего
        """
        database.execute_query('INSERT INTO StalkerBot.player_questionnaire '
                               '(player_id, questionnaire_id, player_role) '
                               'VALUES (%(player_id)s, %(questionnaire_id)s, "checker")',
                               player_id=checker_id,
                               questionnaire_id=self.id)

    def delete_checker(self):
        """
        Удаляет проверяющего у анкеты.
        """
        database.execute_query('DELETE FROM StalkerBot.player_questionnaire '
                               'WHERE questionnaire_id = %(questionnaire_id)s '
                               'AND player_role = "checker"',
                               questionnaire_id=self.id)

    def get_checker_id(self):
        """
        Извлекает из базы данных id проверяющего.
        :return: id проверяющего или None, если его нет
        """
        checker_id = database.execute_query('SELECT player_id '
                                            'FROM StalkerBot.player_questionnaire '
                                            'WHERE questionnaire_id = %(questionnaire_id)s '
                                            'AND player_role = "checker"',
                                            questionnaire_id=self.id)
        if checker_id is not None:
            return checker_id['player_id']

    def get_owner_id(self):
        """
        Извлекает из базы данных id владельца.
        :return: id владельца
        """
        return database.execute_query('SELECT player_id '
                                      'FROM StalkerBot.player_questionnaire '
                                      'WHERE questionnaire_id = %(questionnaire_id)s '
                                      'AND player_role = "owner"',
                                      questionnaire_id=self.id)['player_id']

    @staticmethod
    def get_questionnaire_for_check():
        """
        Извлекает из базы данных информацию об анкетах.
        :return: None, если информации нет, объект анкеты, если есть
        """
        questionnaires_info = database.execute_query('SELECT * '
                                                     'FROM StalkerBot.questionnaire '
                                                     'WHERE formed = 1 AND confirmed = 0 '
                                                     'ORDER BY sending_time ASC',
                                                     True)
        if questionnaires_info is not None:
            for questionnaire_info in questionnaires_info:
                questionnaire = Questionnaire(questionnaire_info['id'])
                questionnaire.load()
                if questionnaire.get_checker_id() is None:
                    return questionnaire

    @staticmethod
    def get_questionnaire_by_checker(checker_id):
        """
        Возвращает id анкеты из базы данных.
        :param checker_id: id проверяющего из базы данных
        :return: id анкеты
        """
        questionnaire_id = database.execute_query('SELECT questionnaire_id '
                                                  'FROM StalkerBot.player_questionnaire '
                                                  'WHERE player_id = %(player_id)s '
                                                  'AND player_role = "checker"',
                                                  player_id=checker_id)['questionnaire_id']
        questionnaire = Questionnaire(questionnaire_id)
        questionnaire.load()
        return questionnaire
