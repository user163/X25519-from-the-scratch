# curve25519 parameters
A = 486662 
B = 1
p = 2**255 - 19 # prime, order of Gallois field GF(p)
Gx = 9
Gy = 14781619447589544791020593568409986887264606134616475288964881837755586237401
l = 2**252 + 27742317777372353535851937790883648493 # order of G, = order of subgroup generated by G 

# from previous chapters ############################################################################

'''
Q1 <> Q2
Constraint: Q2 = Q1 + P
Q3 := Q1 + Q2
'''
def add_projective_constDiff(Q1, Q2, P):
    (X1, Z1) = Q1
    (X2, Z2) = Q2
    (PX, PZ) = P
    S = ((X2 - Z2) * (X1 + Z1)) % p
    T = ((X2 + Z2) * (X1 - Z1)) % p
    X3 = (PZ * pow(S + T, 2, p)) % p
    Z3 = (PX * pow(S - T, 2, p)) % p
    return (X3, Z3)

'''
Q3 = 2 * Q1
'''
def double_projective(Q1):
    (X1, Z1) = Q1
    X3 = (pow(X1 + Z1, 2, p) * pow(X1 - Z1, 2, p)) % p
    Z3 = (4 * X1 * Z1 * (pow(X1 - Z1, 2, p) + (A + 2) * X1 * Z1) ) % p
    return (X3, Z3)

def projective_to_compressed(q1): #projective_to_compressed
    (x1, z1) = q1
    if (z1 == 0):
        return None
    return ((x1 * pow(z1, -1, p)) % p)

def compressed_to_projective(q1):
    if q1 == None:
        return (1,0)
    return (q1, 1)

# Montgomery Ladder, time constant for scalars up to 256 bits
def point_multiplication(s, P):
    Q = (1,0)                           # neutral element
    R = P
    bits = bin(s)[2:]                   # bit encoding of s
    bitsPadded = bits.rjust(256, '0')   # the bit representation of all scalars is extended with leading 0 to 256 bit 
    for b in bitsPadded:                # for each step, the same operations are done, no matter if the bit is 0 or 1
        if b == '0':
            R = add_projective_constDiff(Q, R, P) # Q + R with R = Q + P
            Q = double_projective(Q)
            
        else:
            Q = add_projective_constDiff(Q, R, P) # Q + R with R = Q + P
            R = double_projective(R)
    return Q

def clamp(data_b): # data_b in little endian order
    a_b = bytearray(data_b)
    a_b[0] &= 248  # 0.  byte: set the three least significant bits to 0
    a_b[31] &= 127 # 31. byte: set the most significant bit to 0
    a_b[31] |= 64  #           ...and the second-most significant bit to 1
    return bytes(a_b) 

def le_encode_to_bytes(number):
    return int.to_bytes(number, 32, "little")

def le_decode_to_number(number_b):
    return int.from_bytes(number_b, "little")
  
def secret_clamp(secret_key_b):
    if len(secret_key_b) != 32:
        raise Exception("Bad size of secret key")
    secret_key_clamped_b = clamp(secret_key_b)
    secret_key_clamped = le_decode_to_number(secret_key_clamped_b)
    return secret_key_clamped

def get_public_from_secret(secret_key_b):
    secret_key_clamped = secret_clamp(secret_key_b)
    G = compressed_to_projective(Gx)
    public_key = point_multiplication(secret_key_clamped, G)
    public_key_comp = projective_to_compressed(public_key)
    public_key_b = le_encode_to_bytes(public_key_comp)
    return public_key_b

# new ###############################################################################################

def get_shared_secret(secret_key_b, public_key_b):
    secret_key_clamped = secret_clamp(secret_key_b)
    public_key_comp = le_decode_to_number(public_key_b)
    public_key = compressed_to_projective(public_key_comp)
    shared_secret = point_multiplication(secret_key_clamped, public_key)
    shared_secret_comp = projective_to_compressed(shared_secret)
    shared_secret_b = le_encode_to_bytes(shared_secret_comp)
    return shared_secret_b

'''
# testvector from RFC 7748, 6.1. Curve25519
Alice's private key, a:
     77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a
   Alice's public key, X25519(a, 9):
     8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a
   Bob's private key, b:
     5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb
   Bob's public key, X25519(b, 9):
     de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f
   Their shared secret, K:
     4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742
'''

# derive public keys
alice_secret_key = bytes.fromhex('77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a')
alice_public_key = get_public_from_secret(alice_secret_key)
print(alice_public_key.hex())

bob_secret_key = bytes.fromhex('5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb')
bob_public_key = get_public_from_secret(bob_secret_key)
print(bob_public_key.hex())

# derive shared secrets
alice_shared_secret = get_shared_secret(alice_secret_key, bob_public_key)
print(alice_shared_secret.hex())

bob_shared_secret = get_shared_secret(bob_secret_key, alice_public_key)
print(bob_shared_secret.hex())