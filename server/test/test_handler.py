import json

import boto3
import moto


EVENT = {
    "resource": "/helloworld",
    "path": "/helloworld",
    "httpMethod": "GET",
    "headers": {},
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": {
        "gameId": "4"
    },
    "stageVariables": None,
    "requestContext": {
        "authorizer": {
            "claims": {
                "email_verified": "true",
                "token_use": "id",
                "auth_time": "1564155205",
                "cognito:username": "Player1",
                "exp": "Sat Jul 27 18:39:42 UTC 2019",
                "iat": "Sat Jul 27 17:39:42 UTC 2019",
            }
        },
        "resourcePath": "/helloworld",
        "httpMethod": "GET",
        "requestTime": "27/Jul/2019:17:40:24 +0000",
        "path": "/dev/helloworld",
        "protocol": "HTTP/1.1",
        "stage": "dev",
        "requestTimeEpoch": 1564249224687,
        "identity": {
            "cognitoIdentityPoolId": None,
            "accountId": None,
            "cognitoIdentityId": None,
            "caller": None,
            "principalOrgId": None,
            "accessKey": None,
            "cognitoAuthenticationType": None,
            "cognitoAuthenticationProvider": None,
            "userArn": None,
            "userAgent": "PostmanRuntime/7.15.2",
            "user": None
        },
    },
    "body": None,
    "isBase64Encoded": False
}


def make_dynamo_things():
    dynamo = boto3.resource('dynamodb', region_name='eu-west-1')
    npzr_table = dynamo.create_table(
        TableName="npzrTable",
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'type',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'type',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    npzr_table.put_item(
        Item={
            "id": "4",
            "type": "game",
            "deckSeed": "123456",
            "player1": "Player1",

            "player2": None,
            "Actions": [],
            "Winner": None,
        }
    )
    from server.src import handler
    return handler, npzr_table


@moto.mock_dynamodb2
def test_hello_world():
    """
    Tests GET to /helloworld
    is responding with the event it was called with
    """
    handler, _ = make_dynamo_things()
    resp = handler.hello(EVENT, None)
    assert resp["statusCode"] == 200
    assert resp["body"] == json.dumps({
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": EVENT
    })


@moto.mock_dynamodb2
def test_add_game():
    """
    Tests POST to /
    is creating a game for the player who sent the request
    """
    handler, npzr_table = make_dynamo_things()
    resp = handler.add_game(EVENT, None)
    assert resp["statusCode"] == 201
    game_id = resp["body"]
    created = npzr_table.get_item(
        Key={
            "id": game_id,
            "type": "game",
        }
    )
    assert 'Item' in created
    item = created['Item']
    assert item["player1"] == EVENT["requestContext"]["authorizer"]["claims"]["cognito:username"]


@moto.mock_dynamodb2
def test_join_game():
    """
    Tests POST to /{gameId}
    is joining game if slot available for the user
    """
    player2 = "Player2"
    handler, npzr_table = make_dynamo_things()
    resp = handler.join_game(EVENT, None)
    assert resp["statusCode"] == 400
    assert resp["body"] == "User is already in the game"
    new_event = {**EVENT, "pathParameters": {"gameId": "5"}}
    resp = handler.join_game(new_event, None)
    assert resp["statusCode"] == 404
    assert resp["body"] == "Game not found"
    new_event = {
        **EVENT,
        "requestContext": {"authorizer": {"claims": {"cognito:username": player2}}}
    }
    resp = handler.join_game(new_event, None)
    assert resp["statusCode"] == 200
    assert resp["body"] == "Added user to the game"
    joined = npzr_table.get_item(
        Key={
            "id": "4",
            "type": "game",
        }
    )
    assert 'Item' in joined
    item = joined['Item']
    assert item["player1"] == EVENT["requestContext"]["authorizer"]["claims"]["cognito:username"]
    assert item["player2"] == player2


@moto.mock_dynamodb2
def test_get_game():
    """
    Tests Get to /{gameId}
    is returning the game details
    """
    handler, npzr_table = make_dynamo_things()
    resp = handler.get_game(EVENT, None)
    assert resp["statusCode"] == 200
    new_event = {**EVENT, "pathParameters": {"gameId": "5"}}
    resp = handler.get_game(new_event, None)
    assert resp["statusCode"] == 404
    assert resp["body"] == "Game not found"
