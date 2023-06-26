from aws_cdk import (
    Stack, 
    aws_sagemaker as sm
)


from constructs import Construct

class Model(Construct):

    def __init__(self, scope: Construct, construct_id: str,
                 execution_role_arn,
                 image_uri=None,
                 model_uri=None,
                 model_package_name=None,
                 enable_network_isolation = False,
                  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)

        primary_container_params =  dict (image=image_uri, model_data_url=model_uri)
        if model_package_name:
            primary_container_params =  dict(
                model_package_name= model_package_name,
                )

        self.model = sm.CfnModel(self, "model",
            execution_role_arn=execution_role_arn,
            enable_network_isolation = enable_network_isolation,
            #model_name=model_name,
            primary_container=sm.CfnModel.ContainerDefinitionProperty(
                **primary_container_params
            )
        ) 
