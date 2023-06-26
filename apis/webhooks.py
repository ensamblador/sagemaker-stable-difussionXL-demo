
from aws_cdk import (
    aws_apigateway as apg,

    Stack
)

from constructs import Construct


class WebhookApi(Construct):

    def __init__(self, scope: Construct, construct_id: str,lambdas,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        api = apg.RestApi(self, "images")
        api.root.add_cors_preflight(allow_origins=["*"], allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

        images = api.root.add_resource("images", default_integration=apg.LambdaIntegration(lambdas.list_images, allow_test_invoke=False))
        images.add_cors_preflight(allow_origins=["*"], allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

        images.add_method("GET") 





