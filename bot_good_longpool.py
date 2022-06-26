from vk_api.bot_longpoll import VkBotLongPoll


class BotGoodLongPoll(VkBotLongPoll):
    """Необходим для нормальной работы метода listen класса VkBotLongPoll"""
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as exception:
                print(exception)
