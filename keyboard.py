import json


class Button:
    """
    Отражает сущность кнопки клавиатуры ВКонтакте.
    """

    # Соответствие название цветов
    color_accordance = {'зеленый': 'positive',
                        'красный': 'negative',
                        'синий': 'primary',
                        'белый': 'secondary'}

    def __init__(self, label, color, payload='button', type='text'):
        """
        :param label: надпись на кнопке
        :param color: цвет кнопки
        :param payload: полезная нагрузка
        :param type: тип кнопки
        """
        self.label = label
        self.color = Button.color_accordance[f'{color.lower()}']
        self.payload = payload
        self.type = type

    def get(self):
        """
        Возвращает словарь для конвертации в json.
        """
        return {
            'action': {
                'type': self.type,
                'payload': f'{{"command": "{self.payload}"}}',
                'label': f'{self.label}'
            },
            'color': f'{self.color}'
        }


class Keyboard:

    def __init__(self, buttons_list=None, one_time=False, inline=False):
        """
        :param buttons_list: список с кнопками клавиатуры
        :param one_time: нужно ли показать клавиатуру один раз
        :param inline: нужно ли inline отображение
        """
        if buttons_list is None:
            self.buttons_list = list()
        else:
            self.buttons_list = buttons_list
        self.one_time = one_time
        self.inline = inline

    def get(self):
        """
        Формирует из словаря json-объект клавиатуры.
        :return: json-объект
        """
        keyboard = {'one_time': self.one_time, 'inline': self.inline, 'buttons': []}
        if self.buttons_list is not None:
            for line in self.buttons_list:
                keyboard['buttons'].append([])
                for button in line:
                    line_index = len(keyboard['buttons']) - 1
                    keyboard['buttons'][line_index].append(button.get())
        return json.dumps(keyboard, ensure_ascii=False)

    def add_button(self, button):
        """
        Добавляет в клавиатуру кнопку на новую строку.
        :param button: объект кнопки
        """
        self.buttons_list.append([button])
