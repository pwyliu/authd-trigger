# authd-trigger
[ossec-authd](http://ossec-docs.readthedocs.org/en/latest/programs/ossec-authd.html) is useful, but you can't leave it running all the time because
it eats a ton of CPU and has no authentication. This poses a challenge for
automating agent registration.

Authd-trigger solves this problem in a super dumb way. It lets you remotely start
`ossec-authd` by making an HTTP POST to an api. After a set amount of
time (by default 15 minutes) the authd process is shut down automatically. You
can optionally set up a password so only authorized clients can start the daemon.

## Dependencies
* Python 2.7+
* pgrep, ossec-authd and timeout

## Installation
It's just a Flask application. Clone the repo, install the requirements, and
proxy behind nginx or apache. This app needs to run on the same server as OSSEC
so python can access the authd binary.

Use a virtualenv if you don't want to mess up your system python.

```bash
git clone git@github.com:pwyliu/authd-trigger.git
cd authd-trigger
pip install -r requirements.txt

# start with built in web server (for dev)
python app.py
# start with gunicorn (for real life)
gunicorn -b 127.0.0.1:$PORT -w 2 --user=$USER --group=$GROUP --log-level=$LOGLEVEL app:run
```

See the [Flask documentation](http://flask.pocoo.org/docs/deploying/) for instructions on how to proxy the app. There are
sample nginx and upstart confs in the support folder.

## Configuration
There are two things configure:

* `conf.py`
* Permissions on the `ossec-authd` binary

### Conf.py
Edit `conf.py` to set paths to the needed binaries. If you don't know where a
program is, run `which <program_name>`.

#### Setting a password
You can set up a password that clients must send in their json post to
start authd. This doesn't secure `ossec-authd` in any way, it just prevents
unauthorized clients from starting it through `authd-trigger`.

To enable using a password, first generate a hash of your desired pass with the
included `generate_hash.py` script. Then edit `conf.py` to set
`require_password = True` and `password_hash=<your hash>`.

```bash
# copy/paste the output into conf.py
# remember this will go in your bash history, so do it somewhere you can erase it.

~$ ./generate_hash.py mypassword
pbkdf2:sha256:5000$UT5uzxt4rgK2fkXA$99ef4a7e9f7b407ad01378701ab6c5802d63507ab43b26c56be5aa81a3e02cd6
```

`generate_hash.py` creates a PBKDF2 + HMAC derived key. The hash function is
sha256 with 5000 iterations. You can tweak this if you like. See the [Werkzeug](http://werkzeug.pocoo.org/docs/utils/)
documentation for more details.

### Ossec-authd permissions
The webapp should run as a user in the ossec group, or the group that owns
`ossec-authd`. In order to launch it as a non root user, the binary needs to
have the setuid permission on it.

```bash
~$ chmod 0455 /var/ossec/bin/ossec-authd
```

This kind of sucks but it seems `ossec-authd` will not start without it. If you can
find a better way please let me know.

## Making API calls
There's only one API endpoint: `/api/run/authd`. You have to post
`msg: startauthd` and the password if enabled. That's the only two things the
server is looking for.

```javascript
{
  "msg": "startauthd"
  "password": "mypassword"
}
```

The server responds with `status: started` or `status: running`

### Examples
With curl:

```bash
~$ curl https://server:port/api/run/authd \
-X POST \
-H "Content-type:application/json" \
-d '{"msg": "startauthd", "password": "Sekrit"}'
```

With a puppet manifest:
```puppet

  $ossec_server      = '<server>'
  $ossec_server_ip   = '<server_ip>'
  $authd_port        = '<port>'
  $authd_endpoint    = '/api/run/authd'
  $authd_url         = "https://${ossec_server}:${authd_port}${authd_endpoint}"
  $authd_password    = hiera('encrypted-password')
  $authd_json        = "{\"msg\":\"startauthd\",\"password\":\"${authd_password}\"}"

  $authd_triggercmd  = "curl ${authd_url} -X POST -H 'content-type:application/json' -d '${authd_json}'"
  $authd_cmd         = "${authd_triggercmd} && sleep 5 && bin/agent-auth -m ${ossec_server_ip}"

  exec { 'ossec_register':
    cwd     => $working_dir,
    command => $authd_cmd,
    creates => "${working_dir}/etc/client.keys",
  }
```

## Contributors
You're welcome to submit any pull request, please help me make this better.

## License
The MIT License (MIT)

Copyright (c) 2014 Paul Liu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.