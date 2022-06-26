import pymysql
from config import database_info


class Database:
    """Применяется для работы с базой данных."""

    def __init__(self, host, user, password, name):
        """
        :param host: хост сервера базы данных
        :param user: имя пользователя
        :param password: пароль пользователя
        :param name: название базы данных
        """
        self.host = host
        self.user = user
        self.password = password
        self.name = name

    def connection(self):
        """
        Создает подключение к базе данных.
        :return: объект соединения
        """
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.name,
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection

    def execute_query(self, query, is_many=False, **values_dict):
        """
        Выполняет запрос к базе данных.
        :param query: строковая переменная, содержащая текст запроса
        :param is_many: много ли нужно вернуть строк
        :param values_dict: словарь со значениями для подстановки
        :return: id последней вставленной записи
        """
        try:
            with self.connection() as connection:
                with connection.cursor() as cursor:

                    print(query, values_dict)
                    cursor.execute(query, values_dict)

                    keyword = query.split(' ')[0].lower()

                    if keyword == 'select':
                        if is_many:
                            return cursor.fetchall()
                        return cursor.fetchone()

                    last_insert_id = connection.insert_id()
                    connection.commit()
                    return last_insert_id

        except Exception as exception:
            print(exception)


# Инициализация объекта базы данных
host = database_info['host']
user = database_info['user']
password = database_info['password']
database_name = database_info['database_name']
database = Database(host, user, password, database_name)
