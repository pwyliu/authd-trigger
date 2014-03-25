# Fully qualified paths to binaries
AUTHD = '/var/ossec/bin/ossec-authd'
PGREP = '/usr/bin/pgrep'
TIMEOUT = '/usr/bin/timeout'

# Time before killing authd
TIMEOUT_DURATION = '15m'

# Password Settings
#-----------------------------------------------------------------------------
# Set to "True" to require a password.
# If you require a password you must set password salt and password hash.
# The salt and hash must both be hex encoded. See the README.
#
# This is not really like a super cryptographically secure way to do this.
# Don't do this in a high security environment
# ----------------------------------------------------------------------------
require_password = False
password_salt = 'set_me'  # openssl rand -hex 32
password_hash = 'set_me'  # echo -n <my_salt_here><my_pass_here> | sha256sum
