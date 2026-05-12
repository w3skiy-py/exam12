import flask 
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwerty@127.0.0.1:5432/examflask'
db = SQLAlchemy(app)

# Таблички с БД

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    message = db.Column(db.Text)
    course = db.relationship('Course')
    review = db.relationship('Review', backref='application', uselist=False)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

# Роуты с страничками

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_app = Application(
            user_id=1,
            course_id=request.form.get('course_id'),
            message=request.form.get('message')
        )
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for('user_page'))
    
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/user')
def user_page():
    my_apps = Application.query.filter_by(user_id=1).all()
    return render_template('user.html', applications=my_apps)

@app.route('/add_review/<int:application_id>', methods=['POST'])
def add_review(application_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')

    if rating and comment:
        new_review = Review(
            application_id=application_id,
            rating=int(rating),
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()

    return redirect(url_for('user_page'))

if __name__ == '__main__':
    app.run(debug=True)