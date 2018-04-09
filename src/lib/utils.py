#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import readline


def console_print(sstr):
    sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())+2)+'\r')
    print (sstr)
    sys.stdout.write('> ' + readline.get_line_buffer())
    sys.stdout.flush()
