from flask_login import current_user, login_user, logout_user, login_required
from main.models import User, Documents, Rating
from main import app, db, ALLOWED_EXTENSIONS
from flask import redirect, url_for, flash, render_template, request, send_from_directory
from main.forms import LoginForm, RegistrationForm, DocumentsForm
from werkzeug.utils import secure_filename
import os


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/', methods=['GET', 'POST'])
def index():
    user_rate = db.session.query(Rating).filter_by(user_id=current_user.__dict__.get('id')).subquery()
    data = Documents.query.outerjoin(user_rate, Documents.id == user_rate.c.document_id).filter(
        Documents.visible == 1).add_columns(Documents.name, Documents.filename, Documents.rating,
                                            Documents.id, user_rate.c.user_id)

    if request.method == 'POST':
        choice, doc_id = request.form['choice'].split(', ')
        res = Rating(rate=int(choice), document_id=doc_id, user_id=current_user.id)
        db.session.add(res)
        db.session.query(Documents).filter_by(id=doc_id).update({'rating': Documents.rating + int(choice)})
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('index.html', data=data.all())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user', methods=['GET', 'POST'])
def user():
    if current_user.is_authenticated:
        if request.method == 'POST':
            if request.form.get('submit') == 'upload':
                return redirect(url_for('upload_file'))
        documents = Documents.query.filter_by(user_id=current_user.id)
        return render_template('user.html', docs=documents)
    else:
        return redirect(url_for('login'))


@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = DocumentsForm()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            document = Documents(name=form.name.data or filename, body=form.body.data,
                                 visible=bool(form.visible.data), user_id=current_user.id, filename=filename)
            db.session.add(document)
            db.session.commit()

            return redirect(url_for('user'))
        else:
            flash(f'Error! Unexpected filename extension. Available: {", ".join(ALLOWED_EXTENSIONS)}')
    return render_template('upload_file.html', form=form)


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    directory = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=directory, filename=filename, as_attachment=True)


@app.route('/document/<doc_id>', methods=['GET', 'POST'])
@login_required
def alter_doc(doc_id):
    form = DocumentsForm()
    query = Documents.query.filter_by(id=doc_id)
    doc = query.first_or_404()
    form.name.data = doc.name
    form.body.data = doc.body

    if request.method == 'POST':
        form = DocumentsForm(request.form)
        query.update({'name': form.name.data, 'body': form.body.data, 'visible': bool(form.visible.data)})
        db.session.commit()
        return redirect(url_for('user'))
    return render_template('alter_doc.html', form=form, doc=doc)


@app.route('/document/<doc_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_doc(doc_id):
    query = Documents.query.filter_by(id=doc_id).first_or_404()
    if request.method == 'POST':
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], query.filename))
        db.session.delete(query)
        db.session.commit()
        return redirect(url_for('user'))
    return render_template('delete_doc.html', name=query.name)
