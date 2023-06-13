from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
from aws_cdk import aws_apigatewayv2_alpha as apigwv2
from aws_cdk import Stack

# message_handler: lambda.Function


from constructs import Construct


class WebsocketApi(Construct):
    def __init__(self, scope: Construct, construct_id: str, lambdas, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)

        self.web_socket_api = apigwv2.WebSocketApi(
            self,
            "wsapi",
            connect_route_options=apigwv2.WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration(
                    "connectIntegration", lambdas.ws_handler
                )
            ),
            disconnect_route_options=apigwv2.WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration(
                    "disconnectIntegration", lambdas.ws_handler
                )
            ),
        )
        apigwv2.WebSocketStage(
            self,
            "stage",
            web_socket_api=self.web_socket_api,
            stage_name="dev",
            auto_deploy=True,
        )
        self.web_socket_api.add_route(
            "onmessage",
            integration=WebSocketLambdaIntegration(
                "SendMessageIntegration", lambdas.ws_handler
            ),
        )


        self.endpoint = f'https://{self.web_socket_api.api_id}.execute-api.{stk.region}.amazonaws.com/dev'
