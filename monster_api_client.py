import requests
import json
import logging
from monsterapi import client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# List of valid models for Monster API text-to-image generation
# Only including sdxl-base which is confirmed to work reliably
VALID_MODELS = [
    "sdxl-base"
]

def get_available_models(api_key):
    """
    Get a list of available models from the Monster API
    
    Args:
        api_key (str): Monster API key
        
    Returns:
        list: List of available model names
    """
    try:
        # Initialize the Monster API client
        monster_client = client(api_key)
        
        # Try to get available models directly from the API if possible
        # Note: This depends on the API supporting this feature
        models = monster_client.available_models()
        if models and isinstance(models, list) and len(models) > 0:
            logger.info(f"Retrieved {len(models)} models from API")
            return models
    except Exception as e:
        logger.warning(f"Could not retrieve models from API: {str(e)}")
    
    # Fallback to known working models
    logger.info(f"Using predefined list of {len(VALID_MODELS)} models")
    return VALID_MODELS

def generate_image(api_key, model_name, input_data):
    """
    Generate images using Monster API's stable diffusion models
    
    Args:
        api_key (str): Monster API key
        model_name (str): Name of the model to use (e.g., 'sdxl-base')
        input_data (dict): Parameters for image generation
        
    Returns:
        dict: The API response containing generated images and metadata
        
    Raises:
        Exception: If API request fails
    """
    try:
        # Initialize the Monster API client
        monster_client = client(api_key)
        
        # Validate model name against known working models
        if model_name not in VALID_MODELS:
            logger.warning(f"Model '{model_name}' not in known working models list, but attempting anyway")
        
        # Log generation attempt
        logger.info(f"Generating image with model: {model_name}")
        logger.info(f"Prompt: {input_data.get('prompt', '')}")
        
        # Make the API request
        result = monster_client.generate(model_name, input_data)
        
        # Debug log the raw output structure
        logger.info(f"Response keys: {result.keys() if isinstance(result, dict) else 'Not a dictionary'}")
        if isinstance(result, dict) and 'output' in result:
            logger.info(f"Output type: {type(result['output'])}")
            logger.info(f"Output length: {len(result['output'])}")
            if len(result['output']) > 0:
                logger.info(f"First output item type: {type(result['output'][0])}")
                # Log a small part of the first item to understand format
                if isinstance(result['output'][0], str):
                    snippet = result['output'][0][:50] + "..." if len(result['output'][0]) > 50 else result['output'][0]
                    logger.info(f"First output snippet: {snippet}")
        
        # Check if the result contains expected data
        if not result or 'output' not in result:
            logger.error(f"API returned unexpected response: {result}")
            raise Exception("Invalid response from Monster API")
        
        # Log success
        logger.info(f"Successfully generated {len(result['output'])} images")
        return result
        
    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        raise Exception(f"Failed to generate images: {str(e)}")

def check_api_status(api_key):
    """
    Check if the Monster API is operational
    
    Args:
        api_key (str): Monster API key
        
    Returns:
        bool: True if API is operational, False otherwise
    """
    try:
        # Initialize the client
        monster_client = client(api_key)
        
        # Make a minimal request to check status
        # This depends on the API structure, might need adjustment
        status = monster_client.status()
        return True
    except Exception as e:
        logger.error(f"API status check failed: {str(e)}")
        return False
