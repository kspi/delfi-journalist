#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <assert.h>
#include <sys/time.h>

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

    wid_t previous = 0;
    while (1) {
        wid_t current = sample(transition_distribution(previous));
        if (current == 0) {
            break;
        }

        if (previous != 0) {
            printf(" ");
        }
        printf("%s", word(current));
        previous = current;
    }
    printf("\n");

    return 0;
}
