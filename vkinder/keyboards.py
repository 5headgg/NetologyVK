from vkbottle import Keyboard, Text, KeyboardButtonColor, Callback


__all__ = ['search_keyboard', 'get_carousel_keyboard']


def get_carousel_keyboard(user_id: int, last: bool = False, liked: bool = False) -> str:
    like_button = Callback('&#10084;', payload={'cmd': 'like', 'user_id': user_id})
    next_button = Callback('Дальше', payload={'cmd': 'next', 'user_id': user_id})
    url = f'https://vk.com/id{user_id}'
    url_button = Callback('Перейти 🔗', payload={'cmd': 'open_link', 'link': url})

    carousel_keyboard = Keyboard(one_time=False, inline=True)
    if not liked:
        carousel_keyboard.add(like_button, color=KeyboardButtonColor.NEGATIVE)
        if not last:
            carousel_keyboard.add(next_button, color=KeyboardButtonColor.PRIMARY)
        carousel_keyboard.row()
    carousel_keyboard.add(url_button)
    return carousel_keyboard.get_json()


search_button = Text('Поиск 🔎')
search_keyboard = (
    Keyboard(one_time=True, inline=False)
    .add(search_button)
    .get_json()
)
