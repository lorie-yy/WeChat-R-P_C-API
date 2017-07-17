#!/bin/bash

apt-get update

echo "=====================install deb packages====================="
sfts=("openssh-server" "nginx" "python-dev"  "uwsgi" "uwsgi-plugin-python" "libpcre3" "libpcre3-dev" "python-mysqldb" "python-setuptools" "libmysqld-dev")

for soft_name in ${sfts[@]}
do
    echo "install ${soft_name} ..."

    apt-get install -y ${soft_name}

    if [[ $? -eq 0 ]];then
	echo "install ${soft_name} successful!"
    else
	echo "install ${soft_name} failure!"
    fi
done

echo "install pip ..."
easy_install pip
if [[ $? -eq 0 ]];then
    echo "install pip successful!"
else
    echo "install pip failure!"
fi

echo "install Django-1.8.3 ..."
pip --default-timeout=6000 install Django==1.8.3 -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
if [[ $? -eq 0 ]];then
    echo "install Django-1.8.3 successful!"
else
    echo "install Django-1.8.3 failure!"
fi


echo "=====================mysql install and config====================="
echo "mysql install ..."
DEBIAN_FRONTEND=noninteractive apt install -y mysql-server
if [[ $? -eq 0 ]];then
	echo "install mysql-server successful!"
    else
	echo "install mysql-server failure!"
    fi

set_passwd="UPDATE user SET password=password('bdyun') WHERE user='root';FLUSH PRIVILEGES;"
mysql -uroot "mysql" -e"${set_passwd}"

echo "config my.cnf"
if [ ! -f "/etc/mysql/my.cnf" ];then
    mv "/etc/mysql/my.cnf" "/etc/mysql/my_old.cnf"
fi

cp "./my.cnf" "/etc/mysql/my.cnf"

/etc/init.d/mysql restart

mysql -uroot -pbdyun -e "show variables like 'collation_%'"
mysql -uroot -pbdyun -e "show variables like 'character_set_%'"
mysql -uroot -pbdyun -e "create database radius character set utf8 collate utf8_unicode_ci"
echo "mysql config finised"