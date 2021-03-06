from __future__ import print_function
import requests
import json
from collections import Counter

<<<<<<< HEAD
url = 'http://174.69.134.193:5001'
# -------------Global vars for vR Ops-------------------------------------------
alerts = {}
=======
url = 'YOUR VROPSRELAY URL GOES HERE' #something like http://myopsrelay.net:5001
>>>>>>> b693359de95d225d30ca7c5a653ab0b5422a99e4


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "vRealize Operations - " + title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response_image(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Standard',
            'title': "vRealize Operations - " + title,
            'image': {
                "smallImageUrl": "https://s3-us-west-2.amazonaws.com/blackmesaresearch/vrops-logo-160x160.png",
                "largeImageUrl": "https://s3-us-west-2.amazonaws.com/blackmesaresearch/vrops-logo-160x160.png"
            },
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to vRealize Operations. "

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "ask me for all alerts of a resource kind for a major badge, " \
                    "get all host alerts for health? "

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_image(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_help_request():
    session_attributes = {}
    card_title = "Voice Input Help"
    speech_output = "To get started, ask me for all resource kind alerts for a major badge.  For example," \
        "Get all host alerts for health.  " \
        "Valid resource kinds are, vm, host, datastore and cluster.  " \
        "Valid badges are, health, risk and efficiency.  " \

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def handle_session_end_request():
    session_attributes = {}
    card_title = "Session Ended"
    speech_output = "Closing vRealize Operations session. "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def translate_resource_intent(intent):
    print("Stated intent " + intent['slots']['resource']['value'])
    resString = ""
    vropsResKindString = {
        'bm':'virtualmachine',
        'vm':'virtualmachine',
        'host': 'hostsystem',
        'cluster': 'clustercomputeresource',
        'datastore': 'datastore'
    }

#    if intent['slots']['resource']['value'] in vropsResKindString:
    resString = vropsResKindString.get(intent['slots']['resource']['value'].lower())
    return resString

def speechify_resource_intent(intent,plurality):
        vocalString = ""
        vocalStrings = {
            'bm':'virtual machine',
            'vm':'virtual machine',
            'host': 'host system',
            'cluster': 'cluster',
            'datastore': 'data store'
        }
        if plurality:
            vocalString = vocalStrings.get(intent['slots']['resource']['value'].lower()) + "s"
        else:
            vocalString = vocalStrings.get(intent['slots']['resource']['value'].lower())
        return vocalString

def alerts_by_sev(alerts,sev):
    filteredAlerts = []
    if any(x == sev for x in ["INFO","WARNING","IMMEDIATE","CRITICAL"]):
        for alert in alerts["alerts"]:
            if alert["alertLevel"] == sev:
                filteredAlerts.append(alert)
    return filteredAlerts

#def top_n_resources(alerts):


#------------Invocations-----------------------------------

def get_top_alerts_of_resource_kind(intent, session):
    card_title = "Top " + intent['slots']['num']['value'] + " active " + intent['slots']['badge']['value'] + " alerts for all " + intent['slots']['resource']['value'] + "."
    session_attributes = {}
    should_end_session = False

    resString = translate_resource_intent(intent)

    callurl = url + "/alerts/" + intent['slots']['badge']['value'] + "/" + resString
    print(callurl)
    response = requests.request("GET", callurl)
    alerts = json.loads(response.text)

    topAlerts = Counter(alerts['alertDefinitionName'])





def get_impact_alerts_of_resource_kind(intent, session):
    card_title = "Active " + intent['slots']['badge']['value'] + " alerts for all " + intent['slots']['resource']['value'] + "."
    session_attributes = {}
    should_end_session = False

    resString = translate_resource_intent(intent)

    callurl = url + "/alerts/" + intent['slots']['badge']['value'] + "/" + resString
    print(callurl)
    response = requests.request("GET", callurl)
    alerts = json.loads(response.text)

    numAllAlerts = str(alerts["pageInfo"]["totalCount"])
    numImmediateAlerts = str(len(alerts_by_sev(alerts,"IMMEDIATE")))
    numCriticalAlerts = str(len(alerts_by_sev(alerts,"CRITICAL")))

    speech_output = "There are " + numAllAlerts + " " + intent['slots']['badge']['value'] + " alerts for monitored " + speechify_resource_intent(intent,1) + ". "  + \
                     "Of those " + numCriticalAlerts + " are critical and " + numImmediateAlerts + " are immediate."

    should_end_session = False

    reprompt_text = "ask me for all alerts of a resource kind for a major badge, " \
                    "get all host alerts for health? "

    return build_response(session_attributes, build_speechlet_response_image(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "HealthStatusIntent":
        return get_impact_alerts_of_resource_kind(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return handle_help_request()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    #if event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.amzn1.ask.skill.c79aaa7c-25a0-4d7c-96a6-c4239ba171c8":
    #    raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
