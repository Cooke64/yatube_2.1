from app import app
from blog import views
import models
from auth import views
from follow import view
from profile import views

if __name__ == '__main__':
    app.run()
