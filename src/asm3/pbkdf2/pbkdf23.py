''' Password based key-derivation function - PBKDF2 '''

# This module is for Python 3

# Copyright (c) 2011, Stefano Palazzo <stefano.palazzo@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import hmac
import hashlib
import os
import struct

def pbkdf2(digestmod, password: 'bytes', salt, count, dk_length) -> 'bytes':
    '''
    PBKDF2, from PKCS #5 v2.0:
        http://tools.ietf.org/html/rfc2898

    For proper usage, see NIST Special Publication 800-132:
        http://csrc.nist.gov/publications/PubsSPs.html

    The arguments for this function are:

        digestmod
            a crypographic hash constructor, such as hashlib.sha256
            which will be used as an argument to the hmac function.
            Note that the performance difference between sha1 and
            sha256 is not very big. New applications should choose
            sha256 or better.

        password
            The arbitrary-length password (passphrase) (bytes)

        salt
            A bunch of random bytes, generated using a cryptographically
            strong random number generator (such as os.urandom()). NIST
            recommend the salt be _at least_ 128bits (16 bytes) long.

        count
            The iteration count. Set this value as large as you can
            tolerate. NIST recommend that the absolute minimum value
            be 1000. However, it should generally be in the range of
            tens of thousands, or however many cause about a half-second
            delay to the user.

        dk_length
            The lenght of the desired key in bytes. This doesn't need
            to be the same size as the hash functions digest size, but
            it makes sense to use a larger digest hash function if your
            key size is large. 

    '''
    def pbkdf2_function(pw, salt, count, i):
        # in the first iteration, the hmac message is the salt
        # concatinated with the block number in the form of \x00\x00\x00\x01
        r = u = hmac.new(pw, salt + struct.pack(">i", i), digestmod).digest()
        for i in range(2, count + 1):
            # in subsequent iterations, the hmac message is the
            # previous hmac digest. The key is always the users password
            # see the hmac specification for notes on padding and stretching
            u = hmac.new(pw, u, digestmod).digest()
            # this is the exclusive or of the two byte-strings
            r = bytes(i ^ j for i, j in zip(r, u))
        return r
    dk, h_length = b'', digestmod().digest_size
    # we generate as many blocks as are required to
    # concatinate to the desired key size:
    blocks = (dk_length // h_length) + (1 if dk_length % h_length else 0)
    for i in range(1, blocks + 1):
        dk += pbkdf2_function(password, salt, count, i)
    # The length of the key wil be dk_length to the nearest
    # hash block size, i.e. larger than or equal to it. We
    # slice it to the desired length befor returning it.
    return dk[:dk_length]

def test():
    '''
    PBKDF2 HMAC-SHA1 Test Vectors:
        http://tools.ietf.org/html/rfc6070

    '''
    # One of the test vectors has been removed because it takes
    # too long to calculate. This was a test vector of 2^24 iterations.
    # Since there is no difference between integers and long integers
    # in python3, this will work as well as the others.
    rfc6070_test_vectors = (
        (b"password", b"salt", 1, 20),
        (b"password", b"salt", 2, 20),
        (b"password", b"salt", 4096, 20),
        (b"passwordPASSWORDpassword",
            b"saltSALTsaltSALTsaltSALTsaltSALTsalt", 4096, 25),
        (b"pass\0word", b"sa\0lt", 4096, 16),
    )
    rfc6070_results = (
        b"\x0c\x60\xc8\x0f\x96\x1f\x0e\x71\xf3\xa9\xb5\x24\xaf\x60\x12\x06"
            b"\x2f\xe0\x37\xa6",
        b"\xea\x6c\x01\x4d\xc7\x2d\x6f\x8c\xcd\x1e\xd9\x2a\xce\x1d\x41\xf0"
            b"\xd8\xde\x89\x57",
        b"\x4b\x00\x79\x01\xb7\x65\x48\x9a\xbe\xad\x49\xd9\x26\xf7\x21\xd0"
            b"\x65\xa4\x29\xc1",
        b"\x3d\x2e\xec\x4f\xe4\x1c\x84\x9b\x80\xc8\xd8\x36\x62\xc0\xe4\x4a"
            b"\x8b\x29\x1a\x96\x4c\xf2\xf0\x70\x38",
        b"\x56\xfa\x6a\xa7\x55\x48\x09\x9d\xcc\x37\xd7\xf0\x34\x25\xe0\xc3",
    )
    for v, r in zip(rfc6070_test_vectors, rfc6070_results):
        assert pbkdf2(hashlib.sha1, *v) == r, v

if __name__ == '__main__':
    test()
    print("all tests passed")
