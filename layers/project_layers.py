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

