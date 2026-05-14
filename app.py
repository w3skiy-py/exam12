from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwerty@127.0.0.1:5432/examflask'
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CURRENT_USER_ID = 2


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    applications = db.relationship('Application', backref='user', lazy=True)


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    applications = db.relationship('Application', backref='course', lazy=True)


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    message = db.Column(db.Text)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    application = db.relationship('Application', backref=db.backref('review', uselist=False))


@app.route('/')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)


@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    application = Application.query.filter_by(
        user_id=CURRENT_USER_ID,
        course_id=course_id
    ).first()

    error = None

    if request.method == 'POST':
        if application:
            error = 'Вы уже подали заявку на этот курс.'
        else:
            reason = request.form.get('reason')

            new_application = Application(
                user_id=CURRENT_USER_ID,
                course_id=course_id,
                message=reason
            )
            db.session.add(new_application)
            db.session.commit()

            flash('Заявка успешно отправлена!', 'success')
            return redirect(url_for('course_detail', course_id=course_id))

    reviews = Review.query.join(Application).filter(Application.course_id == course_id).all()

    return render_template(
        'course_detail.html',
        course=course,
        reviews=reviews,
        application=application,
        error=error
    )


@app.route('/my_applications')
def my_applications():
    apps = Application.query.filter_by(user_id=CURRENT_USER_ID).all()
    return render_template('user.html', applications=apps)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)