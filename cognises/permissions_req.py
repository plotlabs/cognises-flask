from functools import wraps


def permission_required(group_detail):
    """ A flask decorator to check if the user has the permission to access a
    particular route.

    A json loaded data for the details of the groups is passed which has a key
    called "allowed_functions" which contains a list of all the functions
    allowed for that particular group.

    """
    def decorator(t):
        @wraps(t)
        def decorated(details, *args, **kwargs):
            for each_obj in group_detail:
                if each_obj['group_name'] == details['user_group'][0]:
                    allow = each_obj['allowed_functions']
                    if t.__name__ not in allow:
                        return t({'message': 'Forbidden access',
                                  'status': 401})
            return t(details, *args, **kwargs)
        return decorated
    return decorator
