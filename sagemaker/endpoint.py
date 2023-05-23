from aws_cdk import (
    Stack, 
    aws_sagemaker as sm
)


from constructs import Construct




class Endpoint(Construct):

    def __init__(self, scope: Construct, construct_id: str,endpoint_config_name, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)


        self.endpoint = sm.CfnEndpoint(self, "Endpoint",
            endpoint_config_name=endpoint_config_name,
            #endpoint_name="endpointName",
        )