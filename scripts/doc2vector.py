from transformers import RobertaTokenizer, Data2VecTextModel, Data2VecVisionModel, Data2VecAudioModel
import torch

tokenizer = RobertaTokenizer.from_pretrained("facebook/data2vec-text-base")
text_model = Data2VecTextModel.from_pretrained("facebook/data2vec-text-base")
# vision_model = Data2VecVisionModel.from_pretrained("facebook/data2vec-vision-base")
# audio_model = Data2VecAudioModel.from_pretrained("facebook/data2vec-audio-base")

def text2vec(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = text_model(**inputs)
    return outputs[0].detach().numpy()