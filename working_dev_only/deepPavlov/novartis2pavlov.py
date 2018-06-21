import json
import os
import random
import re
import argparse
import sqlite3
from collections import OrderedDict
from novartis_config import questions, optional_info, additional_qs, req_sub_dict
from synthetic_pharma_data import get_settings
from utils import sub_reqs, get_entities

download_path = '../deepPavlov/DeepPavlov/download/pharma'

tag_dict = {1: 'what_question', 2: 'should_question', 3: 'usage_question',
            4: 'dose_question', 5: 'side_effect_question', 6: 'store_question', 7: 'ingredient_question'}

question_tag_dict = OrderedDict(tag_dict)
database = 'NovartisQA'

# connect to database
conn = sqlite3.connect(database + '.sqlite')
cur = conn.cursor()

# get list of id for questions from table
cur.execute('SELECT id FROM Questions')
question_ids = cur.fetchall()

openings = ['hello', 'hi', 'good morning', 'hi there', 'good evening', 'good afternoon']
endings = ['thank you', 'thanks', 'ok thanks']


def gen_opening(i, greeting):
    user = {'index': i, 'text': greeting, 'goals': {'greeting': greeting}, 'db_result': None, 'dialog_acts': []}
    bot = {"index": i, "text": "hello, what can I help you with today?",
           "dialog_acts": [{"act": "welcomemsg", "slot": []}]}
    return user, bot


def gen_ending(i, bye):
    user = {'index': i, 'text': bye, 'goals': {'bye': bye}, 'db_result': None, 'dialog_acts': []}
    bot = {"index": i, "text": 'no problem', "dialog_acts": [{"act": 'bye', "slot": []}]}
    return user, bot


def select_question(question_id, id2tag):
    cur.execute('SELECT * FROM Questions WHERE id = ?', (question_id,))
    question_data = cur.fetchall()[0]
    tag = id2tag[question_id]
    question_formats = [q for q in list(question_data[1:5]) if q]
    # sql query
    query = question_data[5]
    # answer
    answer = question_data[6]
    # required slots
    required_fields = question_data[7].split(',')
    question_text = question_formats[random.randint(0, len(question_formats) - 1)] + '?'
    return question_text, tag, query, answer, required_fields


def gen_question(i, question_text, tag, slots):
    goal = {"question": tag}
    dialog_acts = []
    dialog_acts["act"] = "question"
    dialog_acts["slots"] = slots
    return {"index": i, "text": question_text, "goals": goal, "db_result": None, "dialog_acts": dialog_acts}


class GenDialogue(object):
    """
    generate dialogues for a question, given question_id
    """

    def __init__(self, context_details, question_id, id2tag):
        self.context = context_details
        self.question_text, self.tag, self.query, self.answer, self.required_fields = select_question(question_id,
                                                                                                      id2tag)
        self.curr_slots = {}
        # randomly add additional information for certain questions
        for opt, versions in optional_info.items():
            if opt in self.required_fields and random.randint(0, 1):
                version = random.choice(versions)
                self.question_text = self.question_text[:-1] + ' ' + version + '?'

    def update(self, field):
        if field not in self.required_fields:
            self.curr_slots.pop(field, None)
            self.required_fields.append(field)
        self.context[field] = get_settings()[field]

    def sub_reqs(self, text, req_sub_dict, act=None):
        # for user's question, inform, update
        context_details = self.context
        dialog_acts = {'slots': []}
        goals = {}
        for requirement in req_sub_dict.keys():
            if requirement in text:
                exec(req_sub_dict[requirement][0], locals())
                exec(req_sub_dict[requirement][1], locals())
                value = locals()['sub_data']
                text = re.sub(requirement, value, text)
                self.curr_slots[requirement] = value
                self.required_fields.remove(requirement)
                dialog_acts['slots'].append([requirement, value])
        if act:
            dialog_acts['act'] = act
            if act == 'question':
                goals['question'] = self.tag
            else:
                goals['act'] = act
        return text, goals, [dialog_acts]

    def answer_question(self):
        # bot answer the question
        assert not self.required_fields
        query = sub_reqs(cur, self.query, req_sub_dict, self.context)
        cur.execute(query)
        try:
            exec(self.answer, globals())
            answer_text = globals()['answer_text']
            act = 'information_retrieval+' + self.tag
        except:
            answer_text = 'sorry, there is no information for that.'
            act = 'no_information'

        dialog_acts = {'act': act}
        return answer_text, [dialog_acts]

    def request_information(self, requirement, additional_qs):
        assert requirement in self.required_fields
        text = additional_qs[requirement]
        for field, value in self.context.items():
            if field in text:
                text = re.sub(field, value, text)
        dialog_acts = {'act': f'request_information+{field}'}
        return text, [dialog_acts]


# generate synthetic dialogue data
def gen_data(num_dialogues):
    _dialogues = []
    for d in range(num_dialogues):
        curr_dialogue = []
        curr_idx = 0

        # maybe say hello
        if random.randint(0, 1) == 1:
            user_line, bot_line = gen_opening(curr_idx, random.choice(openings))
            curr_dialogue.append(user_line)
            curr_dialogue.append(bot_line)
            curr_idx += 1

        # select a question and format
        question_id = random.randint(1, len(question_ids))

        # generate required fields from available options
        context_details = get_settings()
        dialogue_context = GenDialogue(context_details, question_id, question_tag_dict)
        required_fields = dialogue_context.required_fields[:]

        # ask the question
        text, goals, dialog_acts = dialogue_context.sub_reqs(dialogue_context.question_text, req_sub_dict,
                                                             act='question')
        user_line = {'index': curr_idx, 'text': text, 'goals': goals, "dialog_acts": dialog_acts}
        curr_dialogue.append(user_line)

        for field in dialogue_context.required_fields[:]:
            text, dialog_acts = dialogue_context.request_information(field, additional_qs)
            bot_line = {'index': curr_idx, 'text': text, 'dialog_acts': dialog_acts}
            curr_dialogue.append(bot_line)
            curr_idx += 1
            text, goals, dialog_acts = dialogue_context.sub_reqs(field, req_sub_dict, 'inform')
            user_line = {'index': curr_idx, 'text': text, 'goals': goals, "dialog_acts": dialog_acts}
            curr_dialogue.append(user_line)

        text, dialog_acts = dialogue_context.answer_question()
        bot_line = {'index': curr_idx, 'text': text, 'dialog_acts': dialog_acts}
        curr_dialogue.append(bot_line)
        curr_idx += 1

        # update information
        num_updates = random.randint(0, min(2, len(required_fields)))
        requirements = random.sample(required_fields, num_updates)
        for requirement in requirements:
            dialogue_context.update(requirement)
            text, goals, dialog_acts = dialogue_context.sub_reqs(requirement, req_sub_dict, 'update')
            user_line = {'index': curr_idx, 'text': 'actually i meant ' + text, 'goals': goals,
                         'dialog_acts': dialog_acts}
            curr_dialogue.append(user_line)
            bot_line = {'index': curr_idx, 'text': 'ok, is there anything else to update?',
                        'dialog_acts': [{'act': 'check_update'}]}
            curr_dialogue.append(bot_line)
            curr_idx += 1
        if num_updates > 0:
            user_line = {'index': curr_idx, 'text': 'no', 'goals': {}, 'dialog_acts': []}
            curr_dialogue.append(user_line)
            text, dialog_acts = dialogue_context.answer_question()
            bot_line = {'index': curr_idx, 'text': text, 'dialog_acts': dialog_acts}
            curr_dialogue.append(bot_line)
            curr_idx += 1

        # maybe say thank you
        if random.randint(0, 1) == 1:
            user_line, bot_line = gen_ending(curr_idx, random.choice(endings))
            curr_dialogue.append(user_line)
            curr_dialogue.append(bot_line)
            curr_idx += 1

        _dialogues.append(curr_dialogue)
    return _dialogues


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate data for DeepPavlov')
    parser.add_argument('num_samples', type=int, nargs=3, help='numbers of samples for train, validate, test')
    args = parser.parse_args()
    exts = ['trn', 'tst', 'val']
    nums = args.num_samples
    for ext, num in zip(exts, nums):
        file_name = 'pharma_' + ext + '.jsonlist'
        path = os.path.join(download_path, file_name)
        print(path)
        dialogues = gen_data(num)
        with open(path, 'w') as f:
            for dialogue in dialogues:
                for line in dialogue:
                    json.dump(line, f)
                    f.write('\n')
                f.write("\n")
