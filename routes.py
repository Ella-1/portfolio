from flask import render_template,redirect,url_for,abort,current_app, flash,request
from forms import LoginForm, RegistrationForm,PostForm, UpdateAccountForm
from model import db,app,Users,bcrypt,photos,Post
from flask_login import login_user,login_required,current_user,logout_user
import os



@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title="Home")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Users.query.filter_by(email=form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
         #terinary conditional in python
        flash('Login successful!', 'success')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    else:
        flash('Login Unsuccessful. Please check username and password', 'danger')
   
    return render_template('user/login.html', title="Login", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    
    if request.method == "POST":
        hashed_password= bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        name = request.form.get('name')
        username = request.form.get('username')
        password  = hashed_password
        email = request.form.get('email')

        user = Users(name=name, username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created you can now login', 'success')
        return redirect(url_for('login'))
    return render_template('user/register.html', title="Registration", form=form)


@app.route('/blog')
def blog_home():
    return render_template('blog/home.html', title='Blog-Home')

@app.route('/create', methods=['GET', 'POST'])
def create_blog():
    form= PostForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == "POST":
       
        category = request.form.get('category')
        title = request.form.get('title')
        content = request.form.get('content')
        image = photos.save(request.files.get('image'))

        user = Post( title=title, content=content, category=category,image=image)
        db.session.add(user)
        db.session.commit()
        flash(f'Blog was created successful', 'success')
        return redirect(url_for('blog_home'))
    return render_template('blog/create_blog.html', title="Create-Blog", form=form)

@app.route('/blog/<int:blog_id>/update', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    blog = Post.query.get_or_404(blog_id)
    form = PostForm()
    
   
    if form.validate_on_submit():
        blog.title= form.title.data
        blog.Category= form.category.data
        blog.content= form.content.data
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + blog))
                blog.image =  photos.save(request.files.get('image'))
            except:
                 blog.image =  photos.save(request.files.get('image'))
        elif request.method == 'GET':
            form.title.data = blog.title
            form.category.data = blog.category
            form.content.data = blog.content
            form.image.data = blog.image
            flash('Your blog has been updated!', 'success')
            return redirect(url_for('blog_home', blog_id=blog.id))
    return render_template('blog/edit_blog.html', title="Update-Blog", form=form)

@app.route('/blog/<int:blog_id>/delete', methods=['DELETE'])
@login_required
def delete_blog(blog_id):
    if blog.author != current_user:
        abort(403)
    blog = PostForm.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash(f'Your blog has been deleted successfully', 'success')



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)