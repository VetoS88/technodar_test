"""
    Различные вспомогательные функции.
"""
from . import app


def add_search_filters(query_string, search_param):
    """
    Функция для составления запроса поиска пои имени фамилии и отчеству
    :param query_string: базовый запрос(без фильтров поиска)
    :param search_param: строка с данными по которым нужно осуществить поиск
    :return: query_string: строка с фильтрами поиска.
    """
    search_param = search_param.split()
    query_string = query_string + " " + "WHERE (secondname ILIKE '%{str}%' OR " \
                                        "firstname ILIKE '%{str}%' OR " \
                                        "middlename ILIKE '%{str}%')".format(str=search_param[0])
    if len(search_param) > 1:
        query_string = query_string + " " + "AND (secondname ILIKE '%{str}%' OR " \
                                            "firstname ILIKE '%{str}%' OR " \
                                            "middlename ILIKE '%{str}%')".format(str=search_param[1])
        if len(search_param) > 2:
            query_string = query_string + " " + "AND (secondname ILIKE '%{str}%' OR " \
                                                "firstname ILIKE '%{str}%' OR " \
                                                "middlename ILIKE '%{str}%')".format(str=search_param[2])
    return query_string


@app.template_filter('translate_labels')
def translate_labels(eng_word):
    """
    Фильтр для отображения меток на русском языке.
    
    """
    dictionary = {
        'secondname': 'Фамилия',
        'firstname': 'Имя',
        'middlename': 'Отчество'
    }
    return dictionary.get(eng_word, '')


def filter_changed_data(data):
    """
    Функция для определения изменившихся данных
    :param data: старые и новые данные
    :return: changed_data: словарь только тольок тех данных, которые были изменены
    """
    changed_data = {}
    for field in data:
        if 'old_' not in field:
            changed = data[field] != data['old_' + field]
            if changed:
                changed_data[field] = data[field]
    return changed_data
