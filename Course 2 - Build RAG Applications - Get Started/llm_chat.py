from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials
from langchain_ibm import WatsonxLLM
import gradio as gr

#model_id = 'mistralai/mistral-small-3-1-24b-instruct-2503' # Specify the Mixtral model
model_id = 'meta-llama/llama-4-maverick-17b-128e-instruct-fp8' # Specify llama model

parameters = {
    GenParams.MAX_NEW_TOKENS: 512,  # Specify the max tokens you want to generate
    GenParams.TEMPERATURE: 0.5, # This randomness or creativity of the model's responses
}

project_id = "skills-network"

# Wrap up the model into WatsonxLLM inference
watsonx_llm = WatsonxLLM(
    model_id=model_id,
    url="https://us-south.ml.cloud.ibm.com",
    project_id=project_id,
    params=parameters,
)

def generate_response(prompt):
    return watsonx_llm.invoke(prompt)

chat_app = gr.Interface(
    fn=generate_response,
    allow_flagging="never",
    inputs=gr.Textbox(label="Input", lines=2, placeholder="Type your question here..."),
    outputs=gr.Textbox(label="Output"),
    title="Watsonx.ai Chatbox",
    description="Ask any question and the chatbot will try to answer"
)

chat_app.launch()