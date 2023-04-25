from transformers import RobertaTokenizer, AutoModelForSequenceClassification
import torch
import os

tokenizer = RobertaTokenizer.from_pretrained(os.path.join(os.getcwd(), "models/checkpoint-428"))
text_model = AutoModelForSequenceClassification.from_pretrained(
    os.path.join(os.getcwd(), "models/checkpoint-428"))
text_model.eval()
# vision_model = Data2VecVisionModel.from_pretrained("facebook/data2vec-vision-base")
# audio_model = Data2VecAudioModel.from_pretrained("facebook/data2vec-audio-base")


def text2vec(text):
    inputs = tokenizer(text, return_tensors="pt")
    # inputs = {k: v.to('cuda') for k, v in inputs.items()}
    outputs = text_model(**inputs, output_hidden_states=True)
    return outputs['hidden_states'][-1][0, 0, :].detach().cpu().numpy()
