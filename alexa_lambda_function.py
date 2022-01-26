# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.

#have created all the classes for each intent. 
#TO DO: fix the utterances for each intent and send them to getMovieIntent if possible. if not create separate intents for each path taken by user.
import logging
import ask_sdk_core.utils as ask_utils
import boto3
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

#dict to send to lambda for backend processing
inputParams = {
    "inputType" : "",
    "inputVal" : "",
    "userId" : "",
    "isRating": "",
    "ratingVal": ""
}


#client used to connect and allow permissions to lambda/iam role.
sts_client = boto3.client('sts')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cross_acc_session = sts_client.assume_role(
    RoleArn="arn:aws:iam::719881323872:role/service-role/cloudsearch_Alexa",
    RoleSessionName="test123"
    )
lambda_client  = boto3.client('lambda',
    aws_access_key_id=cross_acc_session['Credentials']['AccessKeyId'],
    aws_secret_access_key=cross_acc_session['Credentials']['SecretAccessKey'],
    aws_session_token=cross_acc_session['Credentials']['SessionToken']
    )
#client created.

#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "I have some filtering options available for you. Please choose one of the following: No filter, filter by genre, filter by Director, director and rating, or genre and rating."
        
        reprompt_output = "please reply with no or with a search query"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_output)
                .response
        )

class getMovieIntentHandler(AbstractRequestHandler):
    """Handler for get Movie Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("getMovieIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Entered getMovieIntent"
        
        userId = handler_input.request_envelope.session.user.user_id
        
        #slot values stored in below four variables -> values are from user on alexa front end.
        slots = handler_input.request_envelope.request.intent.slots
        genreVal = slots["genre"].value
        directorVal = slots["director"].value
        ratingVal = slots["rating"].value
        
        speak_output = "entered none"
        
        # if 'genre' in slots:
        #     #if 'value' in intent['slots']['genre']:
        #     speak_output = 'Genre = ' + slots['genre'].value
        # elif 'director' in slots:
        #     speak_output = "entered director"
        
        if slots["genre"].value is not None:
            inputParams["inputType"] = "genre"
            inputParams["inputVal"] = slots["genre"].value
        elif slots["director"].value is not None:
            inputParams["inputType"] = "director"
            inputParams["inputVal"] = slots["director"].value
            
        if slots["rating"].value is not None:
            inputParams["isRating"] = "true"
            inputParams["ratingVal"] = slots["rating"].value
        else:
            inputParams["isRating"] = "false"
            inputParams["ratingVal"] = "0"
        #end of slot values
        
        # requesting response from lambda
        response = lambda_client.invoke(
            FunctionName = 'arn:aws:lambda:us-east-1:719881323872:function:movieReco',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(inputParams)
            )
        responseFromLambda = json.load(response['Payload'])
        # end of response
        
        return (
            handler_input.response_builder
                .speak(responseFromLambda)
                .response
        )
    
class speakGenreIntentHandler(AbstractRequestHandler):
    """Handler to get genre"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("speakGenreIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        speak_output = 'What genre would you like to filter your recommendation with?'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class speakDirectorIntentHandler(AbstractRequestHandler):
    """Handler to get director"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("speakDirectorIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        speak_output = 'Which director\'s movies would you like to be recommended?'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class speakGandRIntentHandler(AbstractRequestHandler):
    """Handler to get genre with rating"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("speakGandRIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        speak_output = 'What genre and rating should I query with? Please specify rating in integer values only.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class speakDandRIntentHandler(AbstractRequestHandler):
    """Handler to get director with rating"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("speakDandRIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        speak_output = 'What director and rating should I query with? Please specify rating in integer values only.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                #.withShouldEndSession(false)
                .response
        )
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(getMovieIntentHandler())
sb.add_request_handler(speakGenreIntentHandler())
sb.add_request_handler(speakDirectorIntentHandler())
sb.add_request_handler(speakGandRIntentHandler())
sb.add_request_handler(speakDandRIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
# sb.add_request_handler(getGenreIntentHandler())
# sb.add_request_handler(getDirectorIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()