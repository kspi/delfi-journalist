#!/usr/bin/env python3
import sqlite3
import os
import struct

def cstring(s):
    return s.encode("utf-8") + b"\0"

def main():
    db = sqlite3.connect('delfi.db')
    c = db.cursor()

    os.makedirs("db", exist_ok=True)

    c.execute('SELECT COUNT(*) FROM words;')
    wordcount, = c.fetchone()
    print("{} distinct words.".format(wordcount))
    with open("db/words", "wb") as f:
        f.write(struct.pack("I", wordcount))
        offset = f.tell() + wordcount * 4
        words = bytearray()
        c.execute('SELECT word FROM words ORDER BY id;')
        for w, in c.fetchall():
            f.write(struct.pack("I", offset))
            s = cstring(w)
            words += s
            offset += len(s)
        f.write(words)

    print("{} kernel rows.".format(wordcount))
    with open("db/kernel", "wb") as f:
        f.write(struct.pack("I", wordcount))
        offset = f.tell() + wordcount * 4
        dists = bytearray()
        for word1 in range(wordcount):
            dist = bytearray()
            c.execute('''
                SELECT COUNT(*), SUM(frequency)
                FROM kernel
                WHERE word1 == :word1;
            ''', dict(word1=word1))
            dist_size, total_freq = c.fetchone()
            if not total_freq:
                total_freq = 0
            dist += struct.pack('II', dist_size, total_freq)
            c.execute('''
                SELECT word2, frequency
                FROM kernel
                WHERE word1 == :word1
                ORDER BY frequency DESC;
            ''', dict(word1=word1))
            for wid, freq in c.fetchall():
                dist += struct.pack("II", wid, freq)
            f.write(struct.pack("I", offset))
            offset += len(dist)
            dists += dist
        f.write(dists)

if __name__ == "__main__":
    main()
