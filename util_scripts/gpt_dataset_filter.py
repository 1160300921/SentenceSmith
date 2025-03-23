from datasets import load_dataset

# 加载数据集
dataset = load_dataset("humarin/chatgpt-paraphrases")

# 获取训练数据
train_data = dataset['train']

# 创建用于存储数据的列表
texts = []
paraphrases_list = []

# 筛选并收集数据
for data in train_data:
    if data['category'] == 'sentence' and data['source'] == 'cnn_news':
        texts.append(data['text'])
        paraphrases_list.append(data['paraphrases'])

# 创建DataFrame并保存
import pandas as pd
df = pd.DataFrame({
    'text': texts,
    'paraphrases': paraphrases_list
})
df.to_csv('input_sentences.csv', index=False)

print(df.head())
# print("筛选完成，结果已写入 input_sentences.txt 文件中。")
