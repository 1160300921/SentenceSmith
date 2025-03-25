# graphstring2triples.py

import penman
import sys

def graphstring_to_triples(graph_string):
    # 解析图字符串
    graph = penman.decode(graph_string)
    # 获取三元组
    triples = graph.triples
    return triples

if __name__ == "__main__":
    # 从命令行参数读取 AMR 图字符串
    input_graph_string = sys.argv[1]
    # 获取三元组
    triples = graphstring_to_triples(input_graph_string)
    # 输出三元组
    for triple in triples:
        print(triple)

