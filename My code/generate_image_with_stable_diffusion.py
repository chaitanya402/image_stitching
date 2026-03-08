from diffusers import StableDiffusionPipeline
import torch

def generate_image(prompt, output_path):
    # Load the Stable Diffusion pipeline
    pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    # Generate the image
    image = pipe(prompt).images[0]

    # Save the image
    image.save(output_path)

if __name__ == "__main__":
    # Define the prompt
    prompt = "A red racing suit on display with a 20% SALE text and emojis 🎉 and 🎁, professional studio lighting, high quality."

    # Define the output path
    output_path = "video_editor_platform/edited_images/generated_racing_suit_promo.jpg"

    # Generate the image
    generate_image(prompt, output_path)

    print(f"Image generated and saved at {output_path}")