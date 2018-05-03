from functools import wraps


def permission_required(group_detail):
    """ A flask decorator to check if the user has the permission to access a
    particular route.

    It takes the json loaded data for the details of the groups stored in the
    following format:

    [
        {
            "group_name": "String",
            "group_policy":
            {
                "Version": "2012-10-17",
                "Statement": [
                {
                    "Sid": "Stmt1524591948858",
                    "Action": "cognito-idp:*",
                    "Effect": "Allow",
                    "Resource": "arn:aws:cognito-idp:us-east-1:userid:userpool/pool_id"
                }]
            },
            "created": "false",
            "allowed_functions": ["protected", "admin_panel", "view_data"]
        }
   ]

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
