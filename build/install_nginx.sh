#!/bin/sh

PATTERN="#GENERATED skill-tester"

mkdir -p bin

# Prepare addon
ip="$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' skill-tester)"
cp build/nginx_host.conf bin/nginx_host.conf
sed -i "s/@IP@/$ip/g" bin/nginx_host.conf
sed -i "s/$/ $PATTERN/" bin/nginx_host.conf

# Remore old addon
cp /etc/nginx/sites-available/default bin/default
sed -i "/ $PATTERN/d" bin/default

# Apply
sed -i 's#location / {#location / {\n@BLK@#g' bin/default
sed -i -e '/@BLK@/ {' -e 'r bin/nginx_host.conf' -e 'd' -e '}' bin/default

# Move
sudo mv bin/default /etc/nginx/sites-available/default

# Restart nginx
sudo service nginx reload
