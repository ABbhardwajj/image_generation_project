

    
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import generate_images_parallel
import json

class GenerateImagesView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            
             
            data = json.loads(request.body.decode('utf-8'))
            prompts_data = data.get('prompts')
            
            if not prompts_data:
                return JsonResponse({'error': 'No prompts provided'}, status=400)
            
            
            prompts = [prompt_obj['prompt'] for prompt_obj in prompts_data]
            
            
            result_id = generate_images_parallel.delay(prompts)
            
            return JsonResponse({'status': 'Processing', 'task_id': result_id.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



    