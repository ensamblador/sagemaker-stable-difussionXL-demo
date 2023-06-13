from aws_cdk import (
    aws_iam as iam,
    RemovalPolicy,
    Stack,
    aws_lambda,
    aws_iam,
    aws_s3,
    aws_s3 as s3,
    aws_lambda_event_sources 
)
from constructs import Construct
from sagemaker import (Model, Endpoint, EndpointConfig)
from topics import Topics
from lambdas import Lambdas
from databases import Tables
from apis import (WebhookApi, WebsocketApi)
from s3_cloudfront import S3DeployWithDistribution


image_uri = '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.10.2-transformers4.17.0-gpu-py38-cu113-ubuntu20.04'
model_uri = 's3://844626608976-sagemaker-us-east-1/infer-prepack-model-upscaling-stabilityai-stable-diffusion-x4-upscaler-fp16-vgarriden.tar.gz'
hosting_bucket_name =  "sddisplayapp-20230610144911-hostingbucket-dev"
#execution_role_arn = 'arn:aws:iam::844626608976:role/Sagemaker-Execution-Role'
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

        website = S3DeployWithDistribution(self, "Img", "website", "")

        bucket = website.bucket #s3.Bucket(self, 'B', versioned=False, removal_policy=RemovalPolicy.DESTROY)

        #bucket = aws_s3.Bucket.from_bucket_name(self, "S3Bucket", bucket_name=hosting_bucket_name )

        execution_role = aws_iam.Role(self, "SMRole",
            assumed_by=aws_iam.ServicePrincipal("sagemaker.amazonaws.com"))
        
        execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess"))
        execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))

        Fn.invoking_lambda.add_event_source(aws_lambda_event_sources.S3EventSource(bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix="images/original/")]
        ))


        Fn.new_image.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(table=Tbl.images, 
            starting_position=aws_lambda.StartingPosition.LATEST)
        )
        


        model = Model(self, 'M', execution_role.role_arn, image_uri, model_uri)

        
        # ml.g5.2xlarge
        
        config1 = EndpointConfig(self, 'C1', bucket.bucket_name, s3_path, model.model.attr_model_name,
                                instance_type="ml.g5.xlarge", instance_count=1,invocation_per_instance=1,
                                error_topic=topics.failure.topic_arn,success_topic=topics.success.topic_arn)
        endpoint1 = Endpoint(self, 'E1', config1.config.attr_endpoint_config_name, "SDx4-Endpoint-g5-xlarge")  
        

        #permisos 
        
        for f in [Fn.success_invocation, Fn.failure_invocation, Fn.invoking_lambda, Fn.new_image, Fn.list_images]:
            bucket.grant_read_write(f)
            Tbl.invocations.grant_full_access(f)
            Tbl.images.grant_full_access(f)
            f.add_environment("BUCKET", bucket.bucket_name)
            f.add_environment("PREFIX", "scaled_images")
            f.add_environment("IMG_PREFIX", "input_images")
            f.add_environment("PAYLOAD_PREFIX", "payload_images")
            f.add_environment("TABLE_NAME",  Tbl.invocations.table_name)
            f.add_environment("IMAGE_TABLE",  Tbl.images.table_name)
            f.add_environment("DISTRUBUTION_NAME",  website.distribution.domain_name)

        Fn.ws_handler.add_environment("CONNECTIONS_TABLE",  Tbl.connections.table_name)
        Fn.new_image.add_environment( "CONNECTIONS_TABLE",  Tbl.connections.table_name)
        Tbl.connections.grant_full_access(Fn.ws_handler)
        Tbl.connections.grant_full_access(Fn.new_image)

        RestApi = WebhookApi(self, "API", lambdas=Fn)
        WSApi = WebsocketApi(self, "WS", lambdas=Fn)
        Fn.new_image.add_environment("WS_ENDPOINT",  WSApi.endpoint)

        Fn.new_image.add_to_role_policy(iam.PolicyStatement(
            actions=["execute-api:ManageConnections"],resources=["*"])
        )


        Fn.invoking_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["sagemaker:InvokeEndpointAsync","sagemaker:InvokeEndpoint"],resources=[f"arn:aws:sagemaker:*:{stk.account}:endpoint/*"])
        )

        Fn.invoking_lambda.add_environment("SM_ENDPOINT", endpoint1.endpoint.attr_endpoint_name)



     