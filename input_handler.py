try:
    import readline
except:
    pass #readline not available
import pandas as pd
import re
import os
from tabulate import tabulate

from constant import DAY, HOUR, NEXT_RECALL, NEXT_RECALL_STR, VIEW_RANGE
from stdout import bcolors, print_err, print_ok, print_warning
from util import cmp_date, datetime_after_now, datetime_dff, datetime_now

clear = lambda: os.system('clear')
new_df = False

class InputHandler:
    def __init__(self, df: pd.DataFrame):
        self.state = ""
        self.cur_input = ""
        self.cur_word = ""
        self.df = df
        self._update_nxt_rvw_ts_diff()
        self.df = self.df.set_index("word")
        self._save_df()
        self.cur_q_idx = 0
        self.state_cand = {"review", "learn", "update", "delete"}
        self.state_map = {"r": "review", "l": "learn", "u": "update", "d": "delete"}
        self.switch_to_update = False
        self.switch_to_learn = False
        self.col_map = {
            "m": ["meaning"],
            "e": ["example"],
            "r": ["to_remember"],
            "s": ["synonym"],
            "a": ["antonym"],
            "n": ["nxt_rvw_prd_idx"],
            "sall": ["meaning", "to_remember", "example", "synonym", "antonym", "rvw_his_ts"]
        }
    
    def print_with_mode(self, s):
        print(f"[{self.state}]: ".upper() + s)

    def try_switch_state(self):
        cmd = re.findall(r"\w*", self.cur_input[1:])[0]
        if cmd in self.state_map:
            cmd = self.state_map[cmd]
        if self.cur_input.startswith(":") and cmd in self.state_cand:
            if cmd == "update":
                self.switch_to_update = self.state != ""
            self.state=cmd
            return True
        return False
    
    def next_question(self):
        return self.questions[self.state][self.cur_q_idx]

    def _update_nxt_rvw_ts_diff(self):
        self.df["next_rvw_ts_diff"] = self.df["nxt_rvw_ts"].map(lambda x: datetime_dff(datetime_now(), x))
        self.df["next_rvw_ts_diff_abs"] = self.df["nxt_rvw_ts"].map(lambda x: abs(datetime_dff(datetime_now(), x)))
        self.df = self.df.sort_values(["next_rvw_ts_diff_abs"])

    def _print_nxt_rvw_time(self, next_recall):
        self.print_with_mode(f"3: next recall after {bcolors.OKGREEN}{NEXT_RECALL_STR[int(min(max(next_recall.nxt_rvw_prd_idx + 1, 3), len(NEXT_RECALL) - 1))]}{bcolors.ENDC}")
        self.print_with_mode(f"2: next recall after {bcolors.OKGREEN}{NEXT_RECALL_STR[int(min(next_recall.nxt_rvw_prd_idx + 1, len(NEXT_RECALL) - 1))]}{bcolors.ENDC}")
        self.print_with_mode(f"1: next recall after {bcolors.OKGREEN}{NEXT_RECALL_STR[next_recall.nxt_rvw_prd_idx]}{bcolors.ENDC}")
        self.print_with_mode(f"0: next recall after {bcolors.OKGREEN}{NEXT_RECALL_STR[0]}{bcolors.ENDC}")

    def _update_recall_item(self, next_recall: pd.Series):
        if self.cur_input == "3":
            next_recall.nxt_rvw_prd_idx = int(min(max(next_recall.nxt_rvw_prd_idx + 1, 3), len(NEXT_RECALL) - 1))
        elif self.cur_input == "2":
            next_recall.nxt_rvw_prd_idx = int(min(next_recall.nxt_rvw_prd_idx + 1, len(NEXT_RECALL) - 1))
        elif self.cur_input == "1":
            pass
        elif self.cur_input == "0":
            next_recall.nxt_rvw_prd_idx = 0
        else:
            if not self.try_switch_state():
                self.print_with_mode(f"Unknown command: {self.cur_input}")
        next_recall.lst_rvw_ts = datetime_now()
        next_recall.nxt_rvw_ts = datetime_after_now(NEXT_RECALL[next_recall.nxt_rvw_prd_idx])
        if "rvw_his_ts" in next_recall and type(next_recall["rvw_his_ts"]) == str:
            next_recall["rvw_his_ts"] += ", " + next_recall.lst_rvw_ts
        else:
            next_recall["rvw_his_ts"] = next_recall.lst_rvw_ts
        self.print_with_mode(f"Your next recall time will be after {bcolors.OKGREEN}{NEXT_RECALL_STR[next_recall.nxt_rvw_prd_idx]}{bcolors.ENDC}")
        return next_recall

    def _show_vocab_by_command(self, cmd, next_recall: pd.Series):
        # "s": show only word
        # "sr": show word, to_remember
        # "sall": show everything
        cmd = re.findall(r"\w*", cmd)[0]
        tmp_df = next_recall.to_frame().fillna("")
        col = []
        if cmd == "sall":
            col = self.col_map[cmd]
            print_ok(tabulate(tmp_df.loc[col], headers='keys'))
            return
        elif cmd == "s" or cmd == "":
            print_ok(str(next_recall.name))
            return
        for c in cmd:
            if c == "s":
                continue
            if c in self.col_map:
                col += self.col_map[c]
        print_ok(tabulate(tmp_df.loc[col], headers='keys'))
        return


    def _add_new_row(self, row: pd.Series):
        self.df = pd.concat([row.to_frame().T, self.df])
        self._update_nxt_rvw_ts_diff()

    def _save_df(self, new=new_df):
        new_df_path = "gre_vocab.csv"
        if new:
            new_df_path = f"gre_vocab_{datetime_now()}.csv"
        self.df.to_csv(new_df_path, index_label="word")

    def _review_mode(self):
        while(True):
            clear()
            try:
                review_df = self.df[self.df.next_rvw_ts_diff >= 0]
                bool_view = review_df.lst_rvw_ts.map(lambda x: cmp_date(x, datetime_after_now(-VIEW_RANGE)))
                review_df = review_df[bool_view]
                if not review_df.shape[0]:
                    print_warning("Running out of reviewable vocabs, switching to LEARN mode....")
                    self.state = "learn"
                    self.switch_to_learn = True
                    self.cur_input = ""
                    break
                next_recall: pd.Series = review_df.iloc[0]
                self.cur_word = next_recall.name
                self._show_vocab_by_command(":s", next_recall)
                self.cur_input = ""
                os.system(f"say '{next_recall.name}' &") 
                while self.cur_input not in {"0", "1", "2", "3"}:
                    self._print_nxt_rvw_time(next_recall)
                    self.print_with_mode("How well do you remember the word? (0 to 3)")
                    self.cur_input = input()
                    if self.cur_input in {"0", "1", "2", "3"}:
                        break
                    if self.cur_input and self.cur_input[0] == "s":
                        self._show_vocab_by_command(self.cur_input, next_recall)
                    elif self.cur_input and self.cur_input[0] == "l" or self.cur_input=="left":
                        # remain
                        # review_left = self.df[self.df.nxt_rvw_ts <= datetime_now()]
                        print(f"{bcolors.OKGREEN}{review_df['nxt_rvw_ts']}{bcolors.ENDC}")
                    elif self.cur_input and self.cur_input[0] == "f" or self.cur_input=="finished":
                        # remain
                        try:
                            last_secs = -int(self.cur_input.split()[1]) * HOUR
                        except:
                            last_secs = -DAY
                        review_finished = self.df[self.df.lst_rvw_ts.map(lambda x: cmp_date(x, datetime_after_now(last_secs)))]
                        print(f"{bcolors.OKGREEN}{review_finished['lst_rvw_ts']}{bcolors.ENDC}")
                    elif self.try_switch_state():
                        return True
                    else:
                        print_warning("Invalid input")
                next_recall = self._update_recall_item(next_recall.copy())
                self.df.drop(next_recall.name, inplace=True)
                self._add_new_row(next_recall)
                self._save_df()
            except KeyboardInterrupt:
                self.state = ""
                return False

    def _learn_mode(self):
        self.switch_to_learn = False
        self.print_with_mode(f"What's the new word? (pre: {self.df.sort_values(['lst_rvw_ts']).index[-1]})")
        self.cur_input = input()
        if self.cur_input in self.df.index:
            print_warning(f"{self.cur_input} already exists")
            self.state = "update"
            self.switch_to_update = True
            self.cur_word = self.cur_input
            return
        new_word = {}
        word = self.cur_input
        self.cur_word = word
        while(True):
            try:
                os.system(f"say '{word}' &") 
                self.cur_input = input(f"What attribute would you like to add to {bcolors.OKGREEN}{word}{bcolors.ENDC}?\n")
                clear()
                if self.cur_input == ":s":
                    break
                if self.cur_input[0] not in {"+", "-"}:
                    for c in self.col_map["sall"]:
                        if c not in new_word:
                            column = [c]
                            break
                    text = self.cur_input
                elif self.cur_input[0] == "-":
                    column = self.col_map[self.cur_input[1]]
                    del new_word[column[0]]
                    continue
                else:
                    if self.cur_input[1] not in self.col_map:
                        print_warning("Invalid attribute. Please try again")
                    else:
                        column = self.col_map[self.cur_input[1]]
                    text = " ".join(self.cur_input.split()[1:])
                new_word[column[0]] = text
                new_word_ps = pd.Series(new_word, name=word)
                print_ok(tabulate(new_word_ps.to_frame(), headers='keys'))
            except KeyboardInterrupt:
                self.state = ""
                return

        new_word["nxt_rvw_prd_idx"] = 1
        new_word["lst_rvw_ts"] = datetime_now()
        new_word["nxt_rvw_ts"] = datetime_after_now(NEXT_RECALL[0])
        new_word["rvw_his_ts"] = new_word["lst_rvw_ts"]
        new_word_ps = pd.Series(new_word, name=word)
        self._add_new_row(new_word_ps)
        self._save_df()

    def _update_mode(self):
        self.print_with_mode("Which word would you like to update?")
        if not self.switch_to_update:
            self.cur_input = self.cur_word = input()
        word = self.cur_word
        try:
            row = self.df.loc[word]
            self.df.drop(word, inplace=True)
        except:
            print_warning(f"{word} does not exist, please try again")
            return
        print_ok(tabulate(row.to_frame(), headers='keys'))
        new_word = row.to_dict()
        while(True):
            try:
                self.cur_input = input(f"How would you like to update {bcolors.OKGREEN}{word}{bcolors.ENDC}?\n")
                clear()
                if self.cur_input == ":s":
                    self.state = "review"
                    break
                if self.cur_input[1] not in self.col_map:
                    print_warning("Invalid attribute. Please try again")
                    continue
                column = self.col_map[self.cur_input[1]]
                if len(self.cur_input.split()) == 1:
                    print_warning("Invalid input. Please try again")
                    continue
                text = " ".join(self.cur_input.split()[1:])
                new_word[column[0]] = text
                if column == ["nxt_rvw_prd_idx"]:
                    new_word[column[0]] = int(text)
                    new_word["nxt_rvw_ts"] = datetime_after_now(NEXT_RECALL[int(text)])
                new_word_ps = pd.Series(new_word, name=word)
                print_ok(tabulate(new_word_ps.to_frame(), headers='keys'))
            except KeyboardInterrupt:
                self.state = ""
                return
        new_word_ps = pd.Series(new_word, name=word)
        self._add_new_row(new_word_ps)
        self._save_df()

    def _delete_mode(self):
        while(True):
            try:
                self.print_with_mode("Which word would you like to delete?")
                self.cur_input = input()
                self.cur_word = word = self.cur_input
                if word not in self.df.index:
                    print_warning(f"{word} does not exist, please try again")
                    continue
                row = self.df.loc[word]    
                print_err(tabulate(row.to_frame(), headers='keys'))
                self.cur_input = input("Are you sure to delete? (y/n)\n")
                if self.cur_input == "y":
                    self.df.drop(word, inplace=True)
            except KeyboardInterrupt:
                self.state = ""
                return
    
    
    def handle(self):
        clear()
        if self.state == "":
            self.cur_input = input("What would you like to do?\n")
            self.try_switch_state()
        elif self.state.startswith("r") or self.state.startswith("l"):
            # review mode
            if not self.switch_to_learn:
                if self._review_mode():
                    return
            return self._learn_mode()
        elif self.state.startswith("u"):
            return self._update_mode()
        elif self.state.startswith("d"):
            return self._delete_mode()
        
        

    