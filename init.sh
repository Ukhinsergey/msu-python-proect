heroku git:remote -a 'app_name'
heroku config:set APP_URL https://'app_name'.herokuapp.com/
heroku config:set BOT_TOKEN 'Bot token'
heroku config:set CLIENT_ID 'twitch app id'
heroku config:set CLIENT_SECRET 'twitch secret'
heroku config:set MYLANG ru_RU.UTF-8
heroku buildpacks:clear
heroku buildpacks:set heroku/python
heroku buildpacks:add --index 2 heroku-community/locale
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
