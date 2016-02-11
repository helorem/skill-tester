# Skill Tester

## Description
Skill Tester is an user interface to create question sets, and display them.

Is is a volunteer project and was made for IT HR recruting process at for CapFi Tech.

## Requirement
This project was optimized for Nginx. It could run with another WebServer, but not the deploy system.

Morover, you should have a "default" site enabled.

The container system is based on Docker.
```bash
sudo apt-get install docker.io
```

## Default configuration
A default user is created : 

username : admin

pwd : admin

DO NOT FORGET TO DELETE IT !

## Usage

### make deb
Create de .deb file of the project.

### make deploy
Create a Docker image of the project, ready to production. it will create and use the DEB file.

### make run
Run the Docker container, ready to production

### make install_nginx
Modify the default site of Nginx to add a redirection to the container

### make deploy-all
Deploy, run and install Nginx conf

### make deploy-dev
Create a Docker image of the project for dev purpose. The source folder is mounted into the container

### make run-dev
Run the Docker container for dev purpose

### make deploy-dev-all
Deploy and run in dev mode, then install Nginx conf
