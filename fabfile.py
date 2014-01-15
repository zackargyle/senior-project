from fabric.api import local

local_dir = './'

def refresh():
	local("rm -rf api/migrations")
	local("rm db.sqlite3")
	local("python manage.py schemamigration --initial app")
	local("python manage.py syncdb")
	local("python manage.py migrate")
	local("python manage.py createsuperuser")
	local("python manage.py runserver 8001")

def launch(version="", port=8001):
	local("python%s manage.py runserver %s" % (version, port))

def install(version=""):
	local("pip install south django djangorestframework django-cors-headers")
	local("python%s manage.py syncdb" % version)
	local("python%s manage.py schemamigration --initial app" % version)
	local("python%s manage.py migrate rest_framework.authtoken " % version)
	local("python%s manage.py createsuperuser" % version)

def clean():
    """Remove all the .pyc files"""
    local("find . -name '*.pyc' -print0|xargs -0 rm", capture=False)