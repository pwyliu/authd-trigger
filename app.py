from flask import Flask, request, abort, jsonify
import subprocess
from werkzeug.security import check_password_hash
import conf

app = Flask(__name__)
app.debug = False


@app.route('/')
def frontdoor():
    return 'authd-trigger'


@app.route('/api/run/authd', methods=['POST'])
def start_authd():
    # json only:
    if request.headers['Content-Type'] != 'application/json':
        abort(415)

    # password check
    password = request.get_json().get('password', None)
    if conf.require_password:
        if password is None:
            abort(403)
        if not check_password_hash(conf.password_hash, password):
            abort(403)

    # command check
    msg = request.get_json().get('msg', None)
    if msg == u'startauthd':
        try:
            # Check if process is running:
            cmd = '{} -xf "{} -i"'.format(conf.PGREP, conf.AUTHD)
            subprocess.check_call(
                cmd, stdin=None, stdout=None, stderr=None, shell=True)
            return jsonify(status=u'running')
        except subprocess.CalledProcessError as ex:
            if getattr(ex, 'returncode') == 1:
                # Process not running, start it:
                cmd = [conf.TIMEOUT, conf.TIMEOUT_DURATION, conf.AUTHD, '-i']
                subprocess.Popen(
                    cmd, stdin=None, stdout=None, stderr=None, shell=False)
                return jsonify(status=u'started')
            else:
                abort(500)
    else:
        abort(400)


if __name__ == '__main__':
    app.run()