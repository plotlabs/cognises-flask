from functools import wraps
from flask import request, jsonify
import os
import sys
import requests
import simplejson as json
from jose import jwt


def cognito_pool_url(aws_pool_region, cognito_pool_id):
    """ Function to create the AWS cognito issuer URL for the user pool using
    the pool id and the region the pool was created in.

    Returns: The cognito pool url
    """
    return ("https://cognito-idp.{}.amazonaws.com/{}".format(
        aws_pool_region, cognito_pool_id))


def get_user_email(aws_region, aws_user_pool, id_token):
    """ Function to pull the user email out of an id token. It calls the
    function to validate the token and then pulls the user email out of the
    claims returned.

    Returns: the email of the user along with any group/s the user is a part of

    """
    payload = jwt.get_unverified_claims(id_token)
    client_id = payload.get('aud')

    # Validate the token and get the claims
    aws_claims = get_verified_claims(aws_region, aws_user_pool, id_token,
                                     client_id)
    if aws_claims.get('token_use') != 'id':
        raise ValueError('Not an ID Token')

    return {'user_email': aws_claims.get('email'),
            'user_group': aws_claims.get('cognito:groups'),
            'status': 200, 'message': 'Validation successful'}


def get_verified_claims(aws_region, aws_user_pool, token, audience=None):
    """ Function to validate a user jwt id token along with any audience(the
    client id) given.

    Returns: The claims dictionary for the token if valid

    """

    # Get the header from theh given token
    header = jwt.get_unverified_header(token)
    kid = header['kid']

    pool_verify_url = cognito_pool_url(aws_region, aws_user_pool)

    aws_keys = aws_key_dict(aws_region, aws_user_pool)
    key = aws_keys.get(kid)
    kargs = {"issuer": pool_verify_url}

    if audience is not None:
        kargs["audience"] = audience

    aws_claims = jwt.decode(
        token,
        key,
        **kargs
    )
    print("Claims: ", aws_claims)

    return aws_claims


def aws_key_dict(aws_pool_region, cognito_pool_id):
    """ Function to fetch AWS JWT validation file (if necessary) and convert
    the file into a keyed dictionary that is used to validate a user id token.

    Returns: A dictionary of values taken from jwt validation file

    """

    # Load validation file if available
    aws_jwt_validation_file = os.path.abspath(os.path.join(
        os.path.dirname(sys.argv[0]), 'aws_{}.json'.format(
            cognito_pool_id)))

    # Download validation file from cognito pool issuer url if not available
    if not os.path.isfile(aws_jwt_validation_file):
        # If we can't find the file already, try to download it.
        issuer_url = requests.get(
            cognito_pool_url(aws_pool_region, cognito_pool_id) +
            '/.well-known/jwks.json'
        )
        aws_jwt = json.loads(issuer_url.text)
        with open(aws_jwt_validation_file, 'w+') as json_data:
            json_data.write(issuer_url.text)
            json_data.close()

    else:
        with open(aws_jwt_validation_file) as json_data:
            aws_jwt = json.load(json_data)
            json_data.close()

    # Create a dictionary keyed by the kid
    result_dict = {}
    for item in aws_jwt['keys']:
        result_dict[item['kid']] = item

    print('Key dict result: ', result_dict)

    return result_dict


def login_check(cognito_pool_region, cognito_pool_id):
    """ A flask decorator to verify the user jwt id token stored in the cookies.

    It takes aws cognito pool region and aws cognito pool id passed as arguments
    to the decorator.

    Returns: The email and the gruop the user exists in if the token passed is
    valid else return the appropriate errors.

    """
    def decorator(t):
        @wraps(t)
        def decorated_function(*args, **kwargs):

            # Check if the cognito pool region and pool id is passed as
            # arguments to the decorator
            if cognito_pool_region is None or cognito_pool_id is None:
                return jsonify({'message': 'required credentials not passed'})

            # Retrieve the jwt used id token from the cookies
            id_token = request.cookies.get('token_cookie')
            print("Token is here in middleware: ", id_token)

            if id_token:
                try:
                    aws_region = cognito_pool_region
                    aws_pool = cognito_pool_id
                    details = get_user_email(aws_region, aws_pool, id_token)

                except jwt.ExpiredSignatureError:
                    return jsonify({'message': 'token has expired',
                                    'status': 401})

                except:
                    return jsonify({'message': 'token is invalid',
                                    'status': 401})

            else:
                return jsonify({'message': 'token is missing', 'status': 400})

            return t(details, *args, **kwargs)

        return decorated_function

    return decorator
