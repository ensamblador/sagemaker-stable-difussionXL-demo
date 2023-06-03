from constructs import Construct
from aws_cdk import ( 
    aws_s3_deployment as s3deploy, 
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3, RemovalPolicy)


class S3DeployWithDistribution(Construct):
    def __init__(self, scope: Construct, id: str, files_location, dest_prefix,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        self.bucket = s3.Bucket(self, "Bucket",access_control=s3.BucketAccessControl.PRIVATE, removal_policy=RemovalPolicy.DESTROY)
        
        self.distribution = cloudfront.Distribution(self, "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
            origin=origins.S3Origin(self.bucket,origin_path= '/web'),
            response_headers_policy=cloudfront.ResponseHeadersPolicy.CORS_ALLOW_ALL_ORIGINS_WITH_PREFLIGHT_AND_SECURITY_HEADERS
            ),
           
        )

        self.s3deploy = s3deploy.BucketDeployment(self, "Deployment",
            sources=[s3deploy.Source.asset(files_location)],
            destination_bucket = self.bucket, 
            distribution=self.distribution,
            destination_key_prefix=dest_prefix
        )
        



