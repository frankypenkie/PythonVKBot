from group_bot import GroupBot
from profile_bot import ProfileBot
from config import group_bot_info, profile_bot_info

# Инициализация бота-профиля
access_token = profile_bot_info['access_token']
profile_bot = ProfileBot(access_token)

# Инициализация бота-группы
access_token = group_bot_info['access_token']
group_id = group_bot_info['group_id']
server_group_bot = GroupBot(access_token, group_id, profile_bot)
server_group_bot.main()
