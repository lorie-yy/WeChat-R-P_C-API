#!/bin/sh

INSTALL_LOG=/var/log/uwsgi/bdyunlicense_install.log

if [ -h "/etc/nginx/sites-enabled/bdyunlicense_nginx.conf" ];then
    rm "/etc/nginx/sites-enabled/bdyunlicense_nginx.conf"
fi
ln -s ./bdyunlicense_nginx.conf /etc/nginx/sites-enabled/bdyunlicense_nginx.conf

db_name=$(mysql -uroot -pbdyun -e "show databases" 2>>$INSTALL_LOG  | grep license)
if [ "$db_name" != "license" ];then
    mysql -uroot -pbdyun -e "create database license character set utf8 collate utf8_unicode_ci"
    echo "add database 'license' successful ..."
fi
