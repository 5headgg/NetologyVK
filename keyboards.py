from vkbottle import Keyboard, Text, KeyboardButtonColor, Callback

search_keyboard = Keyboard(one_time=True, inline=False).add(Text('Поиск')).get_json()


def get_user_keyboard(user_id, last, liked):
    user_keyboard = Keyboard(one_time=False, inline=True)

    button_like = Callback('лайк ❤️', payload={'cmd': 'like',
                                               'user_id': user_id})
    button_next = Callback('дальше ➡️', payload={'cmd': 'next',
                                                 'user_id': user_id})
    button_open_link = Callback('перейти 👥', payload={'cmd': 'open_link',
                                                      'link': f'https://vk.com/id{user_id}'})

    if not liked:
        return user_keyboard.add(button_open_link).get_json()

    user_keyboard.add(button_like, color=KeyboardButtonColor.NEGATIVE)
    if not last:
        user_keyboard.add(button_next, color=KeyboardButtonColor.PRIMARY)
    return user_keyboard.add(button_open_link).get_json()
