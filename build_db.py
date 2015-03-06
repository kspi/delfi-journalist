#!/usr/bin/env python3

import json
from collections import defaultdict
import pickle
import sqlite3
import os
import itertools
import re

def nwise(iterable, n=2):                                                      
    iters = itertools.tee(iterable, n)                                                     
    for i, it in enumerate(iters):                                               
        next(itertools.islice(it, i, i), None)                                               
    return zip(*iters)   

def padded(xs, padding, n=1):
    for i in range(n):
        yield padding
    yield from xs
    for i in range(n):
        yield padding

def padded_nwise_words(xs, padding, n=2):
    return nwise(padded(xs, '', n - 1), n)

def main():
    try:
        os.remove("delfi.db")
    except FileNotFoundError:
        pass
    db = sqlite3.connect('delfi.db')
    db.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY,
            word TEXT NOT NULL,
            UNIQUE(word)
        );
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS kernel (
            word1 INTEGER NOT NULL,
            word2 INTEGER NOT NULL,
            frequency INTEGER NOT NULL
        );
    ''')
    db.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS words_index
            ON words (word);
    ''')
    db.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS kernel_index
            ON kernel (word1, word2);
    ''')
    c = db.cursor()
    with open("items.json") as f:
        items = json.load(f)
    c.execute('''
        INSERT INTO words (id, word)
        VALUES (0, '');
    ''')
    dash_re = re.compile(r'\s*[–—]\s*')
    whitespace_re = re.compile(r'\s+')
    for i, item in enumerate(items):
        if i % 10000 == 0:
            print("{}/{} {:.2f}%".format(i, len(items), i / len(items) * 100))
        try:
            title = item['title'][0]
        except IndexError:
            continue
        title = dash_re.sub(' - ', title)
        words = whitespace_re.split(title)
        for w in words:
            c.execute('''
                INSERT OR IGNORE INTO words (id, word)
                VALUES (1 + (SELECT MAX(id) FROM words), :word);
            ''', dict(word=w))
        for word1, word2 in padded_nwise_words(words, 2):
            c.execute('''
                INSERT OR REPLACE INTO kernel (word1, word2, frequency)
                VALUES (
                    (SELECT id FROM words WHERE word = :word1),
                    (SELECT id FROM words WHERE word = :word2),
                    COALESCE (
                        (SELECT frequency FROM kernel
                            WHERE word1 = :word1 and word2 = :word2),
                        0
                    ) + 1
                );
            ''', dict(word1=word1, word2=word2))
    db.commit()

if __name__ == "__main__":
    main()
