# Flask Cognises: AWS Cognito Group Based Authorization

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/plotlabs/cognises-flask/blob/master/LICENSE.txt) [![Build Status](https://travis-ci.org/plotlabs/cognises-flask.svg?branch=master)](https://travis-ci.org/plotlabs/cognises-flask) [![CodeFactor](https://www.codefactor.io/repository/github/plotlabs/cognises-flask/badge/master)](https://www.codefactor.io/repository/github/plotlabs/cognises-flask/overview/master) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://www.plotlabs.io/) [![PyPI](https://img.shields.io/pypi/v/cognises.svg)](https://pypi.org/project/cognises/)

This package gives the developer fine grain control over their users through **Group based Permission Using AWS Cognito**, including python middlewares(decorators) called **login_check**, for checking if the user is logged in through AWS Cognito and another middleware called **permission_required** which checks the route access permissions for that user .

**Note:** This package is built essentially for usage within a Flask application.

## Installation

The package can be installed using the pip install command:

```console
pip install cognises
```

## How To Setup

### 1) Create a group within a user pool

**The create_update function allows:**

* creation of new iam role and a new cognito user pool group and links the user pool group to the newly created iam role.
* updation of the role policy of the role already linked to a user group

**The function takes 4 arguments:**

* **group_detail** [Required] - It is a json object that contains details for one or more groups. Each group has a created attribute which takes two values:
  -- **true**: Specifies that the group is already created and implements the update part of the function which updates the role policy.
  -- **false**: Specifies that a new group has to be created and implements the creation part of the function to create a new iam role and a new cognito user pool group.

**The format of the json object is:**

```json
[
  {
    "group_name": "Group1",
    "group_policy": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "Stmt1524591948858",
          "Action": "cognito-idp:*",
          "Effect": "Allow",
          "Resource": "arn:aws:cognito-idp:us-east-1:userid:userpool/pool_id"
        }
      ]
    },
    "created": "false",
    "allowed_functions": ["protected", "admin_panel", "update_data"]
  },
  {
    "group_name": "String",
    "group_policy": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "Stmt1524591948858",
          "Action": "cognito-idp:*",
          "Effect": "Allow",
          "Resource": "arn:aws:cognito-idp:us-east-1:userid:userpool/pool_id"
        }
      ]
    },
    "created": "false",
    "allowed_functions": ["public", "view_data"]
  }
]
```

**Note:** The group_policy is the aws policy for the role attached to that group. Refer to the following link to generate your fine-controlled policies: [AWS Policy Generator](https://awspolicygen.s3.amazonaws.com/policygen.html)

* **iam_client** [Required] - The boto3 iam client.

  ```python
  python boto3.client('iam', 'aws_region', 'aws_access_key_id', 'aws_secret_access_key')
  ```

* **cognito_client** [Required] - The boto3 aws cognito-idp client.

  ```python
  python boto3.client('cognito-idp', 'aws_region', 'aws_access_key_id', 'aws_secret_access_key')
  ```

* **cognito_pool_id** - The aws cognito user pool id. It is required when a new group has to be created. In case of updating already existing group, this argument is not required.

**Example usage:**

```python
import boto3
import os
from flask import json
from cognises import create_update

iam_client = boto3.client('iam', 'aws_region', 'aws_access_key_id', 'aws_secret_access_key')
cognito_client = boto3.client('cognito-idp', 'aws_region', 'aws_access_key_id', 'aws_secret_access_key')

script_dir = os.path.dirname(__file__)
file_name = "group_detail.json"
abs_file_path = os.path.join(script_dir, file_name)
data = json.load(open(abs_file_path))

create_update(data, iam_client, cognito_client, 'cognito_pool_id')
```

### 2) login_check decorator

This decorator checks if the user already has a valid AWS Cognito token or not to access the route, and works much like @login_required decorator in Flask.
It takes 2 arguments:

* **cognito_pool_region** [Required] - The region in which the cognito user pool is created in
* **cognito_pool_id** [Required] - The id of the cognito user pool

**Example usage:**

```python
from cognises import login_check

@app.route('/protected', methods=['GET','POST'])
@login_check('cognito_pool_region', 'cognito_pool_id')
def protected(response):
	if response['status'] == 200:
		return response['user_email']
	else:
		return response['message']
```

### 3) permission_required decorator

This decorator checks whether the user can access the route. It is used along with the login_check decorator and checks whether the route is present in the allowed functions for the cognito user pool group to which the user belongs and restricts the access for the user if the route in not present in it.
It takes the **group_detail** argument which is json object that contains details for one or more groups. It has the same structure described in point 1.

**Example usage:**

```python
from cognises import login_check, permission_required

@app.route('/protected', methods=['GET','POST'])
@login_check('cognito_pool_region', 'cognito_pool_id')
@permission_required(group_details)
def protected(response):
	if response['status'] == 200:
		return response['user_email']
	else:
		return response['message']
```
