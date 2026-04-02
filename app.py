from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Root Finding Calculator Running 🚀"

@app.route('/bisection')
def bisection():
    # Example dummy response
    a = request.args.get('a')
    b = request.args.get('b')
    return f"Bisection method called with a={a}, b={b}"