from __future__ import with_statement
from fabric.api import (
  settings,
  abort,
  run,
  sudo,
  get,
  cd,
  local,
  lcd,
  env,
  roles,
  prefix
)
from fabric.contrib.files import append, exists, sed
import random

from fabric.contrib.console import confirm
from datetime import datetime

def init_project():
    local('virtualenv ./env')
    local('source ./env/bin/activate')
    local('pip install -U pip')
    local('pip install -r ./requirements.txt')

def test():
    with settings(warn_only=True):
        result = local('python manage.py test', capture=True)
    if result.failed and not confirm('Test failed. Continue anyway ?'):
       abort('Aborting at user request.')

def commit_u(message):
    local('git add -u')
    local('git status')
    local('git commit -m %s' % message)

def commit_all(message):
    local('git add .')
    local('git status')
    local('git commit -m %s' % message)

def push(branch='develop'):
    local('git push origin %s' % branch)

# define sets of servers as roles
env.roledefs = {
    'local_dev': ['127.0.0.1:2222']
}
env.user = 'vagrant'
env.password = 'vagrant'

config = {}
config['api'] = {
    'user': 'fraby',
    'group': 'admin',
    'password': 'fraby',
    'repo_url': 'https://github.com/dungntnew/fabploy.git',
    'deploy_branch': 'master',
    'dev_branch': 'develop',
    'dev_path': '/opt/deploy',
    'app_path': '/opt/deploy/fraby',
    'backup_dir': '/opt/deploy/backup'
}


@roles('local_dev')
def uptime():
    run('uptime')

@roles('local_dev')
def init_server():
    """
    update the default os with default tools
    """
    sudo('yum update')
    sudo('yum update -y')
    sudo('yum install wget git -y')

@roles('local_dev')
def init_working():
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')
    backup_path = config['api']['backup_dir']
    dev_path = config['api']['dev_path']
    user = config['api']['user']
    group = config['api']['group']
    password = config['api']['password']
    allow = '%s ALL=(ALL) ALL' % group
    print 'start init at %s' % timestamp

    with settings(warn_only=True):
        backup_dir = '/var/backup/%s' % timestamp
        sudo('mkdir -p %s' % backup_dir)
        sudo('groupdel %s' % group)
        sudo('groupadd %s' % group)
        sudo('cp /etc/sudoers %s/sudoers' % backup_dir)
        sudo('sed -i "/%s/p" %s' % (allow, '/etc/sudoers'))
        sudo('echo "%s" >> /etc/sudoers' % allow)
        sudo('userdel -r -f %s' % user)
        sudo('adduser -G %s %s' % (group, user))
        sudo('echo "%s:%s" | chpasswd' % (user, password))
        sudo('id %s' % user)
        sudo('mkdir -p %s' % dev_path)
        sudo('chown %s:%s %s' % (user, group, dev_path))
        sudo('ls -la %s' % dev_path)

@roles('local_dev')
def init_remote():
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')

    user = config['api']['user']
    password = config['api']['password']
    repo_url = config['api']['repo_url']
    dev_path = config['api']['dev_path']
    app_path = config['api']['app_path']

    # with settings(warn_only=True):
    #     run('git clone %s %s' % (repo_url, app_path), user=user)
    with settings(user=user, password=password, warn_only=True):
        run('whoami')

        run('mkdir -p %s' % app_path)
        for subdir in ('database', 'static', 'virtualenv', 'source'):
            run('mkdir -p %s/%s' %(app_path, subdir))

        sorce_dir = '%s/source' % app_path
        if exists(sorce_dir + '/.git'):
            run('cd %s && git fetch' % sorce_dir)
        else:
            run('git clone %s %s' % (repo_url, sorce_dir))

        last_commit = local('git log -n 1 --format=%H', capture=True)
        run('cd %s && git reset --hard %s' % (sorce_dir, last_commit))

@roles('local_dev')
def prepare_deploy():
    test()

# ref: http://chimera.labs.oreilly.com/books/1234000000754/ch09.html#_breakdown_of_a_fabric_script_for_our_deployment





