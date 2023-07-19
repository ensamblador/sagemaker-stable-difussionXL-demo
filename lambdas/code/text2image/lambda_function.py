from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard, StandardCard, Image
from ask_sdk_model.services.directive import (SendDirectiveRequest, Header, SpeakDirective)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.response import Response
import json
import time
import logging
# import matplotlib.pyplot as plt1
import boto3
# import numpy as np
import os
from io import BytesIO
import base64
from PIL import Image as OpenImage
import random


#ESTO ES UNA PRUEBA


sb = CustomSkillBuilder(api_client=DefaultApiClient())
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
runtime= boto3.client('runtime.sagemaker')
translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
"""
Styles
["enhance", "anime", "photographic", "digital-art", "comic-book", "fantasy-art", "line-art", "analog-film", 
                "neon-punk", "isometric", "low-poly", "origami", "modeling-compound", "cinematic",
                "3d-model", "pixel-art", "tile-texture"]
"""
style_list = ["anime", "digital-art", "comic-book", "fantasy-art", "cinematic"]
message = 'message'


class LaunchRequestHandler(AbstractRequestHandler):
    # Handler for Skill Launch
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Hola. ¿Qué quieres que genere?"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Alexa Demo - Stable Diffusion XL", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

def get_progressive_response(handler_input):
    # type: (HandlerInput) -> None
    request_id_holder = handler_input.request_envelope.request.request_id
    directive_header = Header(request_id=request_id_holder)
    
    slots = handler_input.request_envelope.request.intent.slots
    prompt = str(slots['prompt'].value)

    speech = SpeakDirective(speech="Entendido. Por favor espera un momento. Estoy generando tu imagen...")
    directive_request = SendDirectiveRequest(
        header=directive_header, directive=speech)

    directive_service_client = handler_input.service_client_factory.get_directive_service()
    directive_service_client.enqueue(directive_request)
    
    
    #Fchirinos - Translate
    #text = prompt
    print(prompt)
    prompt = translate.translate_text(Text=prompt, SourceLanguageCode="auto", TargetLanguageCode="en")
    text = str(prompt)
    print(prompt)

    #Max Inference
    if os.environ["random"] == "x":
        style = random.choice(style_list)
    else:
        style = os.environ["style_preset"]
    print(style)
    
    payload = {
        "text_prompts": [{"text":text}],
        #"style_preset": style,
        "width": os.environ["width"]
    }

    encoded_payload = json.dumps(payload).encode("utf-8")
    response = runtime.invoke_endpoint(EndpointName=os.environ['sagemaker_endpoint'],
    #                                    ContentType='application/x-text',
                                        ContentType='application/json',
                                        Accept="application/json",
    #                                    Accept="image/png",
                                        Body=encoded_payload)

    #Max Process
    image = json.loads(response['Body'].read())
    
    if image['result'] == "error":
        
        print(image['error'])
        print(image['error']['message'])
        message = image['error']['message']
        
    else:
        
        image = image['artifacts'][0]['base64']
        image_data = base64.b64decode(image.encode())
        image = OpenImage.open(BytesIO(image_data))

        #Max Save Image
        file_name = time.strftime("%Y%m%d-%H%M%S") + '_' + os.environ["width"] +'.png'
        image.save('/tmp/' + file_name)
        
        s3 = boto3.client("s3")
        bucket_name = os.environ['bucket_name']
        s3_path = os.environ['bucket_folder'] + file_name
        s3.upload_file('/tmp/' + file_name, bucket_name, s3_path, ExtraArgs={'Metadata': {'prompt': text}})
        
        #Signed URL
        
        url = boto3.client('s3').generate_presigned_url(
        ClientMethod='get_object', 
        Params={'Bucket': bucket_name , 'Key': s3_path},
        ExpiresIn=180)
    
        s3_url = url
        
        return s3_url

class HelloWorldIntentHandler(AbstractRequestHandler):
    # Handler for Hello World Intent
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        

        s3_url = get_progressive_response(handler_input)
        
        print(s3_url)
        
        
        slots = handler_input.request_envelope.request.intent.slots
        
        print(slots)
        
        prompt = str(slots['prompt'].value)
        
        print(prompt)
    
        speech_text = "Listo. Ésta es la imagen que generé para: " + prompt
        #speech_text = "Listo. Ésta es la imagen que generé para: " + str(s3_url)
    
        #image = ""
        image = Image(small_image_url=s3_url, large_image_url=s3_url)
        
        reprompt = '¿Quieres que genere algo mas?'

        handler_input.response_builder.speak(speech_text).ask(reprompt).set_card(
            StandardCard("Alexa Demo - Stable Diffusion XL", speech_text, image)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):

    # Handler for Help Intent
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Puedes pedirme que genere una imagen."

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard(
                "Alexa Demo - Stable Diffusion", speech_text))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    # Single handler for Cancel and Stop Intent
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "¡Hasta luego!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Alexa Demo - Stable Diffusion 2.1", speech_text))
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    # Handler for Session End
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    # Catch all exception handler, log exception and
    # respond with custom message
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        logger.exception(
            "Encountered following exception: {}".format(exception),
            exc_info=True)

        speech = "Lo siento, ocurrió un problema. Por favor inténtalo de nuevo."
        speech = "Encountered following exception: {}".format(exception)
        
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()