from aws_cdk import (
    Stack, 
    aws_iam as iam,
    aws_sagemaker as sm
)
from sagemaker import (Model, Endpoint, EndpointConfig, AsyncEndpointConfig)


from constructs import Construct
from config import (upscaler, stable_difussion_xl)


upsacaler_image_uri = upscaler.get("image_uri")
upscaler_model_uri = upscaler.get("model_uri")
upscaler_s3_path = upscaler.get("s3_path")
upscaler_instance_count =  upscaler.get("instance_count")
upscaler_invocation_per_instance =  upscaler.get("invocation_per_instance")
upscaler_instance_type = upscaler.get("instance_type")


sdxl_model_package_name = stable_difussion_xl.get("model_package_name")
sdxl_enable_network_isolation = stable_difussion_xl.get("enable_network_isolation")
sdxl_instance_type = stable_difussion_xl.get("instance_type")
sdxl_instance_count =  stable_difussion_xl.get("instance_count")



class StableDiffusionDeployments(Construct):

    def __init__(self, scope: Construct, construct_id: str, bucket, topics, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        execution_role = iam.Role(self, "SMRole", assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"))
        execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess"))
        execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))

        model_sd_xl = Model(self, 'M_SDXL', execution_role.role_arn, 
                      model_package_name=sdxl_model_package_name,
                      enable_network_isolation=True if sdxl_enable_network_isolation else False)
        
        config_sd_xl = EndpointConfig(self, 'C_SDXL',  model_sd_xl.model.attr_model_name,
                                instance_type=sdxl_instance_type, instance_count=sdxl_instance_count)
        
        endpoint_sd_xl = Endpoint(self, 'E_SDXL', config_sd_xl.config.attr_endpoint_config_name)  


        model_upscaler = Model(self, 'M_x4', execution_role.role_arn, upsacaler_image_uri, upscaler_model_uri)


        config_upsacaler = AsyncEndpointConfig(self, 'C_x4', bucket.bucket_name, upscaler_s3_path, model_upscaler.model.attr_model_name,
                                instance_type=upscaler_instance_type, instance_count=upscaler_instance_count,
                                invocation_per_instance=upscaler_invocation_per_instance,
                                error_topic=topics.failure.topic_arn,success_topic=topics.success.topic_arn)
        
        
        endpoint_upscaler = Endpoint(self, 'E_x4', config_upsacaler.config.attr_endpoint_config_name)  
        
        self.endpoint_upscaler_name = endpoint_upscaler.endpoint.attr_endpoint_name
        self.endpoint_sdxl_name     = endpoint_sd_xl.endpoint.attr_endpoint_name