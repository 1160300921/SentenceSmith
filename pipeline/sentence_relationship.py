import sys
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def main(sentence1, sentence2):
    # 加载tokenizer和模型
    tokenizer = AutoTokenizer.from_pretrained("juliussteen/DeBERTa-v3-FaithAug")
    model = AutoModelForSequenceClassification.from_pretrained("juliussteen/DeBERTa-v3-FaithAug")

    # 使用tokenizer处理输入文本
    inputs = tokenizer(sentence1, sentence2, return_tensors="pt")

    # 使用模型进行预测
    with torch.no_grad():
        outputs = model(**inputs)

    # 获取预测结果的逻辑回归分数
    logits = outputs.logits

    # 计算softmax获取概率
    probabilities = torch.softmax(logits, dim=-1)

    # 获取最高概率的索引和值
    max_prob, max_idx = torch.max(probabilities, dim=1)

    # 将概率转换为百分比格式
    max_prob_percentage = max_prob.item() * 100

    # 类别映射
    id2label = model.config.id2label

    # 获取对应的类别名称
    predicted_category = id2label[max_idx.item()]

    # 打印结果
    print(f"Predicted Relationship: {predicted_category} with {max_prob_percentage:.2f}% confidence.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sentence_relationship.py \"sentence1\" \"sentence2\"")
    else:
        main(sys.argv[1], sys.argv[2])
