import sys
import re

if len(sys.argv) != 3:
    print("Usage: python phonemize.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

def preprocess(text):
    
    text = re.sub(re.compile(r'[„""""«»"]'),'"',text)
    text = re.sub(re.compile('[-—−‒‒–]'),'—',text)
    text = re.sub(re.compile(r'[\(\)\*\/\[\]]'),'',text)

    return text

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for line in lines:
            cleaned_line = preprocess(line.strip())
            out_f.write(cleaned_line + '\n')
