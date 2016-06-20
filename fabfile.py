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

"""
dependence package in remote server
"""
required_packages = ['wget', 'git']

"""
project config
"""
config = {}
config['api'] = {
    'user': 'fraby',
    'group': 'admin',
    'password': 'fraby',
    'dependences': [],
    'repo_url': 'https://github.com/dungntnew/fabploy.git',
    'deploy_branch': 'master',
    'dev_branch': 'develop',
    'dev_path': '/opt/deploy',
    'app_path': '/opt/deploy/fraby',
    'backup_dir': '/opt/deploy/backup',
    'dir_struct': ('database', 'static', 'virtualenv', 'source'),
    'module_name': 'fraby',
    'site_name': 'localhost',
    'local': {
      'root': '.'
    }
}

# define sets of servers as roles
env.roledefs = {
    'local_dev': ['127.0.0.1:2222']
}
env.user = 'vagrant'
env.password = 'vagrant'


def init_project():
    """
    init python dev env in local
    """
    for k, mconf in config.items():
        with lcd(mconf['local']['root']):
            local('virtualenv ./env')
            local('source ./env/bin/activate')
            local('pip install -U pip')
            local('pip install -r ./requirements.txt')

def tests():
    """
    start test all modules in local
    """
    for k, mconf in config.items():
        test(k)

def test(module='api'):
    """
    start test one model in local
    """
    mconf = config[module]
    with lcd(mconf['local']['root']):
        with settings(warn_only=True):
            result = local('python manage.py test', capture=True)
        if result.failed and not confirm('Test failed. Continue anyway ?'):
           abort('Aborting at user request.')



@roles('local_dev')
def init_server():
    """
    setup remote server - install dependence package
    & setup python env for develop(pip, virtualenv)
    """
    _init_server(config)
    _install_python_env()

@roles('local_dev')
def init_pyenv():
    """
    install python dev env(pip, virtual env)
    (current using python3)
    """
    _install_python_env()

@roles('local_dev')
def init_remote(module='api'):
    """
    setup module in remote server
    (create user, create dir, get latest source code,
    update setting, update virtual env, update static files, etc..)
    """
    mconf = config[module]
    with settings(warn_only=True):
        _create_user(mconf)

    with settings(warn_only=True):
        _create_working_dir(mconf)

    with settings(user=mconf['user'],
                  password=mconf['password'],
                  warn_only=True):
        run('whoami')

        _create_subdir_if_need(mconf)
        _get_latest_src(mconf)
        _update_settings(mconf)
        _update_virtualenv(mconf)
        _update_static_files(mconf)

@roles('local_dev')
def prepare_deploy():
    test()

def _init_server(config):
    """
    update remote servers and install required packages
    """
    sudo('yum update')
    sudo('yum update -y')

    if len(required_packages):
      pkgs = ' '.join(required_packages)
      sudo('yum install -y %s' % pkgs)

    for k, mconf in config.items():
        if len(mconf['dependences']):
            pkgs = ' '.join(mconf['dependences'])
            sudo('yum install -y %s' % pkgs)

def _install_python_env():
    """
    install setup tools and pip
    """
    if not exists('/usr/bin/virtualenv'):
        sudo('curl https://bootstrap.pypa.io/ez_setup.py | python -')
        sudo('curl https://bootstrap.pypa.io/get-pip.py | python -')
        sudo('pip install virtualenv')

def _create_user(mconf):
    """
    create user & group in remote server
    """

    now = datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')

    allow = '%s ALL=(ALL) ALL' % mconf['group']

    backup_dir = '%s/%s' % (mconf['backup_dir'], timestamp)
    sudo('mkdir -p %s' % backup_dir)
    sudo('groupdel %s' % mconf['group'])
    sudo('groupadd %s' % mconf['group'])

    sudo('cp /etc/sudoers %s/sudoers' % backup_dir)
    sudo('sed -i "/%s/p" %s' % (allow, '/etc/sudoers'))
    sudo('echo "%s" >> /etc/sudoers' % allow)

    sudo('userdel -r -f %s' % mconf['user'])
    sudo('adduser -G %s %s' % (mconf['group'], mconf['user']))
    sudo('echo "%s:%s" | chpasswd' % (mconf['user'], mconf['password']))
    sudo('id %s' % mconf['user'])

def _create_working_dir(mconf):
    """
    create working dir for module
    and setting own to group:user
    """
    sudo('mkdir -p %s' % mconf['dev_path'])
    sudo('chown %s:%s %s' % (mconf['user'],
                             mconf['group'],
                             mconf['dev_path']))
    sudo('ls -la %s' % mconf['dev_path'])

def _create_subdir_if_need(mconf):
    run('mkdir -p %s' % mconf['app_path'])
    for subdir in mconf['dir_struct']:
        run('mkdir -p %s/%s' %(mconf['app_path'], subdir))

def _get_latest_src(mconf):
    """
    get lastest source from remote repository
    (checkout repo to src_dir if not exists yet)
    """
    src_dir = '%s/source' % (mconf['app_path'])
    if exists(src_dir + '/.git'):
        run('cd %s && git fetch' % src_dir)
    else:
        run('git clone %s %s' % (mconf['repo_url'], src_dir))

    last_commit = local('git log -n 1 --format=%H', capture=True)
    run('cd %s && git reset --hard %s' % (src_dir, last_commit))

def _update_settings(mconf):
    src_dir = '%s/source' % (mconf['app_path'])
    settings_path = '%s/%s/settings.py' % (src_dir, mconf['module_name'])
    sed(settings_path, 'DEBUG = True', 'DEBUG = False')
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["%s"]' % (mconf['site_name'],)
        )
    secret_key_file = '%s/%s/secret_key.py' % (src_dir, mconf['module_name'])
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(mconf):
    src_dir = '%s/source' % (mconf['app_path'])
    virtualenv_dir = src_dir + '/../virtualenv'
    if not exists(virtualenv_dir + '/bin/pip'):
        run('virtualenv --python=python3 %s' % (virtualenv_dir, ))
    run('%s/bin/pip install -r %s/requirements.txt' % (
                                                       virtualenv_dir,
                                                       src_dir))

def _update_static_files(mconf):
    src_dir = '%s/source' % (mconf['app_path'])
    run('cd %s && ../virtualenv/bin/python3 manage.py collectstatic --noinput' % ( src_dir,
    ))

def _update_database(source_folder):
    src_dir = '%s/source' % (mconf['app_path'])
    run('cd %s && ../virtualenv/bin/python3 manage.py migrate --noinput' % (
        src_dir,
    ))

# ref: http://chimera.labs.oreilly.com/books/1234000000754/ch09.html#_breakdown_of_a_fabric_script_for_our_deployment





