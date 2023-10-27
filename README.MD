The goal of this project is to develop a comprehensive project template that includes:
- [x] Deployment to a server using Docker containers (completed) :heavy_check_mark:
- [x] SSL (completed...with "www" issue. See note in Step 6) :heavy_check_mark:
  - [ ] Automate certificate renewal (todo: see 
["Handling Renewals"](https://londonappdeveloper.com/django-docker-deployment-with-https-using-letsencrypt/)
at the bottom of the page)
- [x] All deploy settings set via environmental variables (completed) :heavy_check_mark:
- [x] Django with a Hello World home page (completed) :heavy_check_mark:
- [x] Postgres database (completed) :heavy_check_mark:
- [x] Celery (completed) :heavy_check_mark:
- [x] Redis (completed) :heavy_check_mark:

This project template can be cloned from github as a baseline and easily extended to create private projects

Tutorials followed toward this goal
- Deploying Django with Docker Compose
	- video: https://www.youtube.com/watch?v=mScd-Pc_pX0
	- blog: https://londonappdeveloper.com/deploying-django-with-docker-compose/
	- PyCharm project: deploy-django-with-docker-compose
	- github repo: https://github.com/gregcompton/deploy-django-with-docker-compose
- Django Docker Deployment with HTTPS using Letsencrypt
	- video: https://www.youtube.com/watch?v=3_ZJWlf25bY
	- blog: https://londonappdeveloper.com/django-docker-deployment-with-https-using-letsencrypt/
	- PyCharm project: deploy-django-with-LetsEncrypt
	- github repo: https://github.com/gregcompton/deploy-django-with-LetsEncrypt
- Django Celery Docker Playlist by VERY ACADEMY
	- playlist: https://youtube.com/playlist?list=PLOLrQ9Pn6cayGytG1fgUPEsUp3Onol8V7&si=AcASkX2e2hkwZJd6
	- PyCharm project: django_celery_docker_VERYACADEMY
	- github repo: none

As of 10/23/23 I am using a Linode Ubuntu 22.04 LTS jammy server and [gregcompton.com](https://gregcompton.com) domain to test deployment templates.

# HOW TO DEPLOY THIS REPOSITORY

For better instructions, go to the "Create a Server" section of the [London App Developer 
Tutorial](https://anvilproject.org/guides/content/creating-links#creating-links-in-markdown) and follow the instructions.

Requirements
- domain: e.g. gregcompton.com
- server exposed to the internet. SSL cert won't work on a local network.
- server with docker engine and docker compose (google or ask ChatGPT for instructions on how to install these)

## Step 1: Set up your server. 
If you don't know how, this repository is NOT for you :-)

## Step 2: Point your domain to the server (A Record)
This is a good time to point your domain to your server's ip address so that the change has time to propagate. 
I don't believe SSL cert will succeed until DNS propagation is complete (I might be wrong though). 

Note: I am using linode nameservers and deploying to a Linode server, so the process was nearly instantaneous for me. Your mileage may vary. 

## Step3: Clone the repository to your server. 

	sudo git clone https://github.com/gregcompton/django-basePostgres-with-SSL-docker-deployment.git

## Step 4: Setup the environmental variables file
- Go to the directory containing the project files. 

		cd django-basePostgres-with-SSL-docker-deployment
- Create a `.env` file by copying the sample 

        sudo cp .env.sample .env
- Edit the `.env` file and change settings per the project needs  

        sudo nano .env
  - ALLOWED_HOSTS = yourdomain.com,www.yourdomain.com, *any other subdomains* 
    - *Note: All of the ALLOWED_HOSTS should also be included on the ssl certificate. See Step 4b*
    - If you add additional subdomains, you will need to figure out how to handle them in the Django app.
  - SECRET KEY = a jumble of characters. Use keygen for production
  - DOMAIN = yourdomain.com
  - ACME EMAIL = your email address
  - DB -> make these secure for production (for testing I use: dbname, rootuser, supersecretpassword)

  *Note: "ctrl+x" then "y" to save or "n" exit without saving*

*Note: ALLOWED_HOSTS and DOMAIN are used in similar ways. If your deployment is only for yourdomain.com 
and www.yourdomain.com, the deploy.yml and djano settings can be refactored to simplify things*

## Step 4b (optional): Customization

- **IMPORTANT**: In app/docker/certbot/certify-init.sh add any additional domains/subdomains that need to be served. 
  - Keep in mind that www.youdomain.com and domain.com are DIFFERENT DOMAINS. 
  - If you have anything other than yourdomain.com and www.yourdomain.com in ALLOWED_HOSTS, it might be worth looking 
  into refactoring `-d "$DOMAIN" -d www."$DOMAIN" \` to `-d "$ALLOWED_HOSTS"` in order to keep all settings in `.env`
  - See [certbot documentation](https://eff-certbot.readthedocs.io/en/stable/using.html#deleting-certificates) to learn more.


- You might also want to change the default home page as it has my info.
        
        sudo nano app/home/templates/home/index.html

## Step 5: Get the first certificate
This process can take a while the first time...up to 2 minutes in my experience.

	docker compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh

### STOP then START the service so that the application is served via https
      sudo docker compose -f docker-compose.deploy.yml down

then

    sudo docker compose -f docker-compose.deploy.yml up

or add -d to run in the background

    sudo docker compose -f docker-compose.deploy.yml up -d  



  *Note: I like to run services in the foreground until I am sure that they are working*

## Step 5b: Create a database super user
The first time the database service is started (**and every time it is rebuilt**) a superuser will need to be created

	sudo docker compose -f docker-compose.deploy.yml run --rm app sh -c "python manage.py createsuperuser"

*Note: During the previous step, if you did not bring up the service in the background, you will need to either* 
- *stop the service (ctrl-c) OR*
- *open a new terminal instance*

## Step 6: Verify everything is working properly
#### Test the proxy and base Django installation
- You should see the home page at each of the following
  - http://www.yourdomain.com
  - http://yourdomain.com
  - https://www.yourdomain.com
  - https://yourdomain.com
  - any other domains or subdomains that you registered as ALLOWED_HOSTS *AND* on with certbot

#### Test the database
- Go to https://youdomain.com/admin and login using the superuser credentials created earlier.
- Go to the Samples model, upload a file, save, then click the file link to verify that static files are being handled properly

#### Verify Celery tasks are registered
Scroll back through the terminal history. You should see three lines from celery.
```
[tasks]
  . app.celery.test_app_task
  . home.tasks.test_shared_task
```

This means celery is working.

You may need to restart the services if the messages have been deleted from the terminal buffer.

      sudo docker compose -f docker-compose.deploy.yml down

then

    sudo docker compose -f docker-compose.deploy.yml up


## Step 7: Make changes to the app once it is deployed
The whole idea is to use this as a quickstart jumping off point to start developing an app/website/whatever. 
So, as you edit the project, run these commands to update only the app service without bringing down the proxy or 
database services

        sudo docker compose -f docker-compose.deploy.yml build app

then

        sudo docker compose -f docker-compose.deploy.yml up --no-deps app 

or add -d to run in the background

        sudo docker compose -f docker-compose.deploy.yml up --no-deps -d app`

## Step 8: Setup cronjob to automate certificate renewal
*todo: see 
["Handling Renewals"](https://londonappdeveloper.com/django-docker-deployment-with-https-using-letsencrypt/)
at the bottom of the page*


