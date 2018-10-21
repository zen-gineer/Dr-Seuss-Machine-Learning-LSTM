
# coding: utf-8

# In[178]:


import numpy
from pickle import dump
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
import sys
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from keras.layers import Embedding, Flatten

#notes from website:
#-- Common values are 50, 100, and 300. We will use 50 here, --
#-- but consider testing smaller or larger values. --
#-- We will use a two LSTM hidden layers with 100 memory cells each. --
#-- More memory cells and a deeper network may achieve better results. --

#parameters
drseuss_text = 'data/combinedText.txt'
seed_length = 50
epochs = 500
batch_size=128
modelList = [('LSTM',256,'True'), ('Dense',256,'relu'), ('Dropout',.2,''), 
             ('LSTM',128,'True'), ('Dense',128,'relu'), ('Dropout',.2,''), 
             ('LSTM', 64,'False'), ('Dense',64,'relu'), 
             ('Flatten','',''),('Dense',vocab_size,'softmax')]
#Create the model name
modelName = f'm_{length}'
for layer in modelList:
    modelName+= f'_{layer[0]}_{layer[1]}_{layer[2]}'
modelName += '.h5'
modelName

#create tokenizer file name .pkl
tokenizerName = 'toke' + modelName.replace('m','',1).split('.h5')[0] + '.pkl'
print(f'drseuss_text: \'{drseuss_text}\'\nseed_length: {seed_length}\nepochs: {epochs}\nbatch_size: {batch_size}'
     f'\nmodelName: {modelName}\ntokenizerName: {tokenizerName}\nmodelList: {modelList}')


# In[179]:


# load doc into memory
def load_doc(filename):
    # open the file as read only
    file = open(filename, 'r')
    # read all text
    text = file.read()
    # close the file
    file.close()
    tokens = text.split()
    return tokens

# load document
in_filename = 'data/combinedText.txt'
tokens = load_doc(drseuss_text)
print(tokens[:200])
print('Total Tokens: %d' % len(tokens))
print('Unique Tokens: %d' % len(set(tokens)))


# In[180]:


# organize into sequences of tokens
#the plus one is because the last val in the list will be the expected prediction. 
#Its our Y-train
length = seed_length + 1
sequences = list()
for i in range(length, len(tokens)):
    # select sequence of tokens
    seq = tokens[i-length:i]
    # convert into a line
    #line = ' '.join(seq)
    # store
    sequences.append(seq)
print('Total Sequences: %d' % len(sequences))
print(f'sequences: {type(sequences[0])}')

# import pandas as pd
# df = pd.DataFrame(sequences)
# X = df.iloc[:,:-1]
# y = df.iloc[:,-1]


# In[181]:


tokenizer = Tokenizer()
# integer encode sequences of words
#sequences = [str(i) for i in sequences]
# print(f'tokenizer: {tokenizer}')
tokenizer.fit_on_texts(sequences)
# print(f'tokenizer: {tokenizer}')
sequences = tokenizer.texts_to_sequences(sequences)
# print(f'sequences: {sequences}')


# In[182]:


# vocabulary size
vocab_size = len(tokenizer.word_index) + 1
vocab_size


# In[183]:


import pandas as pd
df = pd.DataFrame(sequences)
X = df.iloc[:,:-1]
y = df.iloc[:,-1]
y = to_categorical(y, num_classes=vocab_size)
seq_length = X.shape[1]
print(f'seq_length: {seq_length}\nshape of X: {X.shape}\nshape of y: {y.shape}')
print(y[0])


# In[184]:


# define model
model = Sequential()
model.add(Embedding(vocab_size, seq_length, input_length=seq_length))
print(f'model.add(Embedding({vocab_size}, {seq_length}, input_length={seq_length}))')
for layer in modelList:
    if layer[0] == 'LSTM':
        #model.add(LSTM(100, return_sequences=True))
        (_, neurons, rsequences) = layer
        model.add(LSTM(neurons, return_sequences=rsequences))
        print(f'model.add(LSTM({neurons}, return_sequences={return_sequences}))')
        
    if layer[0] == 'Dropout':
        #model.add(Dropout(0.2))
        (_, dropout_rate, _) = layer
        model.add(Dropout(dropout_rate))
        print(f'model.add(Dropout({dropout_rate}))')
        
    if layer[0] == 'Dense':
        #model.add(Dense(100, activation='relu'))
        (_, neurons, afunction) = layer
        model.add(Dense(neurons, activation=afunction))
        print(f'model.add(Dense({neurons}, activation={afunction}))')
        
    if layer[0] == 'Flatten':
        model.add(Flatten())
        print(f'model.add(Flatten())')
        
#model.add(LSTM(100, return_sequences=True))
#model.add(Dropout(0.2))
#model.add(LSTM(100))
#model.add(Dense(100, activation='relu'))
#model.add(Dense(vocab_size, activation='softmax'))
print(model.summary())


# In[185]:


# compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# fit model
model.fit(X, y, batch_size=batch_size, epochs=epochs)


# In[157]:


# save the model to file
modelName = f'm_{length}'
for layer in modelList:
    modelName+= f'_{layer[0]}_{layer[1]}_{layer[2]}'
modelName += '.h5'

# save the model to file
model.save(modelName)
# save the tokenizer
dump(tokenizer, open(tokenizerName, 'wb'))


# In[158]:


from random import randint
from pickle import load
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences


# In[159]:


# generate a sequence from a language model
#def generate_seq(model, tokenizer, seq_length, seed_text, n_words):
def generate_seq(model, tokenizer, seq_length, seed_text, n_words):
    result = list()
    in_text = seed_text
    # generate a fixed number of words
    for _ in range(n_words):
        # encode the text as integer
        encoded = tokenizer.texts_to_sequences([in_text])[0]
        # truncate sequences to a fixed length
        encoded = pad_sequences([encoded], maxlen=seq_length, truncating='pre')
        # predict probabilities for each word
        yhat = model.predict_classes(encoded, verbose=0)
        # map predicted word index to word
        out_word = ''
        for word, index in tokenizer.word_index.items():
            if index == yhat:
                out_word = word
                break
        # append to input
        in_text += ' ' + out_word
        result.append(out_word)
    return ' '.join(result)


# In[160]:


# load the model
model = load_model(modelName)
 
# load the tokenizer
tokenizer = load(open(tokenizerName, 'rb'))


# In[161]:


# select a seed text
# seed_text = lines[randint(0,len(lines))]
seed_text = '''Whosever room this is should be ashamed!
His underwear is hanging on the lamp.
His raincoat is there in the overstuffed chair,
And the chair is becoming quite mucky and damp.
His workbook is wedged in the window,
His sweater's been thrown on the floor.
His scarf and one ski are'''
seed_text = ' '.join(seed_text.split(' ')[0:50])
print(seed_text + '\n')


# In[162]:


#encode our seed
encoded = tokenizer.texts_to_sequences([seed_text])[0]


# In[163]:


# generate new text
generated = generate_seq(model, tokenizer, seq_length, seed_text, seed_length)
print(generated)

