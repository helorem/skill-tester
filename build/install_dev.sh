#!/bin/sh

rm -f /etc/init.d/skill-tester
ln -s /mnt/src/conf/skill-tester.service /etc/init.d/skill-tester

rm -f /usr/bin/skill_tester.sh
ln -s /mnt/src/src/api/skill_tester.sh /usr/bin/skill_tester.sh

rm -rf /var/www/skill-tester
ln -s /mnt/src/src /var/www/skill-tester

rm -f /etc/nginx/sites-available/skill-tester
ln -s /mnt/src/conf/nginx_default.conf /etc/nginx/sites-available/skill-tester
ln -s /etc/nginx/sites-available/skill-tester /etc/nginx/sites-enabled/skill-tester

sqlite3 /var/www/skill-tester/api/skill_tester.db < /var/www/skill-tester/api/skill_tester.sql
chown -R www-data:www-data /var/www/skill-tester/api

