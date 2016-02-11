#!/bin/sh

rm -f /etc/init.d/skill-tester
ln -s /mnt/src/conf/skill-tester.service /etc/init.d/skill-tester

rm -rf /var/www/skill-tester
ln -s /mnt/src/src /var/www/skill-tester

rm -f /etc/nginx/sites-available/skill-tester
ln -s /mnt/src/conf/nginx_default.conf /etc/nginx/sites-available/skill-tester
ln -s /etc/nginx/sites-available/skill-tester /etc/nginx/sites-enabled/skill-tester
