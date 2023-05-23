
from aws_cdk import (
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
)

from constructs import Construct



class Topics(Construct):

    def __init__(self, scope: Construct, construct_id: str,Fn, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.success = sns.Topic(self, 'S', display_name='Success Invocation')
        self.failure = sns.Topic(self, 'F', display_name='Failure Invocation')

        self.success.add_subscription(subscriptions.LambdaSubscription(Fn.success_invocation))
        self.failure.add_subscription(subscriptions.LambdaSubscription(Fn.failure_invocation))