import torch
import os
from diffusers import FluxPipeline
from huggingface_hub import login

# Load token from environment variable
hf_token = os.environ.get('HUGGINGFACE_TOKEN')
if hf_token:
    login(token=hf_token)
# Load the FLUX.2-klein-9B model
print("Loading FLUX.2-klein-9B model...")
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.2-klein-9B",
    torch_dtype=torch.bfloat16
)

# Move to GPU if available
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")
pipe = pipe.to(device)




# Generate an image from a text prompt
prompt = "A beautiful sunset over mountains with vibrant colors"

print(f"\nGenerating image for prompt: '{prompt}'")
print("Please wait, this may take a moment...")

# Generate the image
image = pipe(
    prompt=prompt,
    height=1024,
    width=1024,
    num_inference_steps=4,
    guidance_scale=3.5,
).images[0]

# Save the image
output_path = "generated_image.png"
image.save(output_path)

print(f"\nImage generated successfully!")
print(f"Image saved at: {output_path}")
