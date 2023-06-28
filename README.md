
# Amazon Sagemaker - Stable Diffusion XL - Demo

TODO: more verbose explanation and proof read

## Diagram and description

![](diagrama.png)

### 1. Image Generation part
1. The idea is to have or develop an Alexa Skill capable of getting the prompt.
2. The prompt is translated to english (english prompts tends to generate better images)
3. Then a Stable Diffusion XL model is invoked, the corresponding image is stored on s3 bucket 

Note: Despite the 3 different s3 bucket icons, it its the same one.

### 2. Upscaling Part
1. A lambda function is triggered on object creation. It handles a image list in dynamodb, notify the website and invoke a second sagemaker endpoint.
2. We use another SD Model (x4 upscaler) that is capable of taking a pic and upscale x4 in both dimensions (effective x16 image size). This is an asycronous because it can take more than 60 seconds.
3. After completion we update our image list with the hires version.


### 3. Website
1. The website is hosted on s3 bucket and delivered by cloudfront. As mentioned earlier this contains the web app assets (react/js) alongside with generated images changing images every 15 seconds.
2. Rest API provided to list images and get the information on startup and on every update.
3. Websocket API is to have a way to show in realtime the new generated images, popup in the screen for 45 seconds.


## Deployment Instructions

### Pre requisites

* Python and [CDK installed](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install) and remember to [bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_bootstrap) your account and region the first time.
* The first model (Stable Diffusion XL) is a [Stability AI Marketplace offering](https://aws.amazon.com/marketplace/pp/prodview-3j5jzj4k6slxs) that you need to subscribe. It's free of charge as model package. 
* Enough [Sagemaker endpoint quotas](https://us-east-1.console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas) for ml.g5.xlarge or bigger. You'll need at least 2.
* A copy of tweaked Stable Difussion x4 upscaler, this is the same from [Sagemaker Jumpstart](https://github.com/aws/amazon-sagemaker-examples/blob/main/introduction_to_amazon_algorithms/jumpstart_upscaling/Amazon_JumpStart_Upscaling.ipynb) but with [xformers](https://github.com/facebookresearch/xformers) in the inference code to work with less RAM. 
* For the web build you'll need [yarn](https://classic.yarnpkg.com/lang/en/docs/install/) installed

    For a copy of the model share a slack message with @garriden and your aws account id. Then you can copy to your account.

    ```python 
    aws s3 cp s3://844626608976-sagemaker-us-east-1/infer-prepack-model-upscaling-stabilityai-stable-diffusion-x4-upscaler-fp16-vgarriden.tar.gz s3://yourbucket/yourprefix/yourkey
    ```

### Deployment instructions

#### Preparation

1. Clone this repo. Remember that CDK needs to be installed and AWS Credentials present (vía environment variables or aws profile). 

    ```bash 
    git clone https://github.com/ensamblador/sagemaker-stable-difussionXL-demo.git
    cd sagemaker-stable-difussionXL-demo
    ```
2. Create a virtual environment and activate it. Then, install the required python packages.

    ```bash 
    python3 -m venv .venv
    ```
    ```bash 
    source .venv/bin/activate
    ```
    ```bash
    pip install -r requirements.txt
    ```

3. Edit the `config.py` with the stable difussion model package name from your susbscription. Optionally change to a instance_type that you have (ml.g5 family). 

    ```python

    # generative model SD
    stable_difussion_xl = dict (
        model_package_name = "from your subscription",
        instance_type= "ml.g5.xlarge",
        ...
    )

    # upsacaler 
    upscaler =  dict (
        image_uri = '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.10.2-transformers4.17.0-gpu-py38-cu113-ubuntu20.04',
        model_uri = 's3://844626608976-sagemaker-us-east-1/infer-prepack-model-upscaling-stabilityai-stable-diffusion-x4-upscaler-fp16-vgarriden.tar.gz',
        instance_type= 'ml.g5.xlarge',
        ...
    )
    ```
    Optional: if you want to change Stack Name or Tags, go to `app.py` in the same folder.

4. Build de react web app

    ```bash
    cd sd-display-app
    yarn install
    yarn build
    ```

    This will create a `build` folder inside sd-display-app

4. Deploy all the things!

    Take a look at the code in `stable_difussion/stable_difussion_stack.py`. You'll basically this cdk code accounts for all the lambdas, buckets, dynamodb, apis, and sagemaker endpoints. You can view the generated cloudformation template with `cdk synth`. 

    OK, go back to the main folder:

    ```bash
    cd ..
    cdk deploy
    ```
    confirm the deployment:

    ```
    Do you wish to deploy these changes (y/n)?y
    ```

    After like 9-10 minutes all the backend is deployed. You'll some outputs at the end

    ```bash
    SDXL: deploying... [1/1]
    SDXL: creating CloudFormation changeset...

    ✅  SDXL

    ✨  Deployment time: 536.71s

    Outputs:
    SDXL.APIimagesEndpoint = https://xxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
    SDXL.WSwebsocket = wss://yyyyyyy.execute-api.us-east-1.amazonaws.com/dev
    SDXL.wwwWebsite = zzzzz.cloudfront.net
    ```
4. Update Web app with the new APIs and re-deploy that.

    Well, grab the two API url from outputs (here in the cli or you can go to the cloudformation stack outputs) and use that in `sd-display-app/src/apis.js`. Those are the new deployed APIs:

    ```js
    const APIS = {
        images: "https://xxxxxxx.execute-api.us-east-1.amazonaws.com/prod/",
        socket: "wss://yyyyyyy.execute-api.us-east-1.amazonaws.com/dev"
    }

    export default APIS
    ```

    Save that and, again in `sd-display-app`, run 

    ```bash
    cd sd-display-app
    yarn build
    ````

    go back to the cdk folder an re-deploy

    ```bash
    cd ..
    cdk deploy
    ```

    After this second deployment check If you can browse to `zzzzz.cloudfront.net` without errors and you're good to go! otherwise review the previous steps


5. The Alexa Skill part.

    TODO





Thanks to: 
- [Felipe Chirinos](chirinf@amazon.com) 
- [Maximiliano Kretowicz](maxkp@amazon.com) 
- [Enrique Rodriguez](garriden@amazon.com) 

Enjoy!
