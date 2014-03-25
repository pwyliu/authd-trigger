# Fully qualified paths to binaries
AUTHD = '/var/ossec/bin/ossec-authd'
PGREP = '/usr/bin/pgrep'
TIMEOUT = '/usr/bin/timeout'

# Time before killing authd
TIMEOUT_DURATION = '15m'

# Password Settings
#-----------------------------------------------------------------------------
# Set to "True" to require a password.
# If you require a password, you must generate a password hash by running
# generate_hash.py. See README.md for more details.
#
# This is not really like a super cryptographically secure way to do this.
# Don't do this in a high security environment
# ----------------------------------------------------------------------------
require_password = False
# e.g. password_hash = 'pbkdf2:sha256:5000$LSiB0lZ3oRILcjVq$9687738372815171ab910cd35bd40e54a37174e548742eb5417177f3b2b5bc77'
password_hash = ''
