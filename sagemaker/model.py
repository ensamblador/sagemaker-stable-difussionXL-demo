from aws_cdk import (
    Stack, 
    aws_sagemaker as sm
)


from constructs import Construct



class Model(Construct):

    def __init__(self, scope: Construct, construct_id: str,
                 execution_role_arn,
                 image_uri,
                 model_uri,
                  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)


        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.

        # environment: Any

        self.model = sm.CfnModel(self, "model",
            execution_role_arn=execution_role_arn,
            #model_name=model_name,
            primary_container=sm.CfnModel.ContainerDefinitionProperty(
                image=image_uri,
                model_data_url=model_uri,

            )
        ) 
