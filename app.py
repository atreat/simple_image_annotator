import sys
import os
import imghdr
import csv
import argparse
import json

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file

from lib.annotate import Image, Annotation

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        return redirect(url_for('bye'))
    directory = app.config['IMAGES']
    image = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    print(not_end)
    return render_template('tagger.html', not_end=not_end, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

@app.route('/next')
def next():

    # grab current image and move HEAD to next
    image = Image(app.config["FILES"][app.config["HEAD"]])
    app.config["HEAD"] = app.config["HEAD"] + 1

    # write annotations for image
    for label in app.config["LABELS"]:
        width = float(label["xMax"]) - float(label["xMin"])
        height = float(label["yMax"]) - float(label["yMin"])
        x = round(float(label["xMin"]) + (width / 2))
        y = round(float(label["yMin"]) + (height / 2))

        image.add(Annotation(label["name"], center = (x,y), size = (width, height)))

    app.config["ANNOTATIONS"].append(image)
    app.config["LABELS"] = []

    with open(app.config["OUT"],'w') as f:
        f.write(json.dumps(list(map(Image.dictionary, app.config["ANNOTATIONS"]))))

    return redirect(url_for('tagger'))

@app.route("/bye")
def bye():
    return send_file("taf.gif", mimetype='image/gif')

@app.route('/add/<id>')
def add(id):
    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/image/<path:relpath>')
def images(relpath):
    images = app.config['IMAGES']
    return send_file(images + '/' + relpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='specify the images directory')
    parser.add_argument("--out")
    args = parser.parse_args()
    directory = args.dir
    if directory[len(directory) - 1] != "/":
         directory += "/"
    app.config["IMAGES"] = directory
    app.config["LABELS"] = []
    app.config["ANNOTATIONS"] = []
    files = []
    for dirpath, dirs, filenames in os.walk(app.config["IMAGES"]):
        path = dirpath.split(os.sep)
        for f in filenames:
            fullpath = os.sep.join(path + [f])
            relpath  = os.path.relpath(fullpath, app.config["IMAGES"])
            files += [relpath]

    if not files:
        print("No files")
        exit()
    app.config["FILES"] = files
    app.config["HEAD"] = 0
    if args.out == None:
        app.config["OUT"] = "out.json"
    else:
        app.config["OUT"] = args.out

    print(files)
    app.run(debug="True")
