from aws_cdk import (
    Stack, 
    aws_sagemaker as sm
)


from constructs import Construct

class EndpointConfig(Construct):

    def __init__(self, scope: Construct, construct_id: str,
                 model_name,
                 instance_type="ml.g5.xlarge", 
                 instance_count=1,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)



        self.config = sm.CfnEndpointConfig(self, "EndpointConfig",
            production_variants=[sm.CfnEndpointConfig.ProductionVariantProperty(
                initial_variant_weight=1,
                model_name=model_name,
                variant_name="variant1",
                initial_instance_count=instance_count,
                instance_type=instance_type,
            )],


        )


class AsyncEndpointConfig(Construct):

    def __init__(self, scope: Construct, construct_id: str,
                 s3_bucket,
                 s3_path,
                 model_name,
                 instance_type="ml.g5.xlarge", 
                 instance_count=1, 
                 invocation_per_instance=1, 
                 error_topic=False,
                 success_topic=False,   
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)


        async_inference_output_properties = dict(
            s3_failure_path=f"s3://{s3_bucket}/{s3_path}/failures",
            s3_output_path=f"s3://{s3_bucket}/{s3_path}/output"
        )

        async_notification_property = None


        if success_topic:
            if error_topic:
                async_notification_property = sm.CfnEndpointConfig.AsyncInferenceNotificationConfigProperty(error_topic=error_topic,success_topic=success_topic)
            else:
                async_notification_property = sm.CfnEndpointConfig.AsyncInferenceNotificationConfigProperty(success_topic=success_topic)

        else:
            if error_topic:
                async_notification_property = sm.CfnEndpointConfig.AsyncInferenceNotificationConfigProperty(error_topic=error_topic)
            else:
                async_notification_property = None

        if async_notification_property:
            async_inference_output_properties = dict(**async_inference_output_properties,notification_config=async_notification_property)


        self.config = sm.CfnEndpointConfig(self, "EndpointConfig",
            production_variants=[sm.CfnEndpointConfig.ProductionVariantProperty(
                initial_variant_weight=1,
                model_name=model_name,
                variant_name="variant1",

                initial_instance_count=instance_count,
                instance_type=instance_type,
            )],

            # the properties below are optional
            async_inference_config=sm.CfnEndpointConfig.AsyncInferenceConfigProperty(
                output_config=sm.CfnEndpointConfig.AsyncInferenceOutputConfigProperty(**async_inference_output_properties),

                # the properties below are optional
                client_config=sm.CfnEndpointConfig.AsyncInferenceClientConfigProperty(
                    max_concurrent_invocations_per_instance=invocation_per_instance
                )
            ),
            

            #endpoint_config_name=endpoint_config_name,


        )
