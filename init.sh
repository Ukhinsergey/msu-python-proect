export APP_NAME_TWITCH_BOT='name'
export BOT_TOKEN='BOT_TOKEN'
export CLIENT_ID='CLIENT_ID'
export CLIENT_SECRET='CLIENT_SECRET'

heroku git:remote -a $APP_NAME_TWITCH_BOT
heroku config:set APP_URL=https://$APP_NAME_TWITCH_BOT.herokuapp.com/
heroku config:set BOT_TOKEN=$BOT_TOKEN
heroku config:set CLIENT_ID=$CLIENT_ID
heroku config:set CLIENT_SECRET=$CLIENT_SECRET
heroku config:set MYLANG=ru_RU.UTF-8
heroku buildpacks:clear
heroku buildpacks:set heroku/python
heroku buildpacks:add --index 2 heroku-community/locale
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
