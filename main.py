#!/usr/bin/env python
import sys, pymongo, socket

from flask import Flask, render_template, request, redirect
from datetime import datetime

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

#urls_list = []
db = None
urls_collection = None

def connect_to_db():
    global db, urls_collection
    if db is None :
        connection_string = "mongodb://localhost"
        connection = pymongo.Connection(connection_string, safe=True)
        db = connection.urlz
        urls_collection = db.urlz

connect_to_db()

@app.route("/")
def index():
    connect_to_db()
    urls_list = urls_collection.find().sort("url_id", pymongo.DESCENDING).limit(100);
    return render_template('index.html', urls=urls_list, show_all_urls_btn=True)

@app.route("/all")
def index_all():
    connect_to_db()
    urls_list = urls_collection.find().sort("url_id", pymongo.DESCENDING);
    return render_template('index.html', urls=urls_list)

@app.route("/<url_id>")
def handle_url_id(url_id=None):
    try:
        url_id = int(url_id)
    except:
        return redirect('/')

    connect_to_db()
    url = urls_collection.find_one({'url_id' : url_id})

    if url:
        #Increase the number of clicks and the date of last access
        if ("clicks_count" not in url):
            url["clicks_count"] = 0
        url["clicks_count"] = url['clicks_count'] + 1
        url['date_last_access'] = datetime.utcnow()
        urls_collection.save(url)
        return redirect(str(url['url']))

    return redirect("/")

@app.route("/add", methods=['POST'])
def add():
    data = {'url': request.form.get('url')}
    #calculate the next numeric url_id
    #MongoDB hasn't decimal autoincrement indexes in contrast to the MySQL
    #To calculate a unique numerical value using the following atomic "findandmodify" operator
    if (len(data['url']) > 0) :
        connect_to_db()

        next_url_id = db.command("findAndModify",
                    "counters",
                    query = {"_id" : "url_id"},
                    update = {"$inc" : {"seq" : 1}},
                    new = True,
                    upsert = True
                )['value']['seq']
        data['url_id'] = int(next_url_id)
        data['date_creation'] = datetime.utcnow()
        data['ip'] = request.remote_addr
        urls_collection.save(data)
    return redirect('/')

@app.template_filter('timesince')
def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3031)

# vim: sts=4:ts=4:sw=4
