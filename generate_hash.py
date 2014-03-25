#!/usr/bin/env python

import werkzeug.security
import argparse

parser = argparse.ArgumentParser(
    description='Generate a werkzeug password hash')
parser.add_argument(
    'password',
    type=str,
    help='password to hash')
args = parser.parse_args()
pwhash = werkzeug.security.generate_password_hash(
    args.password,
    method='pbkdf2:sha256:5000',
    salt_length=16,
)

print pwhash
