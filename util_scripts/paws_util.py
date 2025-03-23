from datasets import load_dataset
import pandas as pd
import os

splits = {'train': 'en/train-00000-of-00001.parquet', 'test': 'en/test-00000-of-00001.parquet', 'validation': 'en/val-00000-of-00001.parquet'}
df = pd.read_parquet("hf://datasets/google-research-datasets/paws-x/" + splits["test"])
# print(df[:5])

save_dir = './paws_x_csvs'
os.makedirs(save_dir, exist_ok=True)

# 保存第一个 CSV
sentences_csv_path = os.path.join(save_dir, 'paws_x_en_test_sentences.csv')
df[['sentence1', 'sentence2']].to_csv(sentences_csv_path, index=False, encoding='utf-8')
print(f"第一个 CSV 文件 '{sentences_csv_path}' 已成功创建。")

# 保存第二个 CSV
sentence1_csv_path = os.path.join(save_dir, 'paws_x_en_test_sentence1.csv')
df[['sentence1']].to_csv(sentence1_csv_path, index=False, encoding='utf-8')
print(f"第二个 CSV 文件 '{sentence1_csv_path}' 已成功创建。")
