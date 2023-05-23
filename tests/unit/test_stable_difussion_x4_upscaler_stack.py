import aws_cdk as core
import aws_cdk.assertions as assertions

from stable_difussion_x4_upscaler.stable_difussion_x4_upscaler_stack import StableDifussionX4UpscalerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in stable_difussion_x4_upscaler/stable_difussion_x4_upscaler_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = StableDifussionX4UpscalerStack(app, "stable-difussion-x4-upscaler")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
