#!/usr/bin/env python3

import sys, os
import re
import subprocess
import struct

class ProcMapEntry:
    def __init__(self, start, end, permission, offset, dev, inode, path):
        self.start_addr = int(start, 16)
        self.end_addr = int(end, 16)
        self.permission = permission
        self.__parse_perm(permission)
        self.offset = int(offset, 16)
        self.dev = dev
        self.inode = inode
        if path != False:
            self.path = path
        else:
            self.path = self.__gen_path()

    def __gen_path(self):
        return "blank_0x{:x}-0x{:x}".format(self.start_addr, self.end_addr)

    def __parse_perm(self, permission):
        if permission[0] == "r":
            self.read = True
        else:
            self.read = False
        if permission[1] == "w":
            self.write = True
        else:
            self.write = False
        if permission[2] == "x":
            self.exe = True
        else:
            self.exe = False
        if permission[3] == "p":
            self.private = True
        else:
            self.private = False

    def get_path(self):
        return self.path

    def get_offset(self):
        return self.offset

    def get_start_addr(self):
        return self.start_addr

    def __str__(self):
        return "{} 0x{:x}-0x{:x} {} 0x{:x}".format(self.path, self.start_addr, self.end_addr, self.permission, self.offset)

class ProcMaps:
    def __init__(self, pid):
        self.pid = pid
        self.map_entries = {}

    def add_entry(self, entry):
        if self.map_entries.get(entry.get_path(), False) == False:
            self.map_entries[entry.get_path()] = []
        self.map_entries[entry.get_path()].append(entry)

    def get_all_path(self):
        return self.map_entries.keys()

    def get_entries(self, key):
        return self.map_entries[key]

def gen_symoff_table(cmd_result):
    symoff_table = {}
    for line in cmd_result.strip().split("\n")[1:]:
        symbol, offset = line.split(" ")
        symoff_table[symbol.strip()] = int(offset.strip(), 16)
    return symoff_table

def procmem_read(path, pid, gvar_name, symoff_table, base_addrs):
    fd = os.open("/proc/{}/mem".format(pid), os.O_RDWR)
    symoff = symoff_table[gvar_name]
    base_addr = base_addrs[path]
    print("access addr = 0x{:x}".format(base_addr + symoff))
    print("read result: 0x{:x}".format(struct.unpack("<I", os.pread(fd, 4, base_addr + symoff))[0]))

def procmem_write(path, pid, gvar_name, symoff_table, base_addrs, write_data):
    fd = os.open("/proc/{}/mem".format(pid), os.O_RDWR)
    symoff = symoff_table[gvar_name]
    base_addr = base_addrs[path]
    print("access addr = 0x{:x}".format(base_addr + symoff))
    print("before: 0x{:x}".format(struct.unpack("<I", os.pread(fd, 4, base_addr + symoff))[0]))
    os.pwrite(fd, struct.pack("<I", write_data), base_addr + symoff)
    print(" after: 0x{:x}".format(struct.unpack("<I", os.pread(fd, 4, base_addr + symoff))[0]))



def get_baseaddr(pid):
    p = ProcMaps(pid)
    with open("/proc/{}/maps".format(pid), "r") as f:
        for line in f:
            entry = re.sub(r" +", r" ", line.strip()).split(" ")
            if entry[-1] == "[stack]" or entry[-1] == "[vdso]" or entry[-1] == "[vvar]":
                pass
            addr = entry[0].split("-")
            perm = entry[1]
            offset = entry[2]
            dev = entry[3]
            inode = entry[4]
            if entry[-1] == "0":
                path = False
            else:
                path = entry[5]
            p.add_entry(ProcMapEntry(addr[0], addr[1], perm, offset, dev, inode, path))

    ret = {} 
    for k in p.get_all_path():
        for e in p.get_entries(k):
            print(e)
            if e.get_offset() == 0:
                ret[e.get_path()] = e.get_start_addr()
    return ret

def main():
    pyver_major = sys.version_info.major
    pyver_minor = sys.version_info.minor
    if not (pyver_major >= 3 and pyver_minor >= 3):
        print("I need python3.3 or later, so please use python3.3 or later...")
        sys.exit(1)

    if len(sys.argv) < 4:
        print("usage: ./gvtool.py </path/to/elfbinary> <PID> <GLOBAL_VARIABLE_NAME> {<WRITE_VALUE>}")
        sys.exit(1)

    filepath = os.path.abspath(sys.argv[1])
    pid = int(sys.argv[2].strip())
    gvar_name = sys.argv[3].strip()
    write_value = int(sys.argv[4])

    base_addrs = get_baseaddr(pid)
    print("************************")
    for k, v in base_addrs.items():
        print(k, v)

    result = subprocess.run(("./lssymtab {}".format(filepath)).split(" "), capture_output=True, text=True)
    print(result.stdout)
    symoff_table = gen_symoff_table(result.stdout)
    procmem_read(filepath, pid, gvar_name, symoff_table, base_addrs)
    procmem_write(filepath, pid, gvar_name, symoff_table, base_addrs, write_value)

if __name__ == "__main__":
    main()
