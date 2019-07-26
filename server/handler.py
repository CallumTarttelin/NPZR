import json


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    #"""
    #return {
    #    "message": "Go Serverless v1.0! Your function executed successfully!",
    #    "event": event
    #}
    #"""


def addGame(event, context):
    return {
        "statusCode": 501,
        "body": {
            "message": "Working on it",
            "input": event
        }
    }


def getGame(event, context):
    return {
        "statusCode": 501,
        "body": {
            "message": "Working on it",
            "input": event
        }
    }


def takeAction(event, context):
    return {
        "statusCode": 501,
        "body": {
            "message": "Working on it",
            "input": event
        }
    }