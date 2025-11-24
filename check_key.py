import os
import google.generativeai as genai
import time

print("Attempting to connect to Google AI...")

try:
    # 1. Get the key from the environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n!!! ERROR !!!")
        print("GEMINI_API_KEY environment variable not found.")
        print("Please set the key in your terminal first.")
        exit()

    genai.configure(api_key=api_key)

    # 2. List the models your key has access to
    print("\nListing available models for your key...")
    
    # --- MODIFIED SECTION ---
    # We will try to find a reliable, standard model first.
    # These are good, common models from your list.
    preferred_models = [
        "models/gemini-2.5-flash",
        "models/gemini-pro-latest"
    ]
    
    found_model = None
    all_usable_models = []
    
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            all_usable_models.append(m.name)
            if m.name in preferred_models:
                found_model = m.name # We found a preferred one!
                break # Stop looking
    
    # If we didn't find a preferred one, just pick the first one from the list
    if not found_model and all_usable_models:
        found_model = all_usable_models[0] # Pick the first usable one
    # --- END MODIFIED SECTION ---

    if not found_model:
        print("\n!!! ERROR !!!")
        print("Your key is valid, but no usable models were found.")
        exit()
        
    # 3. Try a "Hello World" call
    print(f"\nAttempting a test call with model: {found_model}...")
    model = genai.GenerativeModel(found_model)
    response = model.generate_content("Hello")
    print(f"  > AI Response: {response.text}")

    print("\n" + "="*50)
    print("✅  SUCCESS! Your API key is valid and has a working quota.")
    print(f"We will use the model '{found_model}' for the project.")
    print("="*50)

except Exception as e:
    print("\n" + "="*50)
    print("❌  FAILURE! The test failed.")
    print(f"THE ERROR WAS: {e}")
    print("\nThis is likely a QUOTA problem with this specific model.")
    print("If this continues, try a brand new API key from a different Google account.")
    print("="*50)