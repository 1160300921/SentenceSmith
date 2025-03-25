# sentence2graphstring.py

import amrlib
import spacy
import sys

def setup_nlp_pipeline():
    # 设置 Spacy 与 amrlib 的集成
    amrlib.setup_spacy_extension()
    # 加载 Spacy 英文模型
    nlp = spacy.load('en_core_web_sm')
    return nlp

def sentences_to_graphstrings(text):
    # 初始化 NLP 处理管线
    nlp = setup_nlp_pipeline()
    # 处理文本，生成文档对象
    doc = nlp(text)
    # 使用 amrlib 扩展生成 AMR 图
    graphs = doc._.to_amr()
    return graphs

if __name__ == "__main__":
    input_text = sys.argv[1]
    amr_graphs = sentences_to_graphstrings(input_text)
    for graph in amr_graphs:
        print(graph)

