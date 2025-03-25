#!/bin/bash

# 
# INPUT_FILE="chatgpt_inputs.txt"
# OUTPUT_FILE="output_sentences_all.csv"
# INTERMEDIATE_DIR="intermediate_results_all"
INPUT_FILE="$1"
OUTPUT_FILE="$2"
INTERMEDIATE_DIR="$3"

mkdir -p "$INTERMEDIATE_DIR"

echo "Original Sentence,Modified Sentence,Modification Type,semantic_relationship" > "$OUTPUT_FILE"

# read every sentence from the input file
line_number=0
while IFS= read -r sentence; do
  line_number=$((line_number + 1))
  sub_dir="$INTERMEDIATE_DIR/sentence_$line_number"
  mkdir -p "$sub_dir"

  # remove commas from the sentence to avoid CSV format issues
  original_sentence=$(echo "$sentence" | tr -d ',')

  echo "Processing sentence: $original_sentence"

  # 1. convert sentence to AMR graph string
  amr_file="$sub_dir/amr.txt"
  python sentence2graphstring.py "$original_sentence" > "$amr_file"
  echo "AMR graph string conversion done."

  # 2. convert AMR graph string to triples
  triples_file="$sub_dir/triples.txt"
  python graphstring2triples.py "$(cat $amr_file)" > "$triples_file"
  echo "Conversion to triples done."

  # define the modifications to be made
  modifications=("RD" "hypernym" "polarity_negation" "RS" "antonym")

  # 3. operate on the triples and generate sentences
  for modification in "${modifications[@]}"; do
    modified_triples_file="$sub_dir/modified_triples_$modification.txt"
    modified_amr_file="$sub_dir/modified_amr_$modification.txt"
    output_sentence_file="$sub_dir/output_sentence_$modification.txt"

    # 3.1 modify the triples
    python modify_triples.py "$modification" < "$triples_file" > "$modified_triples_file"
    echo "Modification $modification done."

    # 3.2 turn the modified triples into an AMR graph string
    python triples2graphstring.py < "$modified_triples_file" > "$modified_amr_file"
    echo "Conversion to modified AMR graph string done."

    # 3.3 turn the modified AMR graph string into a sentence
    python graphstring2sentence.py < "$modified_amr_file" > "$output_sentence_file"
    echo "Conversion to sentence done."

    # read the modified sentence
    modified_sentence=$(cat "$output_sentence_file")

    # 
    modified_sentence=$(echo "$modified_sentence" | tr -d ',')

    semantic_relationship=$(python sentence_relationship.py "$sentence" "$modified_sentence")

    # write the results to the output file
    echo "\"$sentence\",\"$modified_sentence\",\"$modification\",\"$semantic_relationship\"" >> $OUTPUT_FILE

  done

done < "$INPUT_FILE"

echo "Processing complete. Results saved to $OUTPUT_FILE and intermediate results saved to $INTERMEDIATE_DIR."
