from nltk import TweetTokenizer
import re
import phonemizer
import json
import sys

if len(sys.argv) != 3:
    print("Usage: python phonemize.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

t_tokenizer = TweetTokenizer()
def preprocess(text):
    
    text = re.sub(re.compile(r'[„""""«»"]'),'"',text)
    text = re.sub(re.compile('[-—−‒‒–]'),'—',text)
    text = re.sub(re.compile(r'[\(\)\*\/\[\]]'),'',text)

    # Remove multiple spaces, separates punctuation from words
    tokenized = " ".join(t_tokenizer.tokenize(text))

    return tokenized

global_phonemizer = phonemizer.backend.EspeakBackend(
    language='pl', 
    preserve_punctuation=True, 
    tie=True, 
    with_stress=True,
    words_mismatch='ignore',
    language_switch='remove-flags',
    punctuation_marks=''.join(list(set([x for x in ';:, .!?¡¿—…"«»""(){}[]-–„"'])))
)

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Process each example and save in LJSpeech format
ljspeech_lines = []
for entry in data:
    text = entry['text']
    hash_id = entry['hash']
    
    # Preprocess the text
    preprocessed = preprocess(text)
    
    # Phonemize the preprocessed text (phonemizer expects a list)
    phonemized = global_phonemizer.phonemize([preprocessed])[0]
    
    # Create LJSpeech formatted line: wav_path|text|speaker
    wav_path = f"{hash_id}.wav"
    ljspeech_line = f"{wav_path}|{phonemized}|0"
    ljspeech_lines.append(ljspeech_line)

# Save to dataset.txt
with open(output_file, 'w', encoding='utf-8') as f:
    for line in ljspeech_lines:
        f.write(line + '\n')