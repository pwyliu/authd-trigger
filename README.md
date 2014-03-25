# authd-trigger
[ossec-authd](http://ossec-docs.readthedocs.org/en/latest/programs/ossec-authd.html) is useful, but you can't leave it running all the time because
it eats a ton of CPU and has no authentication or authorization. This poses a
challenge for automating agent registration.

Authd-trigger solves this problem in a super dumb way. It lets you remotely start
`ossec-authd` by making an HTTP POST to an api endpoint. After a set amount of
time (by default 15 minutes) the authd process is shut down. You can optionally
set up a password so only authorized clients can start the daemon.

## Dependencies
* Python 2.7+
* pgrep, ossec-authd and timeout

## Installation
It's just a [Flask](http://flask.pocoo.org/) application. Clone the repo, install the requirements,
and proxy behind nginx or apache. This needs to run on the same server as OSSEC
so python can access the authd binary.

Use a virtualenv if you don't want to mess up your system Python.

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
unauthorized clients from starting it.

The plaintext password is not stored in `conf.py`. That would be silly. Rather,
`conf.py` stores a salt and the sha256 hash of the password. If you enable
`require_password`, you must set both a salt and a hash.

The salt should be a 64 byte string that is hex encoded. The hash is the
sha256 hash of the salt + the desired password. You can generate both in bash
like this:

```bash
~$ openssl rand -hex 32
4d2dc590d18d3d870a75f7dc2726a90235c78f0c14f9353fdf9367282ca1bf7a

# if your desired password was "Pants"
~$ echo -n 4d2dc590d18d3d870a75f7dc2726a90235c78f0c14f9353fdf9367282ca1bf7aPants | sha256sum
f66ba89ff80cb8c654b714a461e304fae92b12e2baf0ab5be53aa66211998abb  -
```

### ossec-authd permissions
The webapp should run as a user in the ossec group, or the group that owns
`ossec-authd`. In order to launch it as a non root user, the binary needs to
have the setuid permission on it.

```bash
~$ chmod 0455 /var/ossec/bin/ossec-authd
```

This kind of sucks but it seems `ossec-authd` will not start without it. If you can
find a better way please let me know.

## Making API calls.
There's only one API endpoint: `/api/run/authd`. You have to post
`msg: startauthd` and the password if enabled. That's the only two things the
server is looking for.

```json
{
  msg: startauthd
  password: mypassword
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
  $authd_json        = '{"msg": "startauthd", "password": "Sekrit"}'

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