
# generative model SD

stable_difussion_xl = dict (
    model_package_name = "arn:aws:sagemaker:region:account:model-package/sdxl-beta-v0-8-7189b86-fdaf7570ea6635a4a4b0fd3c750691d0",
    enable_network_isolation = True,
    instance_type= "ml.g5.xlarge",
    instance_count=1,
    s3_path = 'images/original/',
    style_preset = 'cinametic',
    width= '512',
    seed='0'
)


# upsacaler 

upscaler =  dict (
    image_uri = '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.10.2-transformers4.17.0-gpu-py38-cu113-ubuntu20.04',
    model_uri = 's3://844626608976-sagemaker-us-east-1/infer-prepack-model-upscaling-stabilityai-stable-diffusion-x4-upscaler-fp16-vgarriden.tar.gz',
    s3_path = 'inferences',
    instance_type= 'ml.g5.xlarge',
    instance_count=1,
    invocation_per_instance=1
)
