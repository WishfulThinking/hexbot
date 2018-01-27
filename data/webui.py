from bottle import route, Bottle

app = application = Bottle()

@app.route('/hello')
def root():
    return "Hello dude"
