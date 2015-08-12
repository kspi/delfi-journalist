#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>

#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <assert.h>
#include <sys/time.h>

#define WORD_COUNT_MIN 3
#define WORD_COUNT_MAX 7
#define SENTENCE_LEN_MAX (WORD_COUNT_MAX * 2)

typedef uint32_t wid_t;

struct dist {
    uint32_t size;
    uint32_t total_freq;
    struct word_freq {
        wid_t wid;
        uint32_t freq;
    } word_freq[];
};

// 'words' is a vector of C strings. The index in this vector is the word's id.
struct words_header {
    uint32_t size;
    uint32_t offsets[];
} const *words;

// 'kernel' is a vector of struct dist. It represents the rows of the
// transition matrix.
struct kernel_header {
    uint32_t size;
    uint32_t offsets[];
} const *kernel;

void const *simple_mmap(char const *filename) {
    int fd = open(filename, O_RDONLY);
    assert(fd >= 0);
    struct stat stat;
    fstat(fd, &stat);
    void const *result = mmap(NULL, stat.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    assert(result != MAP_FAILED);
    return result;
}

void open_database(void) {
    words = simple_mmap("db/words");
    kernel = simple_mmap("db/kernel");
}

char const *word(wid_t wid) {
    return (char const *) (((uint8_t *)words) + words->offsets[wid]);
}

struct dist const *transition_distribution(wid_t from) {
    return (struct dist *) (((uint8_t *)kernel) + kernel->offsets[from]);
}

wid_t sample(struct dist const *dist) {
    uint32_t x = rand() % dist->total_freq;
    uint32_t sum = 0;
    int i = 0;
    while (i < dist->size) {
        uint32_t freq = dist->word_freq[i].freq;
        sum += freq;
        if (sum >= x) {
            return dist->word_freq[i].wid;
        }
        if (freq == 1) {
            // Since freqs are sorted descending, when we reach the tail of 1s
            // we can skip directly to the chosen word.
            i += x - sum;
            sum = x;
        } else {
            i += 1;
        }
    }
    assert(0);
}

int main(int argc, char **argv) {
    struct timeval timeval;
    gettimeofday(&timeval, NULL);
    srand((timeval.tv_sec + timeval.tv_usec) % UINT_MAX);

    open_database();
    assert(word(0)[0] == '\0');

    wid_t sentence[SENTENCE_LEN_MAX];
    int sentence_len;

generate:
    sentence_len = 0;
    wid_t previous = 0;
    int word_count = 0;
    while (1) {
        if (sentence_len > SENTENCE_LEN_MAX) {
            goto generate;
        }

        if (word_count > WORD_COUNT_MAX) {
            goto generate;
        }

        wid_t current = sample(transition_distribution(previous));
        if (current == 0) {
            break;
        }

        sentence[sentence_len] = current;
        ++sentence_len;

        if (strlen(word(current)) > 2) {
            ++word_count;
        }

        previous = current;
    }

    if (word_count < WORD_COUNT_MIN) {
        goto generate;
    }

    previous = 0;
    for (int i = 0; i < sentence_len; ++i) {
        wid_t current = sentence[i];
        if (previous != 0) {
            printf(" ");
        }

        printf("%s", word(current));
        previous = current;
    }
    printf("\n");

    return 0;
}
