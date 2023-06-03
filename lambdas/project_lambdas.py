import sys

from aws_cdk import (
    Duration,
    aws_lambda)

from constructs import Construct


LAMBDA_TIMEOUT= 300

BASE_LAMBDA_CONFIG = dict (
    timeout=Duration.seconds(LAMBDA_TIMEOUT),       
    memory_size=1024,
    tracing= aws_lambda.Tracing.ACTIVE)

COMMON_LAMBDA_CONF = dict (runtime=aws_lambda.Runtime.PYTHON_3_8, **BASE_LAMBDA_CONFIG)

from layers import (Pillow)


class Lambdas(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        
        pil = Pillow(self, 'Lay')


        self.success_invocation = aws_lambda.Function(
            self, "Success", handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/success_invocation"),
            layers= [pil.layer],
            **COMMON_LAMBDA_CONF)


        self.failure_invocation = aws_lambda.Function(
            self, "Failure", handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/failure_invocation"),**COMMON_LAMBDA_CONF)
        
        self.invoking_lambda = aws_lambda.Function(
            self, "Invoke", handler="lambda_function.lambda_handler",
            layers= [pil.layer],
            code=aws_lambda.Code.from_asset("./lambdas/code/invoking_lambda"),**COMMON_LAMBDA_CONF)
        

        self.new_image = aws_lambda.Function(
            self, "NewImage", handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/new_image"),**COMMON_LAMBDA_CONF)
        
        self.list_images = aws_lambda.Function(
            self, "ListImages", handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/list_images"),**COMMON_LAMBDA_CONF)
        
        self.ws_handler = aws_lambda.Function(
            self, "WSHandler", handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/ws_handler"),**COMMON_LAMBDA_CONF)