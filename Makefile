PWD=/home/helorem/tmp/deb

deb: clean
	mkdir -p bin/skill-tester
	cp -r build/DEBIAN bin/skill-tester/DEBIAN
	mkdir -p bin/skill-tester/etc/init.d/
	cp conf/skill-tester.service bin/skill-tester/etc/init.d/skill-tester
	mkdir -p bin/skill-tester/etc/nginx/sites-available/
	cp conf/nginx_default.conf bin/skill-tester/etc/nginx/sites-available/skill-tester
	mkdir -p bin/skill-tester/var/www/skill-tester/
	cp -r src/* bin/skill-tester/var/www/skill-tester/
	mkdir -p bin/skill-tester/usr/bin/
	mv bin/skill-tester/var/www/skill-tester/api/skill_tester.sh bin/skill-tester/usr/bin/
	dpkg-deb --build bin/skill-tester bin/skill-tester.deb

clean:
	rm -rf bin

deploy: deb
	cp build/Dockerfile.deploy bin/Dockerfile
	docker build -t skill-tester bin

run:
	docker stop skill-tester | exit 0
	docker rm skill-tester | exit 0
	docker run -dit --name=skill-tester --expose=80 skill-tester
	docker exec -ti skill-tester service skill-tester start
	docker exec -ti skill-tester service nginx start

deploy-dev:
	cp build/Dockerfile.dev bin/Dockerfile
	docker build -t skill-tester bin

run-dev:
	docker stop skill-tester | exit 0
	docker rm skill-tester | exit 0
	docker run -dit --name=skill-tester -v "$(PWD)":"/mnt/src" --expose=80 skill-tester
	docker exec -ti skill-tester /mnt/src/build/install_dev.sh
	docker exec -ti skill-tester service skill-tester start
	docker exec -ti skill-tester service nginx start

exec:
	docker exec -ti skill-tester bash -l

install_nginx:
	build/install_nginx.sh

deploy-all: deploy run install_nginx

deploy-dev-all: deploy-dev run-dev install_nginx
