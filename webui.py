from bottle import route, Bottle, view

app = application = Bottle()

@app.route('/')
@view('index.tpl')
def index():
    return dict(message="HexBet Rankings")
