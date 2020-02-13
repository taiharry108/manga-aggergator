import string
import lzstring
import re
digs = string.digits + string.ascii_letters

def decompress(s):
    x = lzstring.LZString()
    return x.decompressFromBase64(s)

def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)

def decode(p, a, c, k, d):
    def e(c):
        first = "" if c < a else e(int(c/a))
        c = c % a
        if c > 35:
            second = chr(c + 29)
        else:
            second = int2base(c, 36)
        return first + second
    while c != 0:
        c -= 1
        d[e(c)] = k[c] if k[c] != "" else e(c)
    k = [lambda x: d[x]]
    e = lambda: '\\w+'
    c = 1
    while c !=0:
        c -= 1
        p = re.sub(f'\\b{e()}\\b', lambda x: k[c](x.group()), p)
    return p