#!/bin/sh

INSTALL_LOG=/var/log/uwsgi/bdyunlicense_install.log

if [ -h "/etc/nginx/sites-enabled/bdyunlicense_nginx.conf" ];then
    rm "/etc/nginx/sites-enabled/bdyunlicense_nginx.conf"
fi
ln -s ./bdlicense_nginx.conf /etc/nginx/sites-enabled/bdlicense_nginx.conf

db_name=$(mysql -uroot -pbdyun -e "show databases" 2>>$INSTALL_LOG  | grep bdlicense)
if [ "$db_name" != "license" ];then
    mysql -uroot -pbdyun -e "create database bdlicense character set utf8 collate utf8_general_ci"
    echo "add database 'license' successful ..."
fi
