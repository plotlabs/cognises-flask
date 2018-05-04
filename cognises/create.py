import json


def create_update(group_detail, iam_client, cognito_client, cognito_pool_id=None):
    """ Function to create a new iam role and a new user pool group for an aws
    cognito user pool.

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

   To create a new group the "created" argument should be false and to update a
   group it should be true.

   If created argument is false, a new iam role is created and then a new group
   is created and linked to the newly created role.

   If created argument is true, any changes made to the role policy for the
   group are updated.

    """
    index = 0
    for each_obj in group_detail:
        if each_obj['created'] == "false":
            response = iam_client.create_role(
                RoleName='role_' + each_obj['group_name'],
                AssumeRolePolicyDocument=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Federated": "cognito-identity.amazonaws.com"
                            },
                            "Action": "sts:AssumeRoleWithWebIdentity",
                            "Condition": {
                                "StringEquals": {
                                    "cognito-identity.amazonaws.com:aud":
                                        cognito_pool_id
                                }}}]}))

            role_arn = response['Role']['Arn']

            response = iam_client.put_role_policy(
                RoleName='role_' + each_obj['group_name'],
                PolicyName=each_obj['group_name'] + '_policy',
                PolicyDocument=json.dumps(each_obj['group_policy'])
            )
            response = cognito_client.create_group(
                GroupName=each_obj['group_name'],
                UserPoolId=cognito_pool_id,
                RoleArn=role_arn
            )
            print response
            each_obj['created'] = 'true'
            print(index, 'will be deleted')
            with open("group_detail.json", "w") as jsonFile:
                json.dump(group_detail, jsonFile)
            index += 1
        else:
            response = iam_client.get_role_policy(
                RoleName='role_' + each_obj['group_name'],
                PolicyName=each_obj['group_name'] + '_policy'
            )
            if response['PolicyDocument'] != each_obj['group_policy']:
                print('policy change on', index, 'th object')
                response = iam_client.delete_role_policy(
                    RoleName='role_' + each_obj['group_name'],
                    PolicyName=each_obj['group_name'] + '_policy'
                )

                response = iam_client.put_role_policy(
                    RoleName='role_' + each_obj['group_name'],
                    PolicyName=each_obj['group_name'] + '_policy',
                    PolicyDocument=json.dumps(each_obj['group_policy'])
                )
                print response
            index += 1
