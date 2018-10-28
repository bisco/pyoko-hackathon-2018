#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define PACKAGE
#include <bfd.h>
#include <libgen.h>

int main (int argc, char *argv[])
{
    asymbol **symbol_table;
    bfd *abfd;
    uint32_t i;
    long bfd_vecsize;
    long number_of_symbols;

    if(argc != 2) {
        printf("usage: ./lssymtab </path/to/elfbinary>\n");
        exit(EXIT_FAILURE);
    }

    abfd = bfd_openr(argv[1], NULL);
    fprintf (stdout, "filepath %s\n", abfd->filename);
    if(false == bfd_check_format(abfd, bfd_object)) {
        fprintf(stderr, "bfd_check_format: bad format\n");
        exit(EXIT_FAILURE);
    }

    bfd_vecsize = bfd_get_symtab_upper_bound(abfd);
    if(bfd_vecsize <= 0) {
        fprintf(stderr, "bfd_vecsize = %ld and it must be larger than 0\n", bfd_vecsize);
        exit(EXIT_FAILURE);
    }

    symbol_table = (asymbol **)malloc(bfd_vecsize);
    number_of_symbols = bfd_canonicalize_symtab(abfd, symbol_table);
    if (number_of_symbols <= 0) {
        fprintf(stderr, "Error: number_of_symbols <= 0\n");
        exit(EXIT_FAILURE);
    }

    for (i = 0; i < number_of_symbols; i++) {
        if(((symbol_table[i]->flags & BSF_GLOBAL) != 0x00) && ((symbol_table[i]->flags & BSF_OBJECT) != 0x00)) {
            fprintf(stdout, "%s 0x%lx\n", bfd_asymbol_name(symbol_table[i]), bfd_asymbol_value(symbol_table[i]));
        }
    }

    return 0;
}
