from bottle import route, run

@route('/')
def root():
    return "Hello"

run(host='localhost', port=8080, debug=False)
