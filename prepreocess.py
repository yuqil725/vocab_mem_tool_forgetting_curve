from datetime import datetime, timedelta
import time
import pandas as pd

def reformat_date(s):
    if s:
        return datetime.strptime(s, '%d-%m-%Y').strftime('%Y-%m-%d %H:%M:%S')
    return s

def set_nxt_rvw_ts(dt):
    if dt and dt==dt:
        new_ts = (datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') + timedelta(days=13)).strftime('%Y-%m-%d %H:%M:%S')
        return new_ts
    return None

def set_nxt_rvw_prd_s(s):
    if s:
        return 3
    return 0

df_path = "gre_vocab.csv"
new_df_path = f"gre_vocab_{datetime.now()}.csv"
df = pd.read_csv(df_path)
new_df = df.copy()
# new_df.lst_rvw_ts = df.lst_rvw_ts.apply(reformat_date)
new_df.nxt_rvw_ts = df.lst_rvw_ts.map(set_nxt_rvw_ts)
new_df.nxt_rvw_prd_idx = df.lst_rvw_ts.map(set_nxt_rvw_prd_s)
new_df.word = new_df.word.str.lower()
new_df.set_index("word", inplace=True)
new_df.to_csv(new_df_path)
