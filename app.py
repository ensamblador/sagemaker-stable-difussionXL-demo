#!/usr/bin/env python3
import os
from aws_cdk import (Tags)

import aws_cdk as cdk

from stable_difussion import StableDifussionX4UpscalerStack
TAGS = {
    'application': 'Stable DiffusionXL and Upscaler Demo',
    'cliente': 'CloudExperience'
}



app = cdk.App()
stk = StableDifussionX4UpscalerStack(app, "SDXL")

if TAGS.keys():
    for k in TAGS.keys():
        Tags.of(stk).add(k, TAGS[k])
app.synth()
