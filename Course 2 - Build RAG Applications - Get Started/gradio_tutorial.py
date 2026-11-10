import gradio as gr
'''
def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs="text"
)

demo.launch(server_name="127.0.0.1", server_port= 7860)
'''
'''
from transformers import BlipProcessor, BlipForConditionalGeneration

print("Loading processor...")
processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

print("Loading model...")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

print("Model loaded!")

def generate_caption(image):
    # Now directly using the PIL Image object
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.generate(**inputs)
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption

def caption_image(image):
    """
    Takes a PIL Image input and returns a caption.
    """
    try:
        caption = generate_caption(image)
        return caption
    except Exception as e:
        return f"An error occurred: {str(e)}"

iface = gr.Interface(
    fn=caption_image,
    inputs=gr.Image(type="pil"),
    outputs="text",
    title="Image Captioning with BLIP",
    description="Upload an image to generate a caption."
)

if __name__=="__main__":
    iface.launch(server_name="127.0.0.1", server_port= 7860)
    '''

import torch
import requests
from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights
model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1).eval()

# Download human-readable labels for ImageNet
response = requests.get("https://git.io/JJkYN")
labels = [l.strip() for l in response.text.split("\n") if l.strip()]

# Define image preprocessing (IMPORTANT for ResNet)
transform = transforms.Compose([ transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

def predict(inp):
    # preprocess image
    inp = transform(inp).unsqueeze(0)

    # ensure model runs in inference mode
    with torch.no_grad():
        prediction = torch.nn.functional.softmax(model(inp)[0], dim=0)

    # map predictions to labels
    confidences = {
        labels[i]: float(prediction[i])
        for i in range(len(labels))
    }

    return confidences

gr.Interface(fn=predict,
       inputs=gr.Image(type="pil"),
       outputs=gr.Label(num_top_classes=3)).launch()