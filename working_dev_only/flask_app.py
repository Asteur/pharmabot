import torch
from utils import save_pickle, load_pickle, preload, load_embd_weights, load_data, to_var, update_context, save_embeds
from train import *

from flask import Flask, render_template, request
app = Flask(__name__)

train_data = load_data(fpath_train, entities, w2i, action_dict)
train(model, train_data, optimizer, w2i, action_dict)
torch.save(model.state_dict(), save_path)
#
model = HybridCodeNetwork(-1, len(w2i), args.embd_size, args.hidden_size, len(action_dict), len(entities.keys()), pre_embd_w)
model.load_state_dict(torch.load(save_path))

# run Flask app:
@app.route('/')
def index():
    global context1,context_settings1, uttr_list1, context_list1, bow_list1, prev_list1, act_fil_list1
    context1 = [0] * len(entities.keys())
    context_settings1 = {e: [] for e in entities.keys()}
    uttr_list1, context_list1, bow_list1, prev_list1, act_fil_list1 = [[], [], [], [], []]
    return render_template('index.html')

@app.route('/get')
def get_bot_response():
    uttr = request.args.get('msg')
    output = interactive(uttr, model, w2i, action_dict)
    # output = interactive1(uttr)
    return str(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    app.config['DEBUG'] = True
    app.debug = True
    app.config.update(
        DEBUG=True,
        SECRET_KEY='...'
    )