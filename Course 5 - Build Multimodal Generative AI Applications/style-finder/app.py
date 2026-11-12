"""
Main application file for the Style Finder Gradio interface.
"""

import gradio as gr
import pandas as pd
import os
from tempfile import NamedTemporaryFile

# Import local modules
from models.image_processor import ImageProcessor
from models.llm_service import LlamaVisionService
from utils.helpers import get_all_items_for_image, format_alternatives_response, process_response
import config

class StyleFinderApp:
    """
    Main application class that orchestrates the Style Finder workflow.
    """
    
    def __init__(self, dataset_path):
        """
        Initialize the Style Finder application.
        
        Args:
            dataset_path (str): Path to the dataset file
            serp_api_key (str, optional): SerpAPI key for product searches
            
        Raises:
            FileNotFoundError: If the dataset file is not found
            ValueError: If the dataset is empty or invalid
        """
        # Check if dataset file exists and raise FileNotFoundError if not
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
            
        # Load the dataset
        self.dataset = pd.read_pickle(dataset_path)
        
        #Check if dataset is empty and raise ValueError if it is
        if self.dataset.empty:
            raise ValueError("Dataset is empty")
        
        # Initialize image processor component
        self.image_processor = ImageProcessor(config.IMAGE_SIZE, config.NORMALIZATION_MEAN, config.NORMALIZATION_STD)
        
        # Initialize LLM service component
        self.llm_service = LlamaVisionService(
            config.LLAMA_MODEL_ID,
            config.PROJECT_ID,
            config.REGION
        )
        

    def process_image(self, image):
        """
        Process a user-uploaded image and generate a fashion response.
        
        Args:
            image: PIL image uploaded through Gradio
                
        Returns:
            str: Formatted response with fashion analysis
        """
        # Save the image temporarily if it's not already a file path
        if not isinstance(image, str):
            temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
            image_path = temp_file.name
            image.save(image_path)
        else:
            image_path = image
        
        # Encode the image using the image processor
        encoded_image = self.image_processor.encode_image(image_path, is_url=False)
        
        # Check if encoding was successful
        if encoded_image['vector'] is None:
            return "Error: Unable to process the image. Please submit another."
        
        # Find the closest match in the dataset
        closest_row, similarity_score = self.image_processor.find_closest_match(encoded_image['vector'], self.dataset)
        
        # Check if a match was found
        if closest_row is None:
            return "Error: Unable to find a match. PLease try another."
        
        # Log match details
        print(f"Found closest match: {closest_row['Item Name']} with similarity score: {similarity_score:.2f}")
        
        # Get all related items for the matched image
        all_items = get_all_items_for_image(closest_row['Image URL'], self.dataset)
        
        if all_items.empty:
            return "Error: No items found for the matched image."
        
        # Generate fashion response using the LLM service
        fashion_response = self.llm_service.generate_fashion_response(
            encoded_image['base64'],
            closest_row,
            all_items,
            similarity_score,
            threshold=config.SIMILARITY_THRESHOLD
        )
        
        # Clean up temporary files
        if not isinstance(image, str):
            try:
                os.unlink(image_path)
            except:
                pass
        
        return process_response(fashion_response)


def create_gradio_interface(app):
    """
    Create and configure the Gradio interface.
    
    Args:
        app (StyleFinderApp): Instance of the StyleFinderApp
        
    Returns:
        gr.Blocks: Configured Gradio interface
    """
    with gr.Blocks(theme=gr.themes.Soft(), title="Fashion Style Analyzer") as demo:
        # Introduction
        gr.Markdown(
            """
            # Fashion Style Analyzer
            
            Upload an image to analyze fashion elements and get detailed information about the items.
            This application combines computer vision, vector similarity, and large language models 
            to provide detailed fashion analysis.
            """
        )
        
        # Example images section - moved higher up
        gr.Markdown("### Example Images")
        with gr.Row():
            # Display the images directly
            gr.Image(value="examples/test-1.png", label="Example 1", show_label=True, scale=1)
            gr.Image(value="examples/test-2.png", label="Example 2", show_label=True, scale=1)
            gr.Image(value="examples/test-3.png", label="Example 3", show_label=True, scale=1)
        
        # Example image buttons
        with gr.Row():
            example1_btn = gr.Button("Use Example 1")
            example2_btn = gr.Button("Use Example 2")
            example3_btn = gr.Button("Use Example 3")
        
        with gr.Row():
            with gr.Column(scale=1):
                # Image input component
                image_input = gr.Image(
                    type="pil", 
                    label="Upload Fashion Image"
                )
                
                # Submit button
                submit_btn = gr.Button("Analyze Style", variant="primary")
                
                # Status indicator
                status = gr.Markdown("Ready to analyze.")
            
            with gr.Column(scale=2):
                # Output markdown component for displaying analysis results
                output = gr.Markdown(
                    label="Style Analysis Results",
                    height=700
                )
        
        # Event handlers
        # 1. Submit button click with processing indicator
        submit_btn.click(
            fn=lambda: "Analyzing image... This may take a few moments.",
            inputs=None,
            outputs=status
        ).then(
            fn=app.process_image,
            inputs=[image_input],
            outputs=output
        ).then(
            fn=lambda: "Analysis complete!",
            inputs=None,
            outputs=status
        )
        
        # 2. Example image buttons
        example1_btn.click(
            fn=lambda: "examples/test-1.png", 
            inputs=None, 
            outputs=image_input
        ).then(
            fn=lambda: "Example 1 loaded. Click 'Analyze Style' to process.",
            inputs=None,
            outputs=status
        )
        
        example2_btn.click(
            fn=lambda: "examples/test-2.png", 
            inputs=None, 
            outputs=image_input
        ).then(
            fn=lambda: "Example 2 loaded. Click 'Analyze Style' to process.",
            inputs=None,
            outputs=status
        )
        
        example3_btn.click(
            fn=lambda: "examples/test-3.png", 
            inputs=None, 
            outputs=image_input
        ).then(
            fn=lambda: "Example 3 loaded. Click 'Analyze Style' to process.",
            inputs=None,
            outputs=status
        )
        
        # Information about the application
        gr.Markdown(
            """
            ### About This Application
            
            This system analyzes fashion images using:
            
            - **Image Encoding**: Converting fashion images into numerical vectors
            - **Similarity Matching**: Finding visually similar items in a database
            - **Advanced AI**: Generating detailed descriptions of fashion elements
            
            The analyzer identifies garments, fabrics, colors, and styling details from images.
            The database includes information on outfits with brand and pricing details.
            """
        )
    
    return demo


if __name__ == "__main__":
    try:
        # Initialize the app with the dataset
        app = StyleFinderApp("swift-style-embeddings.pkl")
        
        # Create the Gradio interface
        demo = create_gradio_interface(app)
        
        # Launch the Gradio interface
        demo.launch(
            server_name="127.0.0.1",  
            server_port=5001,
            share=True  # Set to False if you don't want to create a public link
        )
    except Exception as e:
        print(f"Error starting the application: {str(e)}") 