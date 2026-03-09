"""
Script to generate all burger ingredient images using OpenAI's image generation API
"""
import asyncio
import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

load_dotenv()

# Define all ingredients that need images
INGREDIENTS = {
    # Buns
    "bun_top": "Top half of a sesame seed burger bun, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "bun_bottom": "Bottom half of a sesame seed burger bun, professional food photography, white background, PNG transparent, high quality, studio lighting",
    
    # Patties
    "beef_patty": "Grilled beef burger patty, juicy and perfectly cooked, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "chicken_patty": "Grilled chicken burger patty, golden brown, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "veggie_patty": "Vegetarian burger patty with visible vegetables, professional food photography, white background, PNG transparent, high quality, studio lighting",
    
    # Cheese
    "cheese_slice": "Melted cheddar cheese slice, dripping slightly, professional food photography, white background, PNG transparent, high quality, studio lighting",
    
    # Vegetables
    "lettuce": "Fresh green lettuce leaf, crisp and vibrant, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "tomato": "Fresh tomato slice, red and juicy, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "onion": "White onion ring slices, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "pickle": "Pickle slices, bright green, professional food photography, white background, PNG transparent, high quality, studio lighting",
    
    # Extras
    "bacon": "Crispy bacon strips, golden brown, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "jalapeno": "Fresh jalapeño slices, bright green, professional food photography, white background, PNG transparent, high quality, studio lighting",
    
    # Sauces (as dripping layers)
    "ketchup_layer": "Ketchup sauce layer for burger, red, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "mayo_layer": "Mayonnaise sauce layer for burger, white and creamy, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "bbq_layer": "BBQ sauce layer for burger, dark brown, professional food photography, white background, PNG transparent, high quality, studio lighting",
    "mustard_layer": "Yellow mustard sauce layer for burger, professional food photography, white background, PNG transparent, high quality, studio lighting",
}

async def generate_all_images():
    """Generate all ingredient images"""
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        print("ERROR: EMERGENT_LLM_KEY not found in environment variables")
        return
    
    # Create output directory
    output_dir = Path("/app/frontend/public/ingredients")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting image generation for {len(INGREDIENTS)} ingredients...")
    print(f"Using API key: {api_key[:20]}...")
    print(f"Output directory: {output_dir}")
    
    # Initialize image generator
    image_gen = OpenAIImageGeneration(api_key=api_key)
    
    for ingredient_name, prompt in INGREDIENTS.items():
        try:
            print(f"\n🎨 Generating: {ingredient_name}...")
            print(f"   Prompt: {prompt[:80]}...")
            
            # Generate image
            images = await image_gen.generate_images(
                prompt=prompt,
                model="gpt-image-1",
                number_of_images=1
            )
            
            if images and len(images) > 0:
                # Save image
                output_path = output_dir / f"{ingredient_name}.png"
                with open(output_path, "wb") as f:
                    f.write(images[0])
                
                print(f"   ✅ Saved to: {output_path}")
            else:
                print(f"   ❌ No image generated for {ingredient_name}")
                
        except Exception as e:
            print(f"   ❌ Error generating {ingredient_name}: {str(e)}")
            continue
    
    print("\n" + "="*60)
    print("✅ Image generation complete!")
    print(f"📁 Images saved to: {output_dir}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(generate_all_images())
