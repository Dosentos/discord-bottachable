# Discord-Bottachable

Discord bot that gathers all links shared in the specified channel and posts them to website

## Instructions for development
- When you pull new code, run `pip install -r requirements.txt` if there's new requirements added to project
- If you install more PIP packages, remember to run `pip freeze > requirements.txt` to save them in requirements
- If you add more settings in `local_settings.py`, remember to **update local settings example in readme**




## Instructions for setting up development environment

- Install python 3.6.2 (anywhere u like)
- Create a folder for the project
- Go inside the folder you just made
- Run `virtualenv venv` (With virtualenv you can do clean environment and not pollute your entire pc)
- Run `source venv/Scripts/activate` or `venv\Scripts\activate.bat` if you're on Windows
  - Note that this only works on cmd, not for example in git bash
  - IF you are using Windows powershell use command `.\\venv\scripts\activate`
  - In your CL you should now have `(venv) λ` prefix
  - *Remember to activate venv every time you start coding*
- Clone the repository from github
- Run `cd discord-bottachable`
- Run `pip install -r requirements.txt`
- To start local development use `heroku local web` or `heroku local web -f Procfile.windows` if you're on Windows
- You can now access your site on `localhost:5000`
- Set up local_settings.py file
    - Inside the file you should write (verify from buddy that this is the latests version)
    - Save the file in the project root directory.
        ```python
        # SECURITY WARNING: keep the secret key used in production secret!
        SECRET_KEY = ""

        # Whether or not you should see proper error messages on the site when error happens
        DEBUG = True

        # Discord authentication stuff
        DISCORD_BOT_TOKEN = = ''
        ```







If you want to run the bot locally which is recommended, you should run 
- TO BE CONTINUED
- TODO: install clean working environment locally. (NGROK?)

# Heroku starter Template

An utterly fantastic project starter template for Django 1.11.

## Features

- Production-ready configuration for Static Files, Database Settings, Gunicorn, etc.
- Enhancements to Django's static file serving functionality via WhiteNoise.
- Latest Python 3.6 runtime environment. 

## How to Use

To use this project, follow these steps:

1. Create your working environment.
2. Install Django (`$ pip install django`)
3. Create a new project using this template

## Creating Your Project

Using this template to create a new Django app is easy::

    $ django-admin.py startproject --template=https://github.com/heroku/heroku-django-template/archive/master.zip --name=Procfile helloworld

(If this doesn't work on windows, replace `django-admin.py` with `django-admin`)

You can replace ``helloworld`` with your desired project name.

## Deployment to Heroku
- After making changes to models.py and pushing to heroku, you have to run command `heroku run python manage.py migrate`

## License: MIT

## Further Reading

- [Gunicorn](https://warehouse.python.org/project/gunicorn/)
- [WhiteNoise](https://warehouse.python.org/project/whitenoise/)
- [dj-database-url](https://warehouse.python.org/project/dj-database-url/)
