def get_user(object):
    ' function returns model-referenced user-object '

    def get_from_request(obj):
        ' function returns user-object from request attr'
        return getattr(getattr(obj, 'request'), 'user')

    if 'request' in dir(object):
        return get_from_request(object)
    elif 'view' in dir(object):
        return get_from_request(getattr(object['view']))
    elif hasattr(object,'scope'):
        if 'user' in getattr(object, 'scope'):
            return getattr(object, 'scope').get('user')
    else:
        raise TypeError('Can not return user from object {}'.format(type(object)))
