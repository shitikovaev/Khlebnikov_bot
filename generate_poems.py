import os
import get_poems
import gensim
import pymorphy2
import json
import random

# path to check if get_poems has already been done.
path = './resources/json/poems.json'
file = 'resources/json/poems.json'

# list of parts of speech that we don't change
STOP_POS = ['CONJ', 'PREP', 'PRCL', 'NPRO', ]

# dict to translate OpenCorpora tags to Universal Tags format (Pymorphy -> model)
OC_UT_dict = {
    'ADVB': 'ADV',
    'NUMR': 'NUM',
    'ADJF': 'ADJ',
    'ADJS': 'ADJ',
    'INFN': 'VERB',
    'COMP': 'ADV',
    'PRTF': 'VERB',
    'PRTS': 'VERB',
    'GRND': 'VERB',
    'PRED': 'ADV',
    'NPRO': 'NOUN'
}

poems_new = []

if not (os.path.exists(path) and os.path.isfile(file)):
    get_poems.makeFiles()

# get results from previous steps
with open(file, 'r') as f:
    poems = json.load(f)

with open('resources/json/poems_clean.json', 'r') as f:
    poems_clean = json.load(f)

# initialize model and PM analyzer
model = gensim.models.KeyedVectors.load_word2vec_format('resources/model.bin', binary=True)
model.init_sims(replace=True)

morph = pymorphy2.MorphAnalyzer()


# returns a list of similar lemmas from model. If can't find, returns None.
def findSimilar(lemma, pos):
    try:
        similar = model.most_similar(lemma)
        # filters similar to get only those words that have the same part of speech
        words = [x[0] for x in similar if x[0].endswith(str(pos))]
        return words
    except:
        # print(lemma, 'is not found')
        return None


# gets a word in a particular form and returns most similar in the same form
def replace_word(word):
    parsed = morph.parse(word)[0]
    tag = parsed.tag
    pos_oc = str(tag.POS)

    # Check if we need to replace that word:
    if pos_oc not in STOP_POS:

        # translate it to UT format
        if pos_oc in OC_UT_dict.keys():
            pos_ut = OC_UT_dict[pos_oc]
        else:
            pos_ut = pos_oc

        # create lemma
        lemma = str(parsed.normal_form) + '_' + pos_ut
        similars = findSimilar(lemma, pos_ut)
        if similars:
            for similar in similars:
                # gets the normal form of the word
                similar = similar.split('_')[0]

                # translate tag from analyzers form to generator form
                new_tag = translate_tag(tag)

                # put similar word to initial form
                similar_parsed = morph.parse(similar)[0]
                new_word = similar_parsed.inflect(frozenset(new_tag))

                # if successfully, return it
                if new_word:
                    return new_word.word
            return None
        else:
            return None
    else:
        return None


# simply cast string splitted by commas and spaces to list
def translate_tag(tag):
    tag = str(tag).split(' ')
    new_tag = []
    for x in tag:
        new_tag.extend(x.split(','))
    return new_tag


# for every poem, we take according poem cleaned, and for every word we try to replace it.
def makeNewPoems():
    for i in range(len(poems)):
        poem = poems[i]
        for word in poems_clean[i].split(' '):
            # check if it is a word
            if str.isalpha(word):
                new_word = replace_word(word)
                if new_word:
                    # If initial word was capitalized, we capitalize the new word
                    if word[0].isupper():
                        new_word = new_word.capitalize()
                    poem = poem.replace(word, new_word)
        poems_new.append(poem)
    # put all new poem to the json file
    with open('resources/json/poems_new.json', 'w', encoding='utf8') as f:
        json.dump(poems_new, f, ensure_ascii=False)


# makeNewPoems()

# returns a random original poem and a generated one.
def getTwoPoems():
    if not (os.path.exists('./resources/json/poems_new.json') and os.path.isfile('./resources/json/poems_new.json')):
        makeNewPoems()
    with open('resources/json/poems_new.json', 'r') as f:
        poems_new = json.load(f)
    i = random.randint(0, len(poems) - 1)
    return poems[i], poems_new[i]
