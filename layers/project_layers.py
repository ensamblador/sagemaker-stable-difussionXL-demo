import json
from constructs import Construct

from aws_cdk import (
    aws_lambda as _lambda

)


class Pillow(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        layer = _lambda.LayerVersion(
            self, "Pillow", code=_lambda.Code.from_asset("./layers/pil.zip"),
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8,_lambda.Runtime.PYTHON_3_9], 
            description = 'Pillow')

        
        self.layer = layer



class AlexaSDK(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        alexa_sdk_layer = _lambda.LayerVersion(
            self, "AlexaSDK", code=_lambda.Code.from_asset("./layers/ask-sdk-core.zip"),
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8,_lambda.Runtime.PYTHON_3_9], 
            description = 'Alexa SDK')

        
        self.layer = alexa_sdk_layer