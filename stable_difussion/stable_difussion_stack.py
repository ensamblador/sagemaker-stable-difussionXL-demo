from aws_cdk import (
    aws_iam as iam,
    Stack,
    aws_lambda,
    aws_s3 as s3,
    aws_lambda_event_sources 
)
from constructs import Construct
from sagemaker import StableDiffusionDeployments
from topics import Topics
from lambdas import Lambdas
from databases import Tables
from apis import (WebhookApi, WebsocketApi)
from s3_cloudfront import S3DeployWithDistribution

from config import (stable_difussion_xl)


class StableDifussionX4UpscalerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        Tbl = Tables(self, 'Tbl')
        Fn  = Lambdas(self,'Fn')
        topics =  Topics (self, 'SNS', Fn=Fn)

        website = S3DeployWithDistribution(self, "www", "sd-display-app/build", "")

        bucket = website.bucket 

        sd = StableDiffusionDeployments(self, "SD", bucket, topics)

        Fn.invoking_lambda.add_event_source(aws_lambda_event_sources.S3EventSource(bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix="images/original/")]
        ))

        Fn.new_image.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(table=Tbl.images, 
            starting_position=aws_lambda.StartingPosition.LATEST)
        )


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

        Fn.invoking_lambda.add_environment("SM_ENDPOINT", sd.endpoint_upscaler_name)

        Fn.text2image.add_environment("bucket_folder", stable_difussion_xl.get("s3_path"))
        Fn.text2image.add_environment("bucket_name",  bucket.bucket_name)
        Fn.text2image.add_environment("sagemaker_endpoint", sd.endpoint_sdxl_name)
        Fn.text2image.add_environment("seed", stable_difussion_xl.get("seed"))
        Fn.text2image.add_environment("style_preset", stable_difussion_xl.get("style_preset"))
        Fn.text2image.add_environment("width", stable_difussion_xl.get("width"))
        Fn.text2image.add_environment("random", "")


        Fn.text2image.add_to_role_policy(iam.PolicyStatement(
            actions=["sagemaker:InvokeEndpointAsync","sagemaker:InvokeEndpoint"],resources=[f"arn:aws:sagemaker:*:{stk.account}:endpoint/*"])
        )
        Fn.text2image.add_to_role_policy(iam.PolicyStatement( actions=["translate:*"], resources=['*']))

        bucket.grant_read_write(Fn.text2image)




     