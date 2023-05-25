from aws_cdk import (
    Stack, 
    aws_sagemaker as sm
)


from constructs import Construct




class Endpoint(Construct):

    def __init__(self, scope: Construct, construct_id: str,endpoint_config_name, endpoint_name=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)

        config = dict(endpoint_config_name=endpoint_config_name)
        if endpoint_name:
            config = dict(**config, endpoint_name=endpoint_name)

        self.endpoint = sm.CfnEndpoint(self, "Endpoint",**config)