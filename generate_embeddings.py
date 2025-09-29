from platform import win32_edition
import yaml
import librosa
import torch
import torchaudio
from models import load_ASR_models, load_F0_models, build_model
from utils import recursive_munch
import re

def init(config_path):
    config = yaml.safe_load(open(config_path))
    
    device = 'cpu'
    
    
    ASR_config = config.get('ASR_config', False)
    ASR_path = config.get('ASR_path', False)
    text_aligner = load_ASR_models(ASR_path, ASR_config)
    
    # load pretrained F0 model
    F0_path = config.get('F0_path', False)
    pitch_extractor = load_F0_models(F0_path)
    
    # load BERT model
    from Utils.PLBERT.util import load_plbert
    BERT_path = config.get('PLBERT_dir', False)
    plbert = load_plbert(BERT_path)
    
    model_params = recursive_munch(config['model_params'])
    model = build_model(model_params, text_aligner, pitch_extractor, plbert)
    _ = [model[key].eval() for key in model]
    _ = [model[key].to(device) for key in model]
    return model

to_mel = torchaudio.transforms.MelSpectrogram(
    n_mels=80, n_fft=2048, win_length=1200, hop_length=300)

def preprocess(wave):
    mean, std = -4, 4
    wave_tensor = torch.from_numpy(wave).float()
    mel_tensor = to_mel(wave_tensor)
    mel_tensor = (torch.log(1e-5 + mel_tensor.unsqueeze(0)) - mean) / std
    return mel_tensor

device = 'cpu'

def compute_style(model, path):
    wave, sr = librosa.load(path, sr=24000)
    audio, index = librosa.effects.trim(wave, top_db=30)
    if sr != 24000:
        audio = librosa.resample(audio, sr, 24000)
    mel_tensor = preprocess(audio).to(device)

    with torch.no_grad():
        ref_s = model.style_encoder(mel_tensor.unsqueeze(1))
        ref_p = model.predictor_encoder(mel_tensor.unsqueeze(1))

    return torch.cat([ref_s, ref_p], dim=1)

def text_len(text):
    text = re.sub(r'[^a-ząęćłóśźżń ]','',text.lower())
    chars = [x for x in text]
   
    return {
        'words':len(text.split(' ')),
        'chars':len(chars)
    }

if __name__ == "__main__":
    import sys
    import json

    config_path = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    model = init(config_path)
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = []
    for entry in data:
        text = entry['text']
        hash = entry['hash']
        style = compute_style(model, f'.data/{hash}.wav')
        wav_path = f".data/{hash}.wav"
        line = {
            "text": text,
            "tensor": wav_path,
            "len": text_len(text),
        }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(lines, f, ensure_ascii=False, indent=4)
