"""
Handler for NPZR server on AWS lambda
"""

import json
import uuid

import boto3


NPZR_TABLE = boto3.resource('dynamodb').Table('npzrTable')


def hello(event, _):
    """
    Simple helloworld endpoint which gives back the event to check things
    """
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }


def add_game(event, _):
    """
    Creates a game with player1 as the user who created it
    """
    item_id = uuid.uuid4().hex
    NPZR_TABLE.put_item(
        Item={
            "id": item_id,
            "type": "game",
            "deckSeed": uuid.uuid4().int,
            "player1": event["requestContext"]["authorizer"]["claims"]["cognito:username"],
            "player2": None,
            "Actions": [],
            "Winner": None,
        }
    )
    return {
        "statusCode": 201,
        "body": item_id,
    }


def join_game(event, _):
    """
    Join a game if possible
    """
    user = extract_user(event)
    response = NPZR_TABLE.get_item(
        Key={
            'id': event["pathParameters"]["gameId"],
            'type': 'game',
        }
    )
    try:
        item = response["Item"]
    except KeyError:
        return {
            "statusCode": 404,
            "body": "Game not found"
        }
    if item["player2"] is not None:
        return {
            "statusCode": 400,
            "body": "Game is already full"
        }
    if item["player1"] == user:
        return {
            "statusCode": 400,
            "body": "User is already in the game"
        }
    NPZR_TABLE.update_item(
        Key={
            'id': event["pathParameters"]["gameId"],
            'type': 'game',
        },
        UpdateExpression='SET player2 = :val1',
        ExpressionAttributeValues={
            ':val1': user
        },
    )
    return {
        "statusCode": 200,
        "body": {
            "message": "Added user to game",
            "input": event
        }
    }


def get_game(event, _):
    """
    Get the game
    """
    response = NPZR_TABLE.get_item(
        Key={
            'id': event["pathParameters"]["gameId"],
            'type': 'game',
        }
    )
    try:
        item = response["Item"]
    except KeyError:
        return {
            "statusCode": 404,
            "body": "Game not found"
        }
    item["deckSeed"] = int(item["deckSeed"])
    del item["Winner"]
    return {
        "statusCode": 200,
        "body": json.dumps(item),
    }


def take_action(event, _):
    """
    Take an action in the game
    """
    return {
        "statusCode": 501,
        "body": {
            "message": "Working on it",
            "input": event
        }
    }


def extract_user(event):
    """
    :param event: (required) the event from the request
    :return: The username of the user who made the request
    """
    return event["requestContext"]["authorizer"]["claims"]["cognito:username"]
