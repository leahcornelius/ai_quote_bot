from instabot import Bot
import requests
from datetime import datetime
from time import sleep
import random
import shutil
import json
bot = Bot()
uname = ""
psword = ""
hashtags = "#bhfyp #motivation #life #inspiration #funny #comment #positivevibes #motivationalquotes #share #sad #lovequotes #mentalhealth #poetry #live #inspirationalquotes #vibes #quoteoftheday #lifequotes #writer #god #quote #positivity #2 #quotestagram #feelings #thoughts #tarot #motivational #dream #heart"
first = True


def login(username, password):
    global bot
    bot.login(username=username, password=password)

def get_login():
    global psword, uname
    # read login from json
    with open("login.json", "r") as f:
        data = json.load(f)
        psword = data["password"]
        uname = data["username"]


def save_img(url, fn):
    # save the image from the url
    img_data = requests.get(url).content
    with open(fn, 'wb') as handler:
        handler.write(img_data)


def upload(path, caption):
    global bot
    bot.upload_photo(path, caption=caption)


def generate_quote():
    # get a quote from https://inspirobot.me/api?generate=true
    return requests.get('https://inspirobot.me/api?generate=true').text


def watch_stories(user_to_get_likers_of):
    global bot
    current_user_id = user_to_get_likers_of

    try:
        # GET USER FEED
        if not bot.api.get_user_feed(current_user_id):
            bot.logger.error("Can't get feed of user_id=%s" % current_user_id)

        # GET MEDIA LIKERS
        user_media = random.choice(bot.api.last_json["items"])
        if not bot.api.get_media_likers(media_id=user_media["pk"]):
            bot.logger.info(
                "Can't get media likers of media_id='%s' by user_id='%s'"
                % (user_media["id"], current_user_id)
            )

        likers = bot.api.last_json["users"]
        liker_ids = [
            str(u["pk"])
            for u in likers
            if not u["is_private"] and "latest_reel_media" in u
        ][:20]

        # WATCH USERS STORIES
        if bot.watch_users_reels(liker_ids):
            bot.logger.info("Total stories viewed: %d" %
                            bot.total["stories_viewed"])

        # CHOOSE RANDOM LIKER TO GRAB HIS LIKERS AND REPEAT
        current_user_id = random.choice(liker_ids)

        if random.random() < 0.05:
            current_user_id = user_to_get_likers_of
            bot.logger.info(
                "Sleeping and returning back to original user_id=%s" % current_user_id
            )
            sleep(90 * random.random() + 60)

    except Exception as e:
        # If something went wrong - sleep long and start again
        bot.logger.info(e)
        current_user_id = user_to_get_likers_of
        sleep(240 * random.random() + 60)
    bot.logger.info("Finished watching stories")


def main():
    get_login()
    shutil.rmtree("config", True)

    global psword, bot, first
    try:
        login(uname, psword)

    except Exception as e:
        bot.logger.info("Failed to login: " + str(e))
    while True:
        try:
            if (first == False):
                img_path = "img/" + str(datetime.now()) + '.jpg'
                save_img(generate_quote(), img_path)
                upload(img_path, "What do you think? Tell us in the comments 🤔\nIf you came here from a hashtag, consider giving us a like and follow for more quotes!\n" + hashtags)
                sleep(60)
            first = False
            watch_stories("44573319962")
            # sleep between 4 hours and 24 hours
            sleep(60 * 60 * random.randint(4, 24))
        except Exception as e:
            bot.logger.info("Encountered error: " + str(e))
            # try relogging if error
            try:
                shutil.rmtree("config")
                login(uname, psword)
            except Exception as e:
                bot.logger.info("Failed to relogin: " + str(e))

        sleep(60 * random.randint(0, 10))


main()
