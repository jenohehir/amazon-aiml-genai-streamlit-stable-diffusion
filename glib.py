import os
import io
import boto3
import json
import base64
from PIL import Image
from PIL import ImageOps
from io import BytesIO
import sagemaker
from stability_sdk_sagemaker.predictor import StabilityPredictor
from stability_sdk.api import GenerationRequest, GenerationResponse, TextPrompt
import streamlit as st
from resizeimage import resizeimage

# SM Jumpstart Consts
region_name = "us-west-2"
storage_bucket = "perth-recap-mugshots"
sm_sdxl_ep = "sdxl-1-0-jumpstart-2023-12-06-03-16-48-040"

# Bedrock Consts
endpoint_url = "bedrock-endpoint-url"
bedrock_model_id = 'stability.stable-diffusion-xl'

def checkFileinS3(filename):
    session = boto3.Session()
    s3 = session.client('s3')
    results = s3.list_objects(Bucket=storage_bucket, Prefix=filename)
    return ('Contents' in results)

def uploadFileToS3(fileName, fileBytes):
    session = boto3.Session()
    s3 = session.client('s3', region_name=region_name)
    s3.upload_fileobj(io.BytesIO(fileBytes), storage_bucket, fileName)

# Request for an image from SDXL given a text-prompt
# def smjs_create_img_from_prompt(text):
#     session = boto3.session.Session()
#     deployed_model = StabilityPredictor(endpoint_name=sm_sdxl_ep, 
#                                         sagemaker_session=sagemaker.Session(boto_session=session))
#     output_img = deployed_model.predict(GenerationRequest(text_prompts=[TextPrompt(text=text)],
#                                         style_preset="cinematic", seed = 3))
#     return output_img

# def smjs_create_img_from_img_and_prompt(text, image, slider):
#     strength = 0.5 + (slider / 100)*(0.45)
#     session = boto3.session.Session()
#     deployed_model = StabilityPredictor(endpoint_name=sm_sdxl_ep, 
#                                         sagemaker_session=sagemaker.Session(boto_session=session))
#     img = deployed_model.predict(GenerationRequest(text_prompts=[TextPrompt(text=text)],
#                                         init_image=image,
#                                         cfg_scale=9,
#                                         image_strength=strength,
#                                         seed=42))
    return img

# Extract the image out from the response
def decode_image(model_response: GenerationResponse):
    image = model_response.artifacts[0].base64
    image_data = base64.b64decode(image.encode())
    image = Image.open(io.BytesIO(image_data))
    result_io = BytesIO()
    image.save(result_io, format=image.format)
    return result_io

# When taking pictures from a smart-phone, they have rotation metadata
# Remove rotation and resize to 512 to 512. There will be some cropping.
def remove_rotation(image_bytes):
    image_io = BytesIO(image_bytes)
    image = Image.open(image_io)
    new_one = ImageOps.exif_transpose(image)
    new_one = resizeimage.resize_cover(new_one, [512,512])
    new_img_io = BytesIO()
    new_one.save(new_img_io, format="PNG")
    return new_img_io
    
def get_resized_image_io(image_bytes):
    image_io = BytesIO(image_bytes)
    image = Image.open(image_io)
    resized_image = image.resize((512, 512))
    resized_io = BytesIO()
    resized_image.save(resized_io, format=image.format)
    return resized_io

def prepare_image_for_endpoint(image_bytes):
    resized_io = get_resized_image_io(image_bytes)
    img_str = base64.b64encode(resized_io.getvalue()).decode("utf-8")
    return img_str

def get_stability_ai_response_image(response):
    response = json.loads(response.get('body').read())
    image_data = base64.b64decode(response["artifacts"][0]["base64"])
    return BytesIO(image_data)

def get_altered_image_from_model(prompt_content, image_bytes, img_strength, seed, style_preset):
    if image_bytes is None:
        #img = smjs_create_img_from_prompt(prompt_content)
        img = bedrock_create_img_from_img_and_prompt(prompt_content, None, 80, seed, style_preset)
        return img
    else:
        img_str = prepare_image_for_endpoint(image_bytes)
        #img = smjs_create_img_from_img_and_prompt(prompt_content, img_str, img_strength)
        img = bedrock_create_img_from_img_and_prompt(prompt_content, img_str, img_strength, seed, style_preset)
        return img

def get_stability_ai_request_body(prompt, strength, image_str = None, seed=0, style_preset=''):
    # see https://platform.stability.ai/docs/features/api-parameters
    strength = (strength/100)
    body = {"text_prompts": [{"text": prompt}],"cfg_scale":12, "image_strength": strength, "seed": seed, "style_preset": style_preset, "steps":50}
    print(body)
    if image_str:
        body["init_image"] = image_str
    #    body["start_schedule"] = 0.8
    #    body["stop_schedule"] = 0.8
    return json.dumps(body)

def bedrock_create_img_from_img_and_prompt (text, image, strength, seed, style_preset):
    body = get_stability_ai_request_body(text, strength, image, seed, style_preset)
    bedrock = boto3.client(service_name='bedrock-runtime', region_name=region_name)
    response = bedrock.invoke_model(body=body, modelId="stability.stable-diffusion-xl-v1", contentType="application/json", accept="application/json")
    output = get_stability_ai_response_image(response)
    return output
