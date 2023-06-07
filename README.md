# X25519-from-the-scratch

This is not an implementation to be used in a real world scenario. It is only intended to illustrate how X25519 works.

X25519 is executed on curve 25519. Curve 25519 is a [Montgomery curve][i_1]: By^2 = x^3 + Ax^2 + x The curve parameters are: 

```
A = 486662 
B = 1
p = 2**255 - 19 # prime, order of Gallois field GF(p)
Gx = 9
Gy = 14781619447589544791020593568409986887264606134616475288964881837755586237401
l = 2**252 + 27742317777372353535851937790883648493 # order of G, = order of subgroup generated by G 
```

X25519 is described in [RFC 7748][i_2].

-----------------

**Part 1: Point addition**

The addition and the doubling of points in affine coordinates is described e.g. in [*Montgomery curves and their arithmetic*][1_1], *chapter 2.2 The group law*.

Besides, a description in projective coordinates is possible, see [*Montgomery arithmetic*][1_2] in *Wikipedia* or [*Montgomery curves and their arithmetic*][1_1], chapters *3.2 Point addition* and *3.3 Point doubling*. 

While with the affine coordinates the x coordinate of the added/doubled point depends on the y coordinate, with the projective coordinates the X coordinate of the added/doubled point does not depend on the Y (and Z) coordinate. Since for the calculation to X25519 the Y coordinate is not needed, this is omitted. Thereby, however, information is lost, since from the projective coordinates the affine y coordinate cannot be derived unambiguously (but only +y, -y), see [*Montgomery arithmetic*][1_2] in Wikipedia.

The calculations with the affine coordinates contain in contrast to those with the projective coordinates modular divisions and are therefore less performat than those of the projective coordinates, which is why projective coordinates are used in the calculations for X25519. The associated shortcoming of not being able to uniquely determine the affine y coordinate is irrelevant because the y coordinate is not needed for the calculations to X25519. 
As a result, a transformation from affine to projective coordinates is possible, but conversely only the affine x coordinate can be determined from the projective coordinates. This representation is called *compressed* in the following.

With the point addition in projective coordinates it is to be noted that the addition of two points Q1 and Q2 takes place under the secondary condition Q2 = Q1 + P with known P. This is not really a problem in connection with the Montgomery Ladder for point multiplication, since there the individual additions are executed under exactly this condition (see Montgomery Ladder in the next chapter).

The point addition and doubling for X25519 is implemented in *100_point_addition.py* along with tests for addition/doubling with affine and projective coordinates.

-----------------

**Part 2: Point multiplication**

The point multiplication uses the Montgomery ladder, which controls point addition and point doubling by the bit representation of the scalar. The pseudo code of the Montgomery ladder can be found e.g. in [Montgomery ladder][2_1] on Wikipedia or in [Montgomery curves and their arithmetic][1_1], chapter 4.1 The ladder in a group:

```
  R0 ← 0
  R1 ← P
  for i from m downto 0 do
      if di = 0 then
          R1 ← point_add(R0, R1)
          R0 ← point_double(R0)
      else
          R0 ← point_add(R0, R1)
          R1 ← point_double(R1)
  return R0
```

In the algorithm, R1 = R0 + P is always satisfied, which is exactly the constraint that holds for the point addition, so this relation can be used here.

So that no information is leaked (side channel attacks), the point multiplication must be time-constant. For this it is necessary that the *same* operations are performed for an unset bit and a set bit. This is fulfilled in the Montgomery Ladder. Note that in the end only R0 is returned, not R1. R1 is finally only needed to realize identical operations for 0- and 1-bits.  
Furthermore, the implementation must be time-constant, regardless of which is the most significant bit. Therefore, in this implementation, a fixed bit length (256 bits) is used by padding with leading 0 bits. The algorithm of X25519 (and also Ed25519) additionally *implicitly* set the most significant bit to 0 and the second most significant bit to 1 (see clamping in next chapter), so that even insecure implementations that depend on which is the most significant bit are time-constant in this respect.

*200_point_multiplication.py* contains an implementation of the point multiplication based on the Montgomery Ladder and test cases.

-----------------

**Part 3: Clamping**

Clamping is the modification of certain bits in the scalar of the point multiplication. The purpose is to make the algorithm more secure and robust.

```
      0. byte (ls byte), 1. byte, ...		  31. byte (ms byte)
      _ _ _ _   _ 0 0 0           		    0 1 _ _   _ _ _ _
 ms bit               ls bit         ms bit               ls bit
```

Clamping sets the two most significant bits to 0 and 1 (M1) and the three least significant bits to 0 (M2). The purpose of M1 is to neutralize the danger of bad implementations of point multiplications whose time behavior depends on which is the most significant bit, by giving each key per definition the same most significant bit.  
M2 is equivalent to multiplication by 8. curve25519 and edwards25519 both have a cofactor of 8 and therefore have small order subgroups (of order 1, 2, 4 and 8). If a point from such a group is multiplied by 8, the neutral element is obtained. If the other side sends a key from such a subgroup, the neutral element would therefore be generated during the generation of the shared secret: `priv * small_order_pub = priv' * 8 * small_order_pub = 0`, by which such a point would be recognized (and thus a possible small subgroup attack).

More details about clamping can be found in:  
[*An Explainer On Ed25519 Clamping*][3_1]  
[*What’s the Curve25519 clamping all about?*][3_2]

Clamping and tests are implemented in *300_clamping.py*.

-----------------

**Part 4: Key generation**

For key generation, the secret key s is generated as a random 32 bytes sequence. From this the key is derived by first clamping the secret key and using the result s_clamped to perform a point multiplication with the generator point G: public = s_clamped * G.  

[i_1]: https://en.wikipedia.org/wiki/Montgomery_curve
[i_2]: https://datatracker.ietf.org/doc/html/rfc7748

[1_1]: https://inria.hal.science/hal-01483768/document
[1_2]: https://en.wikipedia.org/wiki/Montgomery_curve#Montgomery_arithmetic

[2_1]: https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Montgomery_ladder

[3_1]: https://www.jcraige.com/an-explainer-on-ed25519-clamping
[3_2]: https://neilmadden.blog/2020/05/28/whats-the-curve25519-clamping-all-about/

