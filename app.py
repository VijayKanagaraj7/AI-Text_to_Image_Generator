import streamlit as st
import os
from PIL import Image
import io
import base64
from monster_api_client import generate_image, get_available_models, VALID_MODELS
from text_preprocessing import preprocess_text

st.set_page_config(
    page_title="Text-to-Image Generator",
    page_icon="🖼️",
    layout="wide"
)

# API Key setup
DEFAULT_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImU1ZWY5NmYwMGU2YjExNDBhMTA1MjE3ODZjMmY0ZDM1IiwiY3JlYXRlZF9hdCI6IjIwMjUtMDUtMDFUMTA6MTI6NTQuOTQ3OTk5In0.BaZtc1HytcFMPECzTtlNCWND8BWfDfY949EdanagAhU"
api_key = os.getenv("MONSTER_API_KEY", DEFAULT_API_KEY)

def display_images(images):
    """Display generated images in a grid"""
    cols = st.columns(len(images))
    for i, (img_data, img_info) in enumerate(images):
        with cols[i]:
            try:
                # Request the actual image URL instead of trying to decode the base64
                if isinstance(img_data, str) and img_data.startswith("https://"):
                    # If the API returned a URL instead of base64
                    st.image(img_data, use_column_width=True)
                    image_url = img_data
                    
                    # Display generation info
                    st.write(f"**Seed:** {img_info.get('seed', 'N/A')}")
                    
                    # Add a link to download the image
                    st.markdown(f'<a href="{image_url}" target="_blank" download="generated_image_{i}.png">Download Image</a>', unsafe_allow_html=True)
                
                elif isinstance(img_data, dict) and "url" in img_data:
                    # If the API returns a dictionary with a URL key
                    image_url = img_data["url"]
                    st.image(image_url, use_column_width=True)
                    
                    # Display generation info
                    st.write(f"**Seed:** {img_info.get('seed', 'N/A')}")
                    
                    # Add a link to download the image
                    st.markdown(f'<a href="{image_url}" target="_blank" download="generated_image_{i}.png">Download Image</a>', unsafe_allow_html=True)
                
                elif isinstance(img_data, str):
                    # Display what we received for debugging
                    st.write(f"Raw data seems to be text, length: {len(img_data)}")
                    
                    # Show a sample of the text
                    if len(img_data) > 30:
                        st.code(img_data[:30] + "...", language="text")
                    
                    # Try to load as URL anyway
                    try:
                        st.image(img_data, use_column_width=True)
                        st.write(f"**Seed:** {img_info.get('seed', 'N/A')}")
                    except Exception as e:
                        st.error(f"Could not load image: {str(e)}")
                
                else:
                    # For any other type of data
                    st.error(f"Unsupported image data format: {type(img_data)}")
                    st.json(img_data if isinstance(img_data, (dict, list)) else {"value": str(img_data)})
                    
            except Exception as e:
                st.error(f"Error displaying image {i}: {str(e)}")

def main():
    st.title("🖼️ Text-to-Image Generator")
    st.subheader("Generate images from text prompts using Stable Diffusion")
    
    with st.expander("About this app", expanded=False):
        st.markdown("""
        This application uses the Monster API to generate images from text prompts using Stable Diffusion models.
        
        **Features:**
        - Text preprocessing and cleaning
        - Custom prompt engineering
        - Various configuration options
        - Multiple image generation
        - Image downloading
        
        Enter your prompt in the text area below and adjust the parameters to generate images.
        """)
    
    # Text input section
    st.header("Enter your prompt")
    prompt = st.text_area("Text prompt", 
                          height=100,
                          placeholder="Describe the image you want to generate...")
    
    # Preprocessing toggle
    preprocess = st.checkbox("Preprocess text", value=False, 
                            help="Clean and preprocess the prompt before sending to the model")
    
    
    
    # Negative prompt
    neg_prompt = st.text_area("Negative prompt", 
                             value="unreal, fake, disfigured, poor quality, bad, ugly, blurry",
                             help="Specify what you don't want in the image")
    
    # Try to fetch available models or use the predefined list
    if "available_models" not in st.session_state:
        try:
            st.session_state.available_models = get_available_models(api_key)
        except Exception as e:
            st.warning(f"Could not fetch available models: {str(e)}")
            st.session_state.available_models = VALID_MODELS

    # Advanced settings
    with st.expander("Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            model = st.selectbox("Model", 
                                options=st.session_state.available_models,
                                index=0,
                                help="Select a Stable Diffusion model to use for image generation")
            num_samples = st.slider("Number of samples", min_value=1, max_value=4, value=2)
            steps = st.slider("Steps", min_value=20, max_value=100, value=50)
            guidance_scale = st.slider("Guidance scale", min_value=1.0, max_value=20.0, value=7.5, step=0.5)
            
        with col2:
            aspect_ratio = st.selectbox("Aspect ratio", 
                                      ["square", "portrait", "landscape"], 
                                      index=0)
            enable_enhance = st.checkbox("Enable enhance", value=True)
            enable_optimize = st.checkbox("Enable optimize", value=True)
            safety_filter = st.checkbox("Safety filter", value=True)
            
        seed = st.number_input("Seed (0 for random)", min_value=0, value=0, step=1)
        
        # Display information about the model
        st.info("""
        **Currently Available Model:**  
        Currently, only the 'sdxl-base' model is confirmed to work reliably with this API key.
        Other models were tested but returned errors.
        """)
        # No need to show a list since we only have one model
    
    # Generate button
    generate_col1, generate_col2 = st.columns([3, 1])
    with generate_col1:
        generate_button = st.button("🎨 Generate Images", type="primary", use_container_width=True)
    with generate_col2:
        clear_button = st.button("🗑️ Clear", type="secondary", use_container_width=True)
    
    # Store generation state and results
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = None
    
    if clear_button:
        st.session_state.generated_images = None
    
    # Generate images when button is clicked
    if generate_button and prompt:
        with st.spinner("Generating images... This may take a moment."):
            try:
                # Prepare input data
                input_data = {
                    "prompt": prompt,
                    "negprompt": neg_prompt,
                    "samples": num_samples,
                    "enhance": enable_enhance,
                    "optimize": enable_optimize,
                    "safe_filter": safety_filter,
                    "steps": steps,
                    "aspect_ratio": aspect_ratio,
                    "guidance_scale": guidance_scale,
                }
                
                # Add seed if not random
                if seed > 0:
                    input_data["seed"] = seed
                
                # Generate images
                result = generate_image(api_key, model, input_data)
                
                # Store the raw API response for debugging
                st.session_state.api_response = result
                
                # Extract images if available
                if result and "output" in result:
                    # Log the complete response structure
                    st.write("API Response received. Processing images...")
                    
                    # Extract images and their information
                    images = []
                    for i, img_data in enumerate(result["output"]):
                        # Get image info if available
                        img_info = {}
                        if "seeds" in result and i < len(result["seeds"]):
                            img_info["seed"] = result["seeds"][i]
                        images.append((img_data, img_info))
                    
                    st.session_state.generated_images = images
                    
                    # Also display the raw output format for debugging
                    with st.expander("Debug API Response"):
                        st.json(result)
                else:
                    st.error("Failed to generate images. No output received from API.")
            
            except Exception as e:
                st.error(f"Error generating images: {str(e)}")
    
    # Display results section
    if st.session_state.generated_images:
        st.header("Generated Images")
        st.write(f"**Prompt used:** {prompt}")
        display_images(st.session_state.generated_images)

if __name__ == "__main__":
    main()
