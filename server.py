from flask import Flask

from routes.auth import auth_bp
from routes.fish import fish_bp
from routes.weather import weather_bp

app = Flask(__name__)

app.register_blueprint(fish_bp, url_prefix="/fish")
app.register_blueprint(weather_bp, url_prefix="/weather")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)