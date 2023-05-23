from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as ddb
)
from constructs import Construct


REMOVAL_POLICY = RemovalPolicy.DESTROY

TABLE_CONFIG = dict (removal_policy=REMOVAL_POLICY, billing_mode= ddb.BillingMode.PAY_PER_REQUEST)


class Tables(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.invocations = ddb.Table(
            self, "Invocations", 
            partition_key=ddb.Attribute(name="endpoint_name", type=ddb.AttributeType.STRING),
            sort_key = ddb.Attribute(name="invocation_start", type=ddb.AttributeType.STRING),

            **TABLE_CONFIG)

        self.invocations.add_global_secondary_index(
            index_name='InferenceId-index',
            partition_key=ddb.Attribute(name="InferenceId", type=ddb.AttributeType.STRING),
        )
