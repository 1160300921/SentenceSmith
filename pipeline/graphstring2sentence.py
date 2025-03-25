# graphstring2sentence.py

import sys
import amrlib

def graph_string_to_sentence(graph_string):
    gtos = amrlib.load_gtos_model()
    sentences = gtos.generate([graph_string])
    # 处理每个句子，移除不正确的 'instance' 字样
    processed_sentences = [s.replace('instance of', '').replace('instance', '').strip() for s in sentences[0]]
    return processed_sentences[0] if processed_sentences else ""

if __name__ == "__main__":
    graph_string = sys.stdin.read().strip()
    sentence = graph_string_to_sentence(graph_string)
    print(sentence)
