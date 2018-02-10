# HexBet!!!!!!@!!1!!!!1

from bottle import route, Bottle, view

app = application = Bottle()

@app.route('/')
@view('index.tpl')
def index():
    return

@app.route('/run/:runid')
@view('run.tpl')
def run(runid):
    return dict(run_id=runid)
