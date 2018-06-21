# dialog

## Install deepPavlov
- clone the repository
Since the project contains another repository [deepPavlov](https://github.com/deepmipt/DeepPavlov) as submodule, you need to pass --recurse-submodules to the git clone command, it will automatically initialize and update each submodule in the repository. For more details see [here](https://git-scm.com/book/en/v2/Git-Tools-Submodules).
See example:
```
$ git clone --recurse-submodules https://github.com/chaconinc/MainProject
Cloning into 'MainProject'...
remote: Counting objects: 14, done.
remote: Compressing objects: 100% (13/13), done.
remote: Total 14 (delta 1), reused 13 (delta 0)
Unpacking objects: 100% (14/14), done.
Checking connectivity... done.
Submodule 'DbConnector' (https://github.com/chaconinc/DbConnector) registered for path 'DbConnector'
Cloning into 'DbConnector'...
remote: Counting objects: 11, done.
remote: Compressing objects: 100% (10/10), done.
remote: Total 11 (delta 0), reused 11 (delta 0)
Unpacking objects: 100% (11/11), done.
Checking connectivity... done.
Submodule path 'DbConnector': checked out 'c3f01dc8862123d317dd46284b05b6892c7b29bc'
```

- install deepPavlov
0. Currently we support only `Linux` platform and `Python 3.6` (**`Python 3.5` is not supported!**)

1. Create a virtual environment with `Python 3.6`
    ```
    virtualenv env
    ```
2. Activate the environment.
    ```
    source ./env/bin/activate
    ```
3. `cd` to the directory
   ```
   cd DeepPavlov
   ```
4. Install the requirements:
    ```
    python setup.py develop
    ```
   If you don't have GPU, you need to install tensorflow separately.
5. Install `spacy` dependencies:
    ```
    python -m spacy download en
    ```

- Quick start (Restaurant reservation task)

1. To use our pre-trained models, you should first download them:
    ```
    python -m deeppavlov.download
    ```
2. Download English pretrained wiki fasttext embedding from [fasttext](https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md) and place the bin file wiki.simple.bin in the folder ```deepPavlov/DeepPavlov/download/embeddings/```.
3. Go to the directory ```deepPavlov/DeepPavlov/ ```
To train the model:
```
python -m deeppavlov.deep train deeppavlov/configs/go_bot/gobot_my.json
``` 
To use the model:
```
python -m deeppavlov.deep interact deeppavlov/configs/go_bot/gobot_my.json
```
The current accuracy on DSTC2
```
{"valid": {"examples_seen": 575, "metrics": {"per_item_dialog_accuracy": 0.530427954456223}, "time_spent": "0:02:14"}}
{"test": {"examples_seen": 576, "metrics": {"per_item_dialog_accuracy": 0.5310756205503175}, "time_spent": "0:02:00"}}
```
## PharmaBot based on deepPavlov

- copy the director pharma into DeepPavlov/download/. These are training/validate/text data and templates
- copy intent_cnn_v3_opt.json into DeepPavlov/download/intents/, if use gobot_pharma2.json.
- cop pharma.json into DeepPavlov/download/slots/

We have two different configurations: gobot_pharma.json and gobot_pharma2.json

To train, run:
```
python -m deeppavlov.deep train deeppavlov/configs/go_bot/gobot_pharma.json
```
or 

```
python -m deeppavlov.deep train deeppavlov/configs/go_bot/gobot_pharma2.json
```
To interact, run: 
```
python -m deeppavlov.deep interact deeppavlov/configs/go_bot/gobot_pharma.json
```
or 
```
python -m deeppavlov.deep interact deeppavlov/configs/go_bot/gobot_pharma2.json
```

