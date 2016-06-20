# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "bento/centos-6.7"

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "off", "--cpus", "4"]
    vb.customize ["modifyvm", :id, "--memory", "2048"]
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end

  config.vm.box_check_update = true
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.synced_folder ".", "/home/vagrant/develop", type: "nfs"

  $script =<<-EOF
    yum update -y
    yum install openssl* python-devel libselinux-python -y
    cd /usr/local/src
    wget https://bootstrap.pypa.io/ez_setup.py
    python ez_setup.py
    easy_install pip
    pip install ansible
  EOF

  config.vm.provision "shell", inline: $script

end
