#!/usr/bin/env python3

import sqlite3
import numpy


def generate_title_words(db):
    c = db.cursor()
    c.execute('SELECT word, frequency FROM startwords;')
    startwords, startword_freqs = zip(*list(c.fetchall()))
    s = sum(startword_freqs)
    startword_probabilities = [x / s for x in startword_freqs]
    title_words = []
    word = startwords[numpy.random.choice(len(startwords), p=startword_probabilities)]
    while word != None:
        title_words.append(word)
        c.execute('SELECT word2, frequency FROM pairs WHERE word1 = ?;', (word,))
        words, word_freqs = zip(*list(c.fetchall()))
        s = sum(word_freqs)
        word_probabilities = [x / s for x in word_freqs]
        word = words[numpy.random.choice(len(words), p=word_probabilities)]
    return title_words

def generate_title(db):
    ws = generate_title_words(db)
    while not (3 < len(ws) <= 8):
        ws = generate_title_words(db)
    return ' '.join(ws)

def main():
    db = sqlite3.connect('delfi.db')
    for i in range(10):
        print(generate_title(db))

if __name__ == "__main__":
    main()
