import base64

from flask import Flask, escape, request, render_template
from bandar_bot.Bandar_bot import run_bot
import json
import hashlib
app = Flask(__name__)


@app.route('/animations')
def index():
    return render_template("animations.html")


@app.route("/gif")
def gif():
    user_hash = request.args.get("hash")
    with open("follower.gif", 'rb') as f:
        file = f.read()
        hash = hashlib.sha1(file).hexdigest()
        if user_hash == hash:
            return "", 304

        resp_json = {"image": base64.b64encode(file).decode("utf-8"), "hash": hash}
        return json.dumps(resp_json)


if __name__ == '__main__':
    run_bot()
    app.run(host="0.0.0.0", port=5000, debug=False)
