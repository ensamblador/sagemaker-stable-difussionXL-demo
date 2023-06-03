#!/usr/bin/env python3
import os
from aws_cdk import (Tags)

import aws_cdk as cdk

from stable_difussion_x4_upscaler.stable_difussion_x4_upscaler_stack import StableDifussionX4UpscalerStack

TAGS = {
    'application': 'Stable Diffusion 2.1 x 4 Upscaler Demo',
    'cliente': 'CloudExperience'
}

app = cdk.App()
stk = StableDifussionX4UpscalerStack(app, "SDx4UpscalerV2",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )
if TAGS.keys():
    for k in TAGS.keys():
        Tags.of(stk).add(k, TAGS[k])

app.synth()
