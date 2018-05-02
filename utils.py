# 求两个数的最大公约数
def ext_euclid(a, b):
    if b == 0:
        return 1, 0, a
    else:
        x, y, q = ext_euclid(b, a % b)  # q = gcd(a, b) = gcd(b, a%b)
        x, y = y, (x - (a // b) * y)
        return x, y, q

# 快速求b^e%m
def fastExpMod(b, e, m):
    result = 1
    while e != 0:
        if (e&1) == 1:
            # ei = 1, then mul
            result = (result * b) % m
        e >>= 1
        # b, b^2, b^4, b^8, ... , b^(2^n)
        b = (b*b) % m
    return result

# 加密
B = 0x399fece631f18c964fa5fed2031b1bb7
E = 0xa4f85ea7a7f6822a2e1a8d11579b1e01
M = 0xc368fe392ec77cadb945d18dd4b6e0b1

print(hex(fastExpMod(B, E, M)))