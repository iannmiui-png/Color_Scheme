#!/usr/bin/env python3
"""
color_scheme.py — interpreter for Color scheme by ablit
Reverse-engineered from program images and URL-encoded examples.

Confirmed semantics (derived by exhaustive matching):
  O-LB   push 0
  L      increment top (push 1 if empty)
  R      decrement top
  O-Y    DUP: copy top to top          (confirmed: Hello World double-l)
  O-P    ROT: move top to bottom       (confirmed: Fibonacci)
  BL-L   ADD: pop b, top += b          (confirmed: Fibonacci)
  BL-LB  MUL: pop b, top *= b          (confirmed: Hello World base 10)
  A-W    output top as number, pop
  A-B    output top as char, pop
           0=newline 1=space 2-27=a-z 28-53=A-Z 54+=chr(v-22)
  A-G    output top as raw chr(), pop
  A-L    read integer, push
  W      jump IP to start of next row
  B      halt
  G/B-B  no-op
  GR-O   if top != 0: jump to row 1
  Y-B-BL if top == 0: halt
  Y-B-R  if top == 0: halt (loop exit)
  Y-W-BL if top != 0: jump to row 1
  Y-W-R  if top != 0: jump to start of current row
"""
import sys

def ab_char(v):
    if v == 0: return '\n'
    if v == 1: return ' '
    if 2 <= v <= 27: return chr(ord('a') + v - 2)
    if 28 <= v <= 53: return chr(ord('A') + v - 28)
    if v >= 54: return chr(v - 22)
    return f'[{v}]'

def run(prog, input_val=None, max_steps=100_000, debug=False):
    rows = [r.split(',') for r in prog.strip().split('|')]
    s, out = [], []
    row = col = 0
    halted = False
    inp = [] if input_val is None else ([input_val] if not isinstance(input_val, list) else input_val)
    ip = [0]
    def read():
        if ip[0] < len(inp): v = inp[ip[0]]; ip[0] += 1; return v
        return int(input('? '))

    for _ in range(max_steps):
        if halted or row >= len(rows): break
        r = rows[row]
        if col >= len(r): row += 1; col = 0; continue
        c = r[col].strip().upper()
        if debug: print(f"  [{row},{col}] {c!r:12} {s}", file=sys.stderr)
        jumped = False

        if   c == 'B':     halted = True
        elif c == 'W':     row += 1; col = 0; jumped = True
        elif c in ('G', 'B-B', ''): pass
        elif c == 'O-LB':  s.append(0)
        elif c in ('L', 'O-L'):
            if s: s[-1] += 1
            else: s.append(1)
        elif c in ('R', 'O-R'):
            if s: s[-1] -= 1
        elif c == 'O-Y':   # DUP
            if s: s.append(s[-1])
        elif c == 'O-P':   # ROT: top to bottom
            if len(s) >= 3: s.insert(0, s.pop())
            elif len(s) == 2: s[0], s[1] = s[1], s[0]
        elif c == 'O-B':   s.clear()
        elif c == 'O-RO':  
            if s: s.append(s[-1])
        elif c == 'BL-L':  # ADD
            if len(s) >= 2: b = s.pop(); s[-1] += b
        elif c == 'BL-LB': # MUL
            if len(s) >= 2: b = s.pop(); s[-1] *= b
        elif c == 'A-W':   out.append(str(s.pop() if s else 0))
        elif c == 'A-B':   out.append(ab_char(s.pop() if s else 0))
        elif c == 'A-G':
            v = s.pop() if s else 0
            try: out.append(chr(v))
            except: out.append('?')
        elif c == 'A-L':   s.append(read())
        elif c == 'GR-O':
            if s and s[-1] != 0: row = 1; col = 0; jumped = True
        elif c == 'Y-B-BL':
            if not s or s[-1] == 0: halted = True
        elif c == 'Y-B-R':
            if not s or s[-1] == 0: halted = True
        elif c == 'Y-W-BL':
            if s and s[-1] != 0: row = 1; col = 0; jumped = True
        elif c == 'Y-W-R':
            if s and s[-1] != 0: col = 0; jumped = True
        elif debug:
            print(f"  UNKNOWN: {c!r}", file=sys.stderr)

        if not halted and not jumped:
            col += 1
            if col >= len(rows[row]): row += 1; col = 0

    return ''.join(out)

PROGRAMS = {
    'cat':       "A-L,A-W",
    'truth':     "A-L,GR-O,A-W,B|Y-B-BL,O-Y,A-W,Y-W-BL",
    'fibonacci': "O-LB,O-LB,L,O-LB,O-LB,A-W,A-B,W,B|Y-B-R,O-Y,O-P,BL-L,O-Y,A-W,O-LB,A-B,Y-W-R",
    'hello':     "O-LB,L,L,L,L,L,O-LB,L,L,BL-LB|O-Y,O-LB,L,L,L,BL-LB,L,L,L,L|L,A-B,O-Y,R,R,R,R,A-B,O-Y,L|L,L,O-Y,A-B,A-B,O-Y,L,L,L,L|L,L,A-B,O-LB,L,A-B,O-Y,O-LB,L,L|L,L,L,BL-LB,A-B,O-Y,L,L,L,L|L,L,A-B,O-Y,O-Y,BL-L,R,A-B,O-Y,L|L,L,A-B,O-LB,L,L,L,L,L,A-B|O-Y,L,O-LB,L,L,L,L,L,BL-LB,A-B",
    'heart':     "B-B,B-B,B-B,B-B,B-B,B-B,B-B|B-B,B-B,O-LB,B-B,L,B-B,B-B|B-B,L,L,O-Y,O-Y,O-Y,B-B|B-B,L,L,O-Y,BL-LB,BL-LB,B-B|B-B,B-B,R,BL-L,A-B,B-B,B-B|B-B,B-B,B-B,A-W,B-B,B-B,B-B|B-B,B-B,B-B,B-B,B-B,B-B,B-B",
}

if __name__ == '__main__':
    debug = '--debug' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('-')]

    if not args or args[0] == 'all':
        print(f"cat(42):     {run(PROGRAMS['cat'], 42)!r}")
        print(f"truth(0):    {run(PROGRAMS['truth'], 0)!r}")
        print(f"truth(1):    {run(PROGRAMS['truth'], 1, max_steps=30)!r}")
        print(f"hello world: {run(PROGRAMS['hello'])!r}")
        print(f"fibonacci:   {run(PROGRAMS['fibonacci'], max_steps=200)[:30]!r}...")
        print(f"heart:       {run(PROGRAMS['heart'])!r}")
    elif args[0] in PROGRAMS:
        inp = int(args[1]) if len(args) > 1 else None
        print(run(PROGRAMS[args[0]], inp, debug=debug))
    else:
        url_prog = args[0]
        inp = int(args[1]) if len(args) > 1 else None
        print(run(url_prog, inp, debug=debug))
