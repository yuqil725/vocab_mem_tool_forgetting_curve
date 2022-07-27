# vocab_mem_tool_forgetting_curve

This repository used forgetting curve to learn & review new vocabularies

## Get Started

```bash
python main.py
```

"What would you like to do?" This is a the mode switch view. You can use the following command to switch mode:

- **:l**: learning mode. Add new vocab to `.csv`. If there is any vocab needed to be reviewed, it will switch to review mode automatically.
- **:r**: review mode. Review past learned vocab by following forgetting curve. If all vocab are reviewed, it will switch to learning mode.
- **:u**: update mode. Choose a past vocab and update its content

To get back to mode switch view, use `ctr + c`. Notice, `ctr + c` may also lead to program exit. This is a known bug. You could simply restart the program. All changes will be saved before program exit.

---

## Learning Mode

Everytime you finish filling a field, press `return` to start filling the next field.

To specify which field, you need to use the following format:

`<<command>> <<content>>`

The commands are:

| command | column name |
| ------- | ----------- |
| +w      | word        |
| +m      | meaning     |
| +r      | to_remember |
| +e      | example     |
| +s      | synonym     |
| +a      | antonym     |

If no commands are provided, your input will be filled in column following the top-down order in the table.

A word can be saved any time by `:s` command.

## Update Mode

When switching to update mode, you are required to choose an word to update. The update command is identical to the one showing in learning mode.

## Review Mode

Be honest to yourself, choose the time period that you will right forget the word, which is the best point for refreshing memory.

To check the meaning of the word, use `s` command.

| command | column name      |
| ------- | ---------------- |
| sall    | show all info    |
| sw      | show word        |
| sm      | show meaning     |
| sr      | show to_remember |
| se      | show example     |
| ss      | show synonym     |
| sa      | show antonym     |

To show the remaning reviewing words, use `l` command.

To show the finished reviewing words within today, use `f` command. You can also add time attribute. For example, `f 20000` mean "show finished reviewing words in the last 20000 seconds".

# Constant

`VIEW_RANGE`: you may sometimes accumulate too many words to review, you can limit the program to only be view the vocab learned in the last `VIEW_RANGE` time.
