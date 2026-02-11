"""Check available Gemini models."""
import google.generativeai as genai
from decouple import config

api_key = config('GEMINI_API_KEY', default='')
genai.configure(api_key=api_key)

print("Available Gemini models:")
print("="*80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\nModel: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Supported methods: {model.supported_generation_methods}")
