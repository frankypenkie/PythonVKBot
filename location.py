from database import database


class Location:
    """Отражает сущность локации."""

    def __init__(self, location_id):
        """
        :param location_id: id локации
        """
        self.id = location_id
        self.name = ''
        self.chat_id = 0
        self.nearby_locations = []

    def load(self):
        """
        Извлекает из базы данных информацию о локации.
        """
        location_info = database.execute_query('SELECT * '
                                               'FROM StalkerBot.location '
                                               'WHERE id = %(id)s',
                                               id=self.id)
        self.name = location_info['name']
        self.chat_id = location_info['chat_id']

        for location_id in location_info['nearby_locations'].split(' '):
            self.nearby_locations.append(location_id)

    @staticmethod
    def get_location_by_name(location_name):
        """
        Возвращает id локации из базы данных по ее названию.
        :param location_name: название локации
        :return: id локации из базы данных
        """
        location_id = database.execute_query('SELECT id '
                                             'FROM StalkerBot.location '
                                             'WHERE name = %(name)s',
                                             name=location_name)
        if location_id is not None:
            location = Location(location_id['id'])
            location.load()
            return location
