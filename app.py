from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Root Finding Calculator Running 🚀"

if __name__ == '__main__':
    app.run()