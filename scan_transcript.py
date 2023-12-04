import re
import os
import gzip 
import tempfile
import json
import argparse
from better_profanity import profanity


def flatten_transcript(transcript):
    tokens = []
    for t in transcript:
        tokens += t['tokens']
    print (f"Found {len(tokens)} tokens")
    tms = []
    tokens = [ x for x in tokens if not re.match('^\[.*\]$', x['text']) ]
    return tokens

def search_tokens(tokens):
    tms = []
    for i, t in enumerate(tokens):
        txt = t['text']
        #print (txt)
        if profanity.contains_profanity(txt):
            tms.append(t['timestamps'])
        else:
            if i > 0:
                ptxt = tokens[i-1]['text']
                ctext = ptxt + txt
                if profanity.contains_profanity(ctext) and not profanity.contains_profanity(ptxt):
                    nts = {'from': tokens[i-1]['timestamps']['from'], 'to': t['timestamps']['to']}
                    tms.append(nts)
    return tms

def process_json(input_file):
    j = json.load(open(input_file))
    transcript = j['transcription']
    tokens = flatten_transcript(transcript)
    tms = search_tokens(tokens)
    return tms

def load_words():
    custom_words = [ x for x in ["profanity_wordlist.txt", "profanity_wordlist.txt.gz"] if os.path.exists(x) ]
    if len(custom_words) > 0:
        custom_word_path = custom_words[0]
        print (f"Loading custom word list \"{custom_word_path}\"")
        if custom_word_path.lower().endswith('.gz'):
            with tempfile.NamedTemporaryFile(delete=False, suffix="custom_wordlist.txt") as f:
                #print (f"{f.name}")
                with gzip.open(custom_word_path) as gz:
                    f.write(gz.read())
                    f.close()
                
                profanity.load_censor_words_from_file(f.name)
                os.remove(f.name)
        else:
            profanity.load_censor_words_from_file(custom_word_path)


def main():
    parser = argparse.ArgumentParser(description="Process input and output file names.")

    # Add arguments
    parser.add_argument('-i', '--input', default='tempfile.wav.json', help='Input JSON file name')
    parser.add_argument('-o', '--output', help='Output JSON file name')

    # Parse arguments
    args = parser.parse_args()

    # Set input and output file names
    input_file = args.input
    output_file = args.output if args.output is not None else f'parsed_{input_file}'

    load_words()

    # if os.path.exists('custom_words.txt'):
    #     #cwords = [ x.strip() for x in open('custom_words.txt').read().split('\n') if len(x.strip()) > 0]
    #     #profanity.add_censor_words(cwords)
    #     profanity.load_censor_words('custom_words.txt')
    # else:
    #     profanity.load_censor_words()
    
    tms = process_json(input_file)
    otxt = json.dumps(tms, indent=4)
    open(output_file, 'w').write(otxt)
    flat_tms = [ f'{x["from"]}-{x["to"]}' for x in tms ]
    flat_tms = ", ".join(flat_tms)
    print (f"Following timestamps contained profanity: {flat_tms}")
    #print (otxt)

if __name__ == "__main__":
    main()