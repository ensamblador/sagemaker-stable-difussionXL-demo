from aws_cdk import (
    aws_iam as iam,
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
    aws_lambda_event_sources 
)
from constructs import Construct
from sagemaker import (Model, Endpoint, EndpointConfig)
from topics import Topics
from lambdas import Lambdas
from databases import Tables


image_uri = '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.10.2-transformers4.17.0-gpu-py38-cu113-ubuntu20.04'
model_uri = 's3://844626608976-sagemaker-us-east-1/infer-prepack-model-upscaling-stabilityai-stable-diffusion-x4-upscaler-fp16-vgarriden.tar.gz'
execution_role_arn = 'arn:aws:iam::687406509163:role/Sagemaker-Execution-Role'
#model_name = "cdk-upscaler-x4-model"
#endpoint_name = "cdk-upscaler-x4-endpoint"
#endpoint_config_name = f"{endpoint_name}-config"
s3_path = "inferences"

class StableDifussionX4UpscalerStack(Stack):



    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        Tbl = Tables(self, 'Tbl')

        Fn  = Lambdas(self,'Fn')
        topics =  Topics (self, 'SNS', Fn=Fn)
        bucket = s3.Bucket(self, 'B', versioned=False, removal_policy=RemovalPolicy.DESTROY)


        Fn.invoking_lambda.add_event_source(aws_lambda_event_sources.S3EventSource(bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix="input_images/")]
        ))

        model = Model(self, 'M', execution_role_arn, image_uri, model_uri)

        
        # ml.g5.2xlarge
        
        config1 = EndpointConfig(self, 'C1', bucket.bucket_name, s3_path, model.model.attr_model_name,
                                instance_type="ml.g5.xlarge", instance_count=4,invocation_per_instance=1,
                                error_topic=topics.failure.topic_arn,success_topic=topics.success.topic_arn)
        endpoint1 = Endpoint(self, 'E1', config1.config.attr_endpoint_config_name, "SDx4-Endpoint-g5-xlarge")  
        
        
        '''
        # ml.g5.4xlarge
        config2 = EndpointConfig(self, 'C2', bucket.bucket_name, s3_path, model.model.attr_model_name,
                                instance_type="ml.g5.4xlarge", instance_count=1,invocation_per_instance=1,
                                error_topic=topics.failure.topic_arn,success_topic=topics.success.topic_arn)
        endpoint2 = Endpoint(self, 'E2', config2.config.attr_endpoint_config_name, "SDx4-Endpoint-g5-4xlarge")


        # ml.g5.8xlarge
        config3 = EndpointConfig(self, 'C3', bucket.bucket_name, s3_path, model.model.attr_model_name,
                                instance_type="ml.g5.8xlarge", instance_count=1,invocation_per_instance=1,
                                error_topic=topics.failure.topic_arn,success_topic=topics.success.topic_arn)
        endpoint3 = Endpoint(self, 'E3', config3.config.attr_endpoint_config_name, "SDx4-Endpoint-g5-8xlarge")


        # ml.g5.xlarge
        config4 = EndpointConfig(self, 'C4', bucket.bucket_name, s3_path, model.model.attr_model_name,
                                instance_type="ml.g5.xlarge", instance_count=1,invocation_per_instance=1,
                                error_topic=topics.failure.topic_arn,success_topic=topics.success.topic_arn)
        endpoint4 = Endpoint(self, 'E4', config4.config.attr_endpoint_config_name, "SDx4-Endpoint-g5-xlarge")


        # ml.p3.2xlarge
        config8 = EndpointConfig(self, 'C8', bucket.bucket_name, s3_path, model.model.attr_model_name,
                                instance_type="ml.p3.2xlarge", instance_count=1,invocation_per_instance=1,
                                error_topic=topics.failure.topic_arn,success_topic=topics.success.topic_arn)
        endpoint8 = Endpoint(self, 'E8', config4.config.attr_endpoint_config_name, "SDx4-Endpoint-p3-2xlarge") 
        '''

        #permisos 
        
        for f in [Fn.success_invocation, Fn.failure_invocation, Fn.invoking_lambda]:
            bucket.grant_read_write(f)
            Tbl.invocations.grant_full_access(f)
            f.add_environment("BUCKET", bucket.bucket_name)
            f.add_environment("PREFIX", "scaled_images")
            f.add_environment("IMG_PREFIX", "input_images")
            f.add_environment("PAYLOAD_PREFIX", "payload_images")
            f.add_environment("TABLE_NAME",  Tbl.invocations.table_name)


        Fn.invoking_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["sagemaker:InvokeEndpointAsync","sagemaker:InvokeEndpoint"],resources=[f"arn:aws:sagemaker:*:{stk.account}:endpoint/*"])
        )

        Fn.invoking_lambda.add_environment("SM_ENDPOINT", endpoint1.endpoint.attr_endpoint_name)



     