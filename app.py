import json
import sqlite3
from datetime import datetime
from googletrans import Translator

translator = Translator()


def translate_text(text, dest='en'):
    try:
        return text


def init_db():
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            cat TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_num INTEGER,
            items TEXT,
            total INTEGER,
            status TEXT,
            date TEXT,
            lang TEXT DEFAULT 'ru'
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            lang TEXT DEFAULT 'ru',
            cart TEXT DEFAULT '[]',
            stage TEXT DEFAULT 'main'
        )
    ''')
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        items = [
            ('Чизбургер', 189, 'Бургеры'),
            ('Биг Бургер', 249, 'Бургеры'),
            ('Картошка', 99, 'Закуски'),
            ('Наггетсы', 149, 'Закуски'),
            ('Цезарь', 179, 'Салаты'),
            ('Греческий', 159, 'Салаты'),
            ('Кола', 89, 'Напитки'),
            ('Кофе', 129, 'Напитки'),
            ('Мороженое', 79, 'Десерты'),
            ('Чизкейк', 199, 'Десерты')
        ]
        cur.executemany('INSERT INTO menu (name, price, cat) VALUES (?, ?, ?)', items)
        conn.commit()
    conn.close()


def get_db():
    conn.row_factory = sqlite3.Row
    return conn


def get_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cur.fetchone()
    conn.close()
    if not user:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (user_id, lang, cart, stage) VALUES (?, ?, ?, ?)', (user_id, 'ru', '[]', 'main'))
        conn.commit()
        conn.close()
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cur.fetchone()
        conn.close()
    return user


def update_user(user_id, **kwargs):
    conn = get_db()
    cur = conn.cursor()
    for key, value in kwargs.items():
        cur.execute(f'UPDATE users SET {key} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()


def get_menu(cat=None):
    conn = get_db()
    cur = conn.cursor()
    if cat:
        cur.execute('SELECT id, name, price FROM menu WHERE cat = ?', (cat,))
    else:
        cur.execute('SELECT id, name, price, cat FROM menu')
    result = cur.fetchall()
    conn.close()
    return result


def get_cats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT cat FROM menu')
    return [row[0] for row in cur.fetchall()]


def add_order(table_num, items_text, total, lang='ru'):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO orders (table_num, items, total, status, date, lang) VALUES (?, ?, ?, ?, ?, ?)',
                (table_num, items_text, total, 'new', datetime.now().isoformat(), lang))
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def get_orders():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, table_num, items, total, status FROM orders ORDER BY date DESC')
    return cur.fetchall()


def update_order(order_id, status):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()


def add_item(name, price, cat):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO menu (name, price, cat) VALUES (?, ?, ?)', (name, price, cat))
    item_id = cur.lastrowid
    conn.commit()
    conn.close()
    return item_id


def update_item(item_id, name, price, cat):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE menu SET name = ?, price = ?, cat = ? WHERE id = ?', (name, price, cat, item_id))
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM menu WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()


def get_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'done'")
    done = cur.fetchone()[0]
    cur.execute("SELECT SUM(total) FROM orders WHERE status = 'done'")
    money = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'new'")
    new = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM menu")
    items = cur.fetchone()[0]
    conn.close()
    return {'done': done, 'new': new, 'money': money, 'items': items}


BANNER_IMAGE_ID = '1030494/858fd810c8d7a4a1ade3'

TEXTS_RU = {
    'welcome': '🍔 Добро пожаловать во "ВКУСНО И БЫСТРО"!\nВыберите категорию:',
    'cart': '🛒 ВАША КОРЗИНА:\n\n',
    'cart_empty': 'Корзина пуста.',
    'cart_clear': 'Корзина очищена!',
    'order_prompt': '📋 Напишите номер стола (от 1 до 50):',
    'order_success': '✅ Заказ #{} принят! Спасибо!',
    'order_error': 'Номер стола должен быть от 1 до 50.',
    'added': '✅ {} добавлен в корзину!',
    'help': '🍔 КОМАНДЫ:\nБургеры, Закуски, Салаты, Напитки, Десерты\nКорзина, Очистить, Заказать, Назад\nEnglish - сменить язык',
    'stats': '📊 СТАТИСТИКА:\n\n✅ Заказов: {}\n🟡 Новых: {}\n💰 Выручка: {}₽\n🍔 Блюд: {}',
    'orders_list': '📦 ЗАКАЗЫ:\n\n',
    'order_done': '✅ Заказ #{} выполнен!',
    'menu': '📋 МЕНЮ:\n\n',
    'item_added': '✅ Блюдо добавлено!',
    'item_updated': '✅ Блюдо обновлено!',
    'item_deleted': '🗑️ Блюдо удалено!',
    'enter_name': 'Введите название блюда:',
    'enter_price': 'Введите цену:',
    'enter_cat': 'Введите категорию:',
    'lang_changed_ru': '🌐 Язык: русский',
    'lang_changed_en': '🌐 Language: English',
    'unknown': 'Не понял. Доступные команды: Бургеры, Закуски, Салаты, Напитки, Десерты, Корзина, Очистить, Заказать, Назад',
    'back': 'Главное меню. Выберите категорию:',
    'select_category': '🍽️ {}:\n',
    'total': '💸 Итого: {}₽',
    'order_confirm': 'Скажите "Заказать" или "Очистить"',
    'admin_activated': '🔐 АДМИН-ПАНЕЛЬ\n\nМеню\nДобавить\nРедактировать [ID]\nУдалить [ID]\nЗаказы\nВыполнить [ID]\nСтатистика\nВыйти',
    'admin_exit': 'Выход из админ-панели'
}

sessions = {}


def handler(event, context):
    init_db()

    req = event.get('request', {})
    session = event.get('session', {})
    user_id = session.get('user_id', 'anonymous')
    text = req.get('original_utterance', '').lower().strip()
    is_new = session.get('new', False)

    if user_id not in sessions:
        sessions[user_id] = {'admin': False, 'temp': {}, 'current_cat': None}

    user = get_user(user_id)
    lang = user['lang']
    cart = json.loads(user['cart'])
    stage = user['stage']
    admin = sessions[user_id]['admin']
    temp = sessions[user_id]['temp']
    current_cat = sessions[user_id].get('current_cat')

    if lang == 'en':
        t = {k: translate_text(v, 'en') for k, v in TEXTS_RU.items()}
    else:
        t = TEXTS_RU

    if admin:
        if 'выйти' in text:
            sessions[user_id]['admin'] = False
            update_user(user_id, stage='main')
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['admin_exit'], 'end_session': False}}
        if 'статистика' in text:
            stats = get_stats()
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['stats'].format(stats['done'], stats['new'], stats['money'], stats['items']),
                                 'end_session': False}}
        if 'заказы' in text:
            orders = get_orders()
            if not orders:
                return {'version': event['version'], 'session': session,
                        'response': {'text': 'Нет заказов', 'end_session': False}}
            msg = t['orders_list']
            for o in orders[:10]:
                msg += f'ID:{o["id"]} | Стол:{o["table_num"]} | {o["total"]}₽ | {"✅ Готов" if o["status"] == "done" else "🟡 Новый"}\n'
            return {'version': event['version'], 'session': session, 'response': {'text': msg, 'end_session': False}}
        if 'выполнить' in text or 'готов' in text:
            import re
            nums = re.findall(r'\d+', text)
            if nums:
                update_order(int(nums[0]), 'done')
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['order_done'].format(nums[0]), 'end_session': False}}
        if 'меню' in text:
            cats = get_cats()
            msg = t['menu']
            for cat in cats:
                items = get_menu(cat)
                msg += f'\n{cat}:\n'
                for item in items:
                    msg += f'  {item["id"]}. {item["name"]} - {item["price"]}₽\n'
            return {'version': event['version'], 'session': session,
                    'response': {'text': msg[:1000], 'end_session': False}}
        if 'добавить' in text:
            sessions[user_id]['temp'] = {'stage': 'add_name'}
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['enter_name'], 'end_session': False}}
        if 'редактировать' in text:
            import re
            nums = re.findall(r'\d+', text)
            if nums:
                sessions[user_id]['temp'] = {'edit_id': int(nums[0]), 'stage': 'edit_name'}
                return {'version': event['version'], 'session': session,
                        'response': {'text': f'Редактируем ID {nums[0]}. {t["enter_name"]}', 'end_session': False}}
        if 'удалить' in text:
            import re
            nums = re.findall(r'\d+', text)
            if nums:
                delete_item(int(nums[0]))
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['item_deleted'], 'end_session': False}}

        stage_admin = temp.get('stage', '')
        if stage_admin == 'add_name':
            temp['name'] = text
            temp['stage'] = 'add_price'
            sessions[user_id]['temp'] = temp
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['enter_price'], 'end_session': False}}
        if stage_admin == 'add_price':
            try:
                temp['price'] = int(text)
                temp['stage'] = 'add_cat'
                sessions[user_id]['temp'] = temp
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['enter_cat'], 'end_session': False}}
            except:
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['enter_price'], 'end_session': False}}
        if stage_admin == 'add_cat':
            add_item(temp['name'], temp['price'], text)
            sessions[user_id]['temp'] = {}
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['item_added'], 'end_session': False}}
        if stage_admin == 'edit_name':
            temp['edit_name'] = text
            temp['stage'] = 'edit_price'
            sessions[user_id]['temp'] = temp
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['enter_price'], 'end_session': False}}
        if stage_admin == 'edit_price':
            try:
                temp['edit_price'] = int(text)
                temp['stage'] = 'edit_cat'
                sessions[user_id]['temp'] = temp
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['enter_cat'], 'end_session': False}}
            except:
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['enter_price'], 'end_session': False}}
        if stage_admin == 'edit_cat':
            update_item(temp['edit_id'], temp['edit_name'], temp['edit_price'], text)
            sessions[user_id]['temp'] = {}
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['item_updated'], 'end_session': False}}

        return {'version': event['version'], 'session': session,
                'response': {'text': t['admin_activated'], 'end_session': False}}

    if text == 'активироватьадминпанель67':
        sessions[user_id]['admin'] = True
        update_user(user_id, stage='admin')
        return {'version': event['version'], 'session': session,
                'response': {'text': t['admin_activated'], 'end_session': False}}

    if text in ['русский', 'russian']:
        update_user(user_id, lang='ru')
        return {'version': event['version'], 'session': session,
                'response': {'text': TEXTS_RU['lang_changed_ru'], 'end_session': False}}
    if text in ['английский', 'english']:
        update_user(user_id, lang='en')
        return {'version': event['version'], 'session': session,
                'response': {'text': 'Language changed to English', 'end_session': False}}

    if is_new:
        update_user(user_id, cart='[]', stage='main')
        cats = get_cats()
        buttons = [{'title': c, 'hide': True} for c in cats] + [{'title': 'Корзина', 'hide': True},
                                                                {'title': 'Помощь', 'hide': True},
                                                                {'title': 'English' if lang == 'ru' else 'Русский',
                                                                 'hide': True}]
        response = {'version': event['version'], 'session': session,
                    'response': {'text': t['welcome'], 'buttons': buttons, 'end_session': False}}
        if BANNER_IMAGE_ID:
            response['response']['card'] = {'type': 'BigImage', 'image_id': BANNER_IMAGE_ID, 'title': 'ВКУСНО И БЫСТРО',
                                            'description': 'Доставка еды'}
        return response

    if stage == 'order_table':
        try:
            table_num = int(text)
            if 1 <= table_num <= 50:
                items_text = ';'.join([f"{item['name']} x{item['qty']}" for item in cart])
                total = sum(item['price'] * item['qty'] for item in cart)
                order_id = add_order(table_num, items_text, total, lang)
                update_user(user_id, cart='[]', stage='main')
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['order_success'].format(order_id), 'end_session': False}}
            else:
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['order_error'], 'end_session': False}}
        except:
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['order_error'], 'end_session': False}}

    if 'бургеры' in text:
        cat = 'Бургеры'
        items = get_menu(cat)
        msg = t['select_category'].format(cat)
        buttons = []
        for item in items:
            msg += f'{item["id"]}. {item["name"]} - {item["price"]}₽\n'
            buttons.append({'title': item["name"], 'hide': True})
        buttons.append({'title': 'Назад', 'hide': True})
        buttons.append({'title': 'Корзина', 'hide': True})
        update_user(user_id, stage='select_item')
        sessions[user_id]['current_cat'] = cat
        return {'version': event['version'], 'session': session,
                'response': {'text': msg, 'buttons': buttons, 'end_session': False}}

    if 'закуски' in text:
        cat = 'Закуски'
        items = get_menu(cat)
        msg = t['select_category'].format(cat)
        buttons = []
        for item in items:
            msg += f'{item["id"]}. {item["name"]} - {item["price"]}₽\n'
            buttons.append({'title': item["name"], 'hide': True})
        buttons.append({'title': 'Назад', 'hide': True})
        buttons.append({'title': 'Корзина', 'hide': True})
        update_user(user_id, stage='select_item')
        sessions[user_id]['current_cat'] = cat
        return {'version': event['version'], 'session': session,
                'response': {'text': msg, 'buttons': buttons, 'end_session': False}}

    if 'салаты' in text:
        cat = 'Салаты'
        items = get_menu(cat)
        msg = t['select_category'].format(cat)
        buttons = []
        for item in items:
            msg += f'{item["id"]}. {item["name"]} - {item["price"]}₽\n'
            buttons.append({'title': item["name"], 'hide': True})
        buttons.append({'title': 'Назад', 'hide': True})
        buttons.append({'title': 'Корзина', 'hide': True})
        update_user(user_id, stage='select_item')
        sessions[user_id]['current_cat'] = cat
        return {'version': event['version'], 'session': session,
                'response': {'text': msg, 'buttons': buttons, 'end_session': False}}

    if 'напитки' in text:
        cat = 'Напитки'
        items = get_menu(cat)
        msg = t['select_category'].format(cat)
        buttons = []
        for item in items:
            msg += f'{item["id"]}. {item["name"]} - {item["price"]}₽\n'
            buttons.append({'title': item["name"], 'hide': True})
        buttons.append({'title': 'Назад', 'hide': True})
        buttons.append({'title': 'Корзина', 'hide': True})
        update_user(user_id, stage='select_item')
        sessions[user_id]['current_cat'] = cat
        return {'version': event['version'], 'session': session,
                'response': {'text': msg, 'buttons': buttons, 'end_session': False}}

    if 'десерты' in text:
        cat = 'Десерты'
        items = get_menu(cat)
        msg = t['select_category'].format(cat)
        buttons = []
        for item in items:
            msg += f'{item["id"]}. {item["name"]} - {item["price"]}₽\n'
            buttons.append({'title': item["name"], 'hide': True})
        buttons.append({'title': 'Назад', 'hide': True})
        buttons.append({'title': 'Корзина', 'hide': True})
        update_user(user_id, stage='select_item')
        sessions[user_id]['current_cat'] = cat
        return {'version': event['version'], 'session': session,
                'response': {'text': msg, 'buttons': buttons, 'end_session': False}}

    if 'корзина' in text:
        if not cart:
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['cart_empty'], 'end_session': False}}
        msg = t['cart']
        total = 0
        for item in cart:
            msg += f'{item["name"]} x{item["qty"]} - {item["price"] * item["qty"]}₽\n'
            total += item["price"] * item["qty"]
        msg += f'\n{t["total"].format(total)}\n\n{t["order_confirm"]}'
        return {'version': event['version'], 'session': session, 'response': {'text': msg, 'buttons': [
            {'title': 'Заказать', 'hide': True}, {'title': 'Очистить', 'hide': True}], 'end_session': False}}

    if 'очистить' in text:
        update_user(user_id, cart='[]')
        return {'version': event['version'], 'session': session,
                'response': {'text': t['cart_clear'], 'end_session': False}}

    if 'заказать' in text:
        if not cart:
            return {'version': event['version'], 'session': session,
                    'response': {'text': t['cart_empty'], 'end_session': False}}
        update_user(user_id, stage='order_table')
        return {'version': event['version'], 'session': session,
                'response': {'text': t['order_prompt'], 'end_session': False}}

    if 'назад' in text:
        update_user(user_id, stage='main')
        sessions[user_id]['current_cat'] = None
        cats = get_cats()
        buttons = [{'title': c, 'hide': True} for c in cats] + [{'title': 'Корзина', 'hide': True},
                                                                {'title': 'Помощь', 'hide': True},
                                                                {'title': 'English' if lang == 'ru' else 'Русский',
                                                                 'hide': True}]
        return {'version': event['version'], 'session': session,
                'response': {'text': t['back'], 'buttons': buttons, 'end_session': False}}

    if 'помощь' in text:
        return {'version': event['version'], 'session': session, 'response': {'text': t['help'], 'end_session': False}}
    if current_cat and stage == 'select_item':
        items = get_menu(current_cat)
        for item in items:
            if item['name'].lower() == text or str(item['id']) == text:
                found = False
                for ci in cart:
                    if ci['id'] == item['id']:
                        ci['qty'] += 1
                        found = True
                        break
                if not found:
                    cart.append({'id': item['id'], 'name': item['name'], 'price': item['price'], 'qty': 1})
                update_user(user_id, cart=json.dumps(cart))
                return {'version': event['version'], 'session': session,
                        'response': {'text': t['added'].format(item['name']), 'end_session': False}}
    cats = get_cats()
    buttons = [{'title': c, 'hide': True} for c in cats] + [{'title': 'Корзина', 'hide': True},
                                                            {'title': 'Помощь', 'hide': True},
                                                            {'title': 'English' if lang == 'ru' else 'Русский',
                                                             'hide': True}]
    return {'version': event['version'], 'session': session,
            'response': {'text': t['unknown'], 'buttons': buttons, 'end_session': False}}
