import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'D:\\Users\\Jayesh\\Desktop\\flask_blog-master\\static\\uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

class Image(db.Model):
     image_id = db.Column(db.Integer, primary_key=True)
     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
     #register_id = db.Column()----foriegn key  image id match with user id
     
class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    #register id forieng key ...we can see what users have posted also user id match with title
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    designation = db.Column(db.String(50))
    #image file fk coz we can see which user has what pic.


@app.route('/', methods=['GET', 'POST' ])
def register():
    if request.method == "POST":
        username = request.form['username']
        designation= request.form['designation']
        password = request.form['password']
        email = request.form['email']
        user = User(username=username , email= email, password= password ,designation=designation)
        db.session.add(user)
        db.session.commit()
        

        session['email']=email
        return redirect(url_for('signup'))
    else:
        return render_template('register.html')


@app.route('/signup', methods =['GET', 'POST'])
def signup():
    
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']  
        conn=sqlite3.connect('blog.db')
        c=conn.cursor()
        c.execute("SELECT * FROM User WHERE username='"+username+"' and password='"+password+"'")
        data=c.fetchone()
        
        #app.logger.info(design)
        
        if (data[1]==username and data[3]==password):
            design = data[4]
            session['design']= design
            session['logedin']=True
            session['username']= username
            #globaluser = username
            #app.logger.warning(globaluser)
            flash("Successfully logged in!","info")

            return redirect(url_for('index'))

        


        



    else:
            error="invalid"
            return render_template('signup.html')

#def foreignkey():
        #y = globaluser
        #return y

@app.route('/index')
def index():
     #previous sqlalchemy query
    #posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
     conn=sqlite3.connect('blog.db')
     c=conn.cursor()
     c.execute("SELECT * from Blogpost ORDER BY date_posted DESC")
     posts = c.fetchall()
     return render_template('index.html', posts=posts)



@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/post/<int:post_id>')
def post(post_id):
    conn=sqlite3.connect('blog.db')
    c=conn.cursor()
    c.execute("SELECT * from Blogpost WHERE id=(?)",(post_id,))
    post = c.fetchone()
    #previous sqlalchemy query
    #post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)



@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == "POST":
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        content = request.form['content']
        date=datetime.now()
        conn=sqlite3.connect('blog.db')
        c=conn.cursor()
        c.execute("SELECT * FROM User WHERE username=(?)",(session.get('username'),) )
        data=c.fetchone()
        
        c.execute("INSERT INTO Blogpost(title,subtitle,author,date_posted,content,bloguser_id) VALUES(?,?,?,?,?,?)",(title,subtitle,author,date,content,data[0]))
        conn.commit()
    return render_template('add.html')






@app.route('/profile', methods=['GET', 'POST'])
def profile():
    
    proname=""

    if request.method == "POST":
       profilepic=request.files['profilepic']
       profilepic.save(os.path.join(UPLOAD_FOLDER, profilepic.filename))
       proname=profilepic.filename
       
       conn=sqlite3.connect('blog.db')
       c=conn.cursor()
       c.execute("SELECT * FROM User WHERE username=(?)",(session.get('username'),) )
       data=c.fetchone()
       #app.logger.warning(data)
       c.execute("INSERT INTO Image (image_file,userimage_id) VALUES  (?,?)",(profilepic.filename,data[0]))
       conn.commit()
       
       #inserting imagename in db
       #pic= Image(image_file=profilepic.filename)
       

       #db.session.add(pic)
       #db.session.commit()
       #session
       session['profilepic']=profilepic.filename

    return render_template("profile.html")



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        post = request.form['post']
        # search by author or post
        conn=sqlite3.connect('blog.db')
        c=conn.cursor()
        c.execute("SELECT title, author from Blogpost WHERE title LIKE (?) OR author LIKE (?)", (post, post))
        data = c.fetchall()
        return render_template("search.html" ,data=data)
        
        
    return render_template("search.html" )



@app.route('/loggedout')
def loggedout():
    session.pop("profilepic", None)
    session.pop("design",None)
    session.pop("username",None)
    flash("you have been logged out","info")
    return redirect(url_for('signup'))

if __name__ == '__main__':
    app.run(debug=True)
