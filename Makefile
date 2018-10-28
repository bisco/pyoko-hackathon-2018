CC = gcc
MAKE = make

SRCDIR = $(realpath .)
INCDIR = $(SRCDIR)
OBJDIR = $(SRCDIR)
IGNORE =
SRCS = $(filter-out $(IGNORE),$(wildcard $(SRCDIR)/*.c))
OBJS = $(subst $(SRCDIR),$(OBJDIR),$(SRCS:.c=.o))
CFLAGS = -g -Wall -Wextra -Wpedantic -I$(INCDIR)
LDFLAGS = -lbfd
EXE = lssymtab

.PHONY: default conf clean
default: conf $(EXE)

conf:
	@echo "SRCDIR  = " $(SRCDIR)
	@echo "IGNORE  = " $(IGNORE)
	@echo "INCDIR  = " $(INCDIR)
	@echo "OBJDIR  = " $(OBJDIR)
	@echo "SRCS    = " $(SRCS)
	@echo "OBJS    = " $(OBJS)
	@echo "EXE     = " $(EXE)
	@echo "CC      = " $(CC)
	@echo "CFLAGS  = " $(CFLAGS)
	@echo "LDFLAGS = " $(LDFLAGS)

clean:
	rm -f $(OBJS) $(EXE)

$(EXE): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS) $(LDFLAGS)

$(OBJDIR)/%.o : $(SRCDIR)/%.c
	[ -d $(OBJDIR) ] || mkdir -p $(OBJDIR)
	$(CC) $(CFLAGS) -c -o $@ $<
