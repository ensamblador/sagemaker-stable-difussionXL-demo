from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
from aws_cdk import aws_apigatewayv2_alpha as apigwv2
# message_handler: lambda.Function


from constructs import Construct


class WebsocketApi(Construct):

    def __init__(self, scope: Construct, construct_id: str,lambdas,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        

        web_socket_api = apigwv2.WebSocketApi(self, "wsapi")
        apigwv2.WebSocketStage(self, "stage",
            web_socket_api=web_socket_api,
            stage_name="dev",
            auto_deploy=True
        )
        web_socket_api.add_route("sendmessage",
            integration=WebSocketLambdaIntegration("SendMessageIntegration", lambdas.ws_handler)
        )
