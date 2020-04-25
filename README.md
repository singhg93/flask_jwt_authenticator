JWT Authentication using flask
==============================

A simple authentication api using flask and jwt web tokens

# Dependencies

- Python 3.5 or higher
- Virtualenv

You can install python from here 
[Python](https://www.python.org/downloads/)

Virtualenv can be installed from
[Virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)


# Installing and running

Clone the repository
```
$ git clone https://github.com/singhg93/flask_jwt_authenticator.git
$ cd flask_jwt_authenticator
```

Now create a virtual environment

```
$ python3 -m venv venv
```

On Windows:

```
py -3 -m venv venv
```

Activate the environment

```
$ . ./venv/bin/activate
```

Install all the requirements

```
$ pip install -r requirements.txt
```

Set some environment variables

```
$ . ./export.sh
```

Set a secret key, you the create a random key by using the following command

```
$ python -c 'import os; print(os.urandom(16))'

# sample output
b'\x87\x86\xa6\x98?\xb0\xcd"\x9e\xa7\x93)\tv)['
```

Set the secret keys for flask and jwt

```
$ export SECRET_KEY=dev # change this to a very long random string
$ export JWT_SECRET_KEY=jwt-dev # change this to a very long random string
```

Run the application

```
$ flask run
```

# Making requests

Registering a user

```
$ curl -H "Content-Type: application/json" -X POST\
  -d '{"username": "testUsername", "password": "testPassword123@"}' \
  http://localhost:5000/auth/register
```

Response: 

```
{
    "message": "User Created",
    "ok": true
}
```

Authenticate

```
$ curl -H "Content-Type: application/json" -X POST\
  -d '{"username": "testUsername", "password": "testPassword123@"}' \
  -c cookies.txt
  -D headers.txt
  http://localhost:5000/auth/login
```

Response: 

```
{
    "login": "true",
    "username": testUsername
}
```

The JWT tokens are sent in http only cookies, and the cookies are saved in
cookies.txt by the curl request.
Dump the contents of the headers file to see all the cookies.

```
$ cat headers.txt

HTTP/1.0 200 OK

Content-Type: application/json

Content-Length: 51

Set-Cookie: access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODc4NDg0NTcsIm5iZiI6MTU4Nzg0ODQ1NywianRpIjoiNjI4N2M4NmYtMmI5MS00ZWI3LTkxNmEtN2UzODUzMTNjMTVjIiwiZXhwIjoxNTg3OTM0ODU3LCJpZGVudGl0eSI6eyJ1c2VybmFtZSI6InRlc3RVc2VybmFtZSJ9LCJmcmVzaCI6dHJ1ZSwidHlwZSI6ImFjY2VzcyIsImNzcmYiOiI1NzRjNjg0MC1mMjY4LTRiNGUtOTQyYS0wNmZmYzg1NjFjOTQifQ.01YxSjdG2b8m8bhF6LLQvaS1nUQEx2QXJ3tBeXxyNYU; HttpOnly; Path=/

Set-Cookie: csrf_access_token=574c6840-f268-4b4e-942a-06ffc8561c94; Path=/

Set-Cookie: refresh_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODc4NDg0NTcsIm5iZiI6MTU4Nzg0ODQ1NywianRpIjoiYWY1MjcwZjQtZDg1Mi00NGEyLThiNmUtM2RmZjc2ZTQ4MzRlIiwiZXhwIjoxNTkwNDQwNDU3LCJpZGVudGl0eSI6eyJ1c2VybmFtZSI6InRlc3RVc2VybmFtZSJ9LCJ0eXBlIjoicmVmcmVzaCIsImNzcmYiOiIyOGM0NzJhZC1mMzI5LTQ1OGQtYWQwMS1iNjhmMDM5MTNlNDIifQ.QHJYM4WICuZgfuskzvshBqutcvIAJKh-trFawJaLh3o; HttpOnly; Path=/auth/refresh

Set-Cookie: csrf_refresh_token=28c472ad-f329-458d-ad01-b68f03913e42; Path=/

Server: Werkzeug/1.0.1 Python/3.8.2

Date: Sat, 25 Apr 2020 21:00:57 GMT

```

Validating the token

To validate the token, jwt and csrf is sent in the request headers as cookies.
To include cookies in the header, the cookies.txt file can be used which was
created when the user logged in.

```
$ curl -b cookies.txt http://localhost:5000/auth/validate_token
```

Response:

```
{
  "is_valid": true,
  "ok": true,
  "user": {
    "username": "testUsername"
  }
}
```
