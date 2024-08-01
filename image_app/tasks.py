import base64
from celery import shared_task, group
import requests
import os
import json
from django.conf import settings
from .models import GeneratedImage

@shared_task
def generate_image(prompt):
    
    print(prompt)
    payload = {
        "text_prompts": [
            {"text": prompt}
        ],
        "output_format": "png",  
    }
    
    response = requests.post(
                f"{settings.STABILITY_API_URL}",
                headers={
                    "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                data=json.dumps(payload)  
            )
    
    if response.status_code == 200:
        data = response.json()
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        
        for i, image in enumerate(data.get("artifacts", [])):
            base64_data = image.get("base64", "")

            if base64_data:
                try:
                    
                    image_content = base64.b64decode(base64_data)

                    image_filename = f'{prompt.replace(" ", "_")}_{data.get("id", "unknown")}_{i}.png'
                    image_path = os.path.join(settings.MEDIA_ROOT, image_filename)

                    
                    with open(image_path, 'wb') as image_file:
                        image_file.write(image_content)
                    
                    print(f"Saved image to {image_path}")
                
                except base64.binascii.Error as e:
                    print(f"Base64 decoding error: {e}")
            else:
                print("No base64 data found in the response.")

        
        GeneratedImage.objects.create(prompt=prompt, image_url=image_path)
        return image_path

    else:
        
        return {'error': f'Failed to generate image. Status code: {response.status_code}, Message: {response.text}'}



@shared_task
def generate_images_parallel(prompts):
    
    job = group(generate_image.s(prompt) for prompt in prompts)
    result = job.apply_async()
    results = result.get()  
    return results
