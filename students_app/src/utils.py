def add_search_filters(query_string, search_param):
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
