from flask import Flask, render_template
import glob
from datetime import datetime
import locale
from searchbot import searchbot
import os
import pytz

timezone = pytz.timezone('America/Los_Angeles')
month = datetime.now(timezone).month
day = datetime.now(timezone).day

app = Flask(__name__, template_folder='templates')
year = os.environ.get("YEAR")
semester = os.environ.get('SEMESTER')

def refresh():
    preview = searchbot(year=year, term=semester)
    preview.saveHtml('preview.html')
    f = open('templates/date' + '_' + str(month) + '_' + str(day), "w")
    f.close()
    del preview, f

def getfile():
    try:
        return glob.glob('templates/date*')[-1]
    except IndexError:
        refresh()
        return glob.glob('templates/date*')[-1] 

def isnewest(month_, day_):
    if int(month_) >= int(month) and int(day_) >= int(day):
        return True
    else:
        return False

@app.route('/')
def index():
    filename = getfile()
    header = semester + ' ' + year
    if not isnewest(filename.split('_')[1], filename.split('_')[2]):
        os.remove(os.path.dirname(os.path.abspath(__file__)) + '/' + filename)
        refresh()
        filename = getfile()
    return render_template('index.html', title="PCC - " + header, header=header)

@app.route('/about')
def about():
    return render_template('about.html', title="PCC - About", header='About')

@app.route('/preview.html')
def preview():
    return render_template('preview.html')

if __name__ == "__main__":
    refresh()
    app.run()
