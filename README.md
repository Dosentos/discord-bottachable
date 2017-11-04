# Discord-Bottachable

Discord bot that gathers all links shared in the specified channel and posts them to website

## Bot features

### Discord commands for standard user
- !link
  - Purpose: Saves a link to the database and publishes it on the website
  - Syntax: `!link [url] tags: [your,tags] title: [your title]`
  - Example: `!link https://discord-bottachable.herokuapp.com tags: discord, bottachable, bot, amazing, cool, attachment title: The front page of Discord-bottachable`
  - `[url]` &mdash; __required__
  - `tags: your, tags` &mdash; __optional__
  - `title: Your Title` &mdash; __optional__

- !test
  - Purpose: Tells you how many messages have you written among 100 last messages in current channel (discord.py example bot feature)
  - Syntax: `!test`
  - Example: `!test`

- !sleep
  - Purpose: waits five seconds and prints you response
  - Syntax:  `!sleep`
  - Example: `!sleep`

### Discord commands for admins
- !admin_dump_users
  - prints all users in DB to console
- !admin_dump_links
  - prints all links in DB to console
- !admin_dump_tags
  - prints all tags in DB to console

- !admin_delete_all_users
  - deletes all users in DB
- !admin_delete_all_links
  - deletes all links in DB
- !admin_delete_all_tags
  - deletes all tags in DB

## Instructions for development
- When you pull new code, run `pip install -r requirements.txt` if there's new requirements added to project
- If you install more PIP packages, remember to run `pip freeze > requirements.txt` to save them in requirements
- If you add more settings in `local_settings.py`, remember to **update local settings example in readme**
- In the project folder root you can start venv directly with `.\..\venv\scripts\activate` (powershell)

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

        # Discord authentication stuff (add your token here)
        DISCORD_BOT_TOKEN = ''

        # As default sentry is disabled in debug mode so sentry key can be empty string
        SENTRY_KEY = ''

        RAVEN_CONFIG = {}
        ```

### Setting up mock data for UI
1. Delete `db.sqlite3` and everything else in `discord_bottachable/migrations/` except `__init__.py`
2. Migrate
    - `python manage.py showmigrations`
    - `python manage.py makemigrations`
    - `python manage.py migrate`
3. Load mock data
    - `python manage.py loaddata users.json`
    - `python manage.py loaddata tags.json`
    - `python manage.py loaddata servers.json`
    - `python manage.py loaddata links.json`
    > Note: Make sure `models.py` contains all the fields

4. Run server
    > Note: If you need to use print for debugging, say, views.py then use `python manage.py runserver`
