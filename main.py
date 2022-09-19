import requests, time, os, json, threading
from flask import Flask

mainFile = "commits"
githubAccount = "the-red-eye-studio"
accountName = "Redeye"

Github_token = "noTokenForUbozo"

threshold = 1210000 # ~ 2 weeks


def returnHTML(text, color):
    if color == "red":
        color = "252, 3, 23"
    elif color == "green":
        color = "54, 153, 8"
    return """<!DOCTYPE html><html><style>.container{margin: 0; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family:'Courier New'; font-size: 450%; color: rgb(""" + color + """);}@keyframes cursor-blink{0%{opacity: 0;}}.container::after{content: "|"; animation: cursor-blink 1.5s steps(2) infinite;}</style> <body style="background-color:#2c353d"><div class="container"><a>""" + text + """</a></div><div class="bottom_link"><a href="https://github.com/the-red-eye-studio/am-I-alive" style="position: fixed; left: 50%; bottom: 20px; transform: translate(-50%, -50%); margin: 0 auto; color:#5f6061; text-decoration: none; font-family:'Courier New';">Source code</a></div></body></html>"""


if not os.path.exists(mainFile):
    with open(mainFile, 'w') as f:
        f.write(json.dumps([requests.get("https://api.github.com/users/" + githubAccount + "/events/public", auth=(Github_token, "x")).json()[0]["id"], int(time.time())]))
        time.sleep(7)

def worker():
    while True:
        with open(mainFile, 'r') as f:
            lastCommit = json.loads(f.read())

        try:
            _latestCommit = requests.get("https://api.github.com/users/" + githubAccount + "/events/public", auth=(Github_token, "x")).json()[0]["id"]
        except:
            _latestCommit = lastCommit[0]
            time.sleep(120)

        if not lastCommit[0] == _latestCommit:
            with open(mainFile, 'w') as f:
                f.write(json.dumps([_latestCommit, int(time.time())]))
            print("New commit")

        time.sleep(20)


threading.Thread(target=worker).start()

app = Flask(__name__)

@app.route("/")
def hello_world():
    with open(mainFile, 'r') as f:
        lastCommit = json.loads(f.read())
    
    if time.time() - lastCommit[1] > threshold:
        return returnHTML(accountName + " is dead, he hasn't commited in " + str(round((time.time() - lastCommit[1])/ 24 / 60 / 60, 2)) + " days ;-;", "red")
    else:
        return returnHTML(accountName + " is alive, he commited " + str(round((time.time() - lastCommit[1])/ 24 / 60 / 60, 2)) + " days ago :)", "green")


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5978)

