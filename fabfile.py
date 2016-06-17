from fabric.api import local

def init_project():
    local('virtualenv ./env')
    local('source ./env/bin/activate')
    local('pip install -U pip')
    local('pip install -r ./requirements.txt')

def prepare_deploy():
    local('python manage.py test')
    local('git add .')
    local('git status')
    local('git commit')
