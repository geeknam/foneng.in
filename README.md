push-sms
========

Installation
--------------
``` bash
$ mkvirtualenv push-sms --no-site-packages
$ export PATH=${PATH}:/path/to/google_appengine
$ export PYTHONPATH=/path/to/google_appengine
```

Run tests
--------------
``` bash
$ pip install nosegae
$ pip install rednose
$ pip install webtest
$ pip install coverage

$ nosetests -v --with-gae --rednose --with-coverage --cover-html --cover-package=gae
```

