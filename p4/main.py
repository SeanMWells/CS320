# project: p4
# submitter: Smwells3
# partner: none
# hours: 12

#I got my data by searching for trending covid-related datasets on Kaggle. I think an interesting graph that I could use from this data would be comparing infection rate (# of infected / population or # tested) and population density. I'd probably expect this number to increase as population density increases but it'd be interesting to graph nonetheless. 

import pandas as pd
from flask import Flask, request, jsonify, Response
import re, matplotlib
from matplotlib import pyplot as plt
from io import BytesIO

matplotlib.use('Agg')

app = Flask(__name__)
df = pd.read_csv("main.csv")
df_html = pd.DataFrame.to_html(df)
visited = 0
click_stats = {"a": 0, "b": 0}

@app.route('/')
def home():
    global visited
    with open("index.html") as f:
            html = f.read()
    while visited < 10:
        if (visited % 2) == 0:
            visited += 1
            return html
        visited += 1
        return html.replace("<a href=\"donate.html?from=a\">Donate</a>\n", "<a href=\"donate.html?from=b\" style=\"color:red;\">Donate</a>\n")
    while visited >= 10:
        if click_stats["a"] > click_stats["b"]:
            return html
        return html.replace("<a href=\"donate.html?from=a\">Donate</a>\n", "<a href=\"donate.html?from=b\" style=\"color:red;\">Donate</a>\n")

@app.route('/browse.html')
def browse():
    return(f"<html><body><h1>Browse</h1></body>{df_html}<html>")

@app.route('/donate.html')
def donate():
    if request.args.get("from"):
        click_stats[request.args.get("from")] += 1
    with open("donate.html") as f:
        html = f.read()
    return html

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if re.match(r"\w*@\w*\.\w*", email): # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        with open("emails.txt", "r") as f:
            n = len(f.read().split())
        return jsonify("thanks, you're subscriber number {}!".format(n))
    return jsonify("Invalid email format entered, please try again (ex. johnsmith@email.com)") # 3

@app.route("/dashboard_1.svg")
def plot():
    c = None
    fig, ax = plt.subplots()
    x_axis = pd.Series((df["Infected"]/df["Population"]))
    y_axis = pd.Series((df["Deaths"]/df["Infected"]))
    if request.args.get("cmap"):
        c = pd.Series(df[request.args.get("cmap")])
    plt.scatter(x_axis, y_axis, c=c)
    if request.args.get("cmap"):
        plt.colorbar(label=request.args.get("cmap"))
    ax.set_xlabel("% Infected")
    ax.set_ylabel("% that Died")
    ax.set_title("Percent of states population infected vs percent of deaths as a result of Covid")
    plt.tight_layout()
    f = BytesIO()
    fig.savefig(f, format="svg")
    plt.close(fig)
    return Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route("/dashboard_2.svg")
def plot_2():
    fig, ax = plt.subplots()
    plt.hist(df["Flu Deaths"])
    ax.set_xlabel("Flu deaths per 100,000 people")
    ax.set_ylabel("Number of states")
    ax.set_title("Frequency of flu deaths per state")
    plt.tight_layout()
    f = BytesIO()
    fig.savefig(f, format="svg")
    plt.close(fig)
    return Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.