import pandas as pd
from input_handler import InputHandler


if __name__ == "__main__":
    df_path = "gre_vocab.csv"
    df = pd.read_csv(df_path)
    ih = InputHandler(df)
    while(True):
        # s = input(ih.next_question() + "\n")
        ih.handle()