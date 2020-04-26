import os
from flask_mail import Mail, Message
from flask import Flask, render_template, request, session, redirect, url_for, flash, g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy

engine = create_engine("mysql+pymysql://root:Cssp#143@localhost/cssp")
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)


# Login here
# ==========


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("emailID")
        password = request.form.get("passwd")
        emaildata = db.execute("SELECT email FROM signup WHERE email=:email", {"email": email}).fetchone()
        passworddata = db.execute("SELECT passwd FROM signup WHERE email=:email", {"email": email}).fetchone()
        if emaildata is None:
            flash("No username", "danger")
            return render_template("login.html")
        else:
            for i in passworddata:
                if i == password:
                    return redirect(url_for('home'))
                else:
                    return render_template("login.html")

    return render_template('login.html', title='login')


@app.route('/sign_out')
def sign_out():
    session.pop('username', None)
    return redirect(url_for('login'))


# Sign up here
# ============


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("fname")
        last_name = request.form.get("lname")
        contact = request.form.get("contact")
        email = request.form.get("email")
        passwd = request.form.get("pass")
        repasswd = request.form.get("repass")

        if passwd == repasswd:
            db.execute(
                "INSERT INTO signup(firstName,lastName,email,contact,passwd,repass) VALUES(:fname,:lname,:email,"
                ":contact,:pass,:repass)",
                {"fname": first_name, "lname": last_name, "contact": contact,
                 "email": email, "pass": passwd, "repass": repasswd})
            db.commit()
            return redirect(url_for('login'))
        else:
            flash("Password is not match..!!", "danger")
            return render_template('signup.html')

    return render_template('signup.html')


@app.route("/forgot")
def forgot():
    return render_template('forgot.html')


@app.route("/home")
def home():
    return render_template('index.html')


# ioMemory Posts
# ==============

@app.route("/ioMemory", methods=["GET", "POST"])
def iomemory():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM posts where deviceType=1")
        return render_template('iomemory.html', posts=posts)


# Data60 Posts
# ============

@app.route("/data60", methods=["GET", "POST"])
def data60():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM posts where deviceType=2")
        return render_template('data60.html', posts=posts)


# Data102 Posts
# ==============


@app.route("/data102", methods=["GET", "POST"])
def data102():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM posts where deviceType=3")
        return render_template('data102.html', posts=posts)


# G-Rack Posts
# ============


@app.route("/g-rack", methods=["GET", "POST"])
def grack():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM posts where deviceType=4")
        return render_template('g-rack.html', posts=posts)


# Show all posted data
# ====================

@app.route("/post-details/<string:post_slug>", methods=["GET"])
def postdetails(post_slug):
    slug_number = post_slug
    if request.method == "GET":
        posts = db.execute("SELECT * FROM posts where slug=:slug_number", {"slug_number": slug_number})
        return render_template('postdetails.html', posts=posts, slug_number=slug_number)


# Update all posted data
# ======================
@app.route("/post-update/<string:post_slug>", methods=["GET"])
def postupdate(post_slug):
    if request.method == "GET":
        posts = db.execute("SELECT * FROM posts where slug=:slug_number", {"slug_number": post_slug})
        return render_template('updatepost.html', posts=posts, slug_number=post_slug)


@app.route("/post-updating/<string:post_slug>", methods=["POST"])
def updatingpost(post_slug):
    if request.method == "POST":
        update_item = request.form.get("updateitem")
        update_value = request.form.get("updatevalue")
        print(update_value)
        print(update_item)
        if update_item == '1':
            db.execute("UPDATE `posts` SET `subject`=:update_value WHERE `slug`=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        elif update_item == '2':
            db.execute("UPDATE `posts` SET `infoType`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        elif update_item == '3':
            db.execute("UPDATE `posts` SET `steps`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        elif update_item == '4':
            db.execute("UPDATE `posts` SET `sfdcID`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        elif update_item == '5':
            db.execute("UPDATE `posts` SET `esswiki`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        else:
            db.execute("UPDATE `posts` SET `essjira`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        return redirect(url_for('updatepostsendmail'))
        # posts = db.execute("UPDATE posts SET tutorial_title = 'Learning JAVA'  WHERE slug=:slug_number",
        # {"slug_number": post_slug})
        return render_template('index.html')


# Delete post
# ============

@app.route("/post-delete/<string:post_slug>", methods=["GET"])
def postdelete(post_slug):
    if request.method == "GET":
        db.execute("DELETE FROM posts WHERE slug=:slug_number", {"slug_number": post_slug})
        db.commit()
        # posts = db.execute("SELECT * FROM posts where slug=:slug_number", {"slug_number": post_slug})
        return redirect(url_for('home'))
    return render_template('index.html')


# Device Post Here
# ===============

@app.route("/post", methods=["GET", "POST"])
def post():
    if request.method == "POST":
        dev_type = request.form.get("device")
        info_type = request.form.get("info")
        subject = request.form.get("text")
        steps = request.form.get("steps")
        sfdc_id = request.form.get("sfdc")
        esswiki = request.form.get("esswiki")
        essjira = request.form.get("essjira")
        db.execute(
            "INSERT INTO posts(deviceType,infoType,subject,steps,sfdcID,esswiki,essjira) VALUES(:device,:info,:text,"
            ":steps,:sfdc,:esswiki,:essjira)",
            {"device": dev_type, "info": info_type, "text": subject,
             "steps": steps, "sfdc": sfdc_id, "esswiki": esswiki, "essjira": essjira})
        db.commit()
        return redirect(url_for('newpostsendmail', subject=subject))

    return render_template('post.html')


# Process Tab
# ===========


@app.route("/dcsrma", methods=["GET", "POST"])
def dcsrma():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM process where processType=1")
        return render_template('dcsrma.html', posts=posts)


@app.route("/abcrma", methods=["GET", "POST"])
def abcrma():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM process where processType=2")
        return render_template('abcrma.html', posts=posts)


@app.route("/fgl", methods=["GET", "POST"])
def fgl():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM process where processType=3")
        return render_template('fgl.html', posts=posts)


@app.route("/sfdc", methods=["GET", "POST"])
def sfdc():
    if request.method == "GET":
        posts = db.execute("SELECT * FROM process where processType=4")
        return render_template('sfdc.html', posts=posts)


# Show all process data
# =====================

@app.route("/process-details/<string:post_slug>", methods=["GET"])
def processdetails(post_slug):
    slug_number = post_slug
    if request.method == "GET":
        posts = db.execute("SELECT * FROM process where slug=:slug_number", {"slug_number": slug_number})
        return render_template('processdetails.html', posts=posts, slug_number=slug_number)


# Process Post Here
# ===============

@app.route("/processpost", methods=["GET", "POST"])
def processpost():
    if request.method == "POST":
        pro_type = request.form.get("process")
        subject = request.form.get("subject")
        body = request.form.get("body")
        esswiki = request.form.get("esswiki")
        essjira = request.form.get("essjira")
        db.execute(
            "INSERT INTO process(processType,subject,body,esswiki,essjira) VALUES(:process,:subject,:body,"
            ":esswiki,:essjira)",
            {"process": pro_type, "subject": subject, "body": body,
             "esswiki": esswiki, "essjira": essjira})
        db.commit()
        return redirect(url_for('newpostsendmail', subject=subject))

    return render_template('processpost.html')


# Process Post Update
# ===================

@app.route("/process-update/<string:post_slug>", methods=["GET"])
def processpostupdate(post_slug):
    if request.method == "GET":
        posts = db.execute("SELECT * FROM process where slug=:slug_number", {"slug_number": post_slug})
        return render_template('processpostupdate.html', posts=posts, slug_number=post_slug)


@app.route("/process-updating/<string:post_slug>", methods=["POST"])
def updatingprocesspost(post_slug):
    if request.method == "POST":
        update_item = request.form.get("updateitem")
        update_value = request.form.get("updatevalue")
        if update_item == '1':
            db.execute("UPDATE `process` SET `subject`=:update_value WHERE `slug`=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        elif update_item == '2':
            db.execute("UPDATE `process` SET `body`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        elif update_item == '3':
            db.execute("UPDATE `process` SET `esswiki`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        else:
            db.execute("UPDATE `process` SET `essjira`=:update_value WHERE slug=:post_slug",
                       {"post_slug": post_slug, "update_value": update_value})
            db.commit()
        return redirect(url_for('updatepostsendmail'))

    return render_template('index.html')


# Delete process post
# ===================

@app.route("/process-delete/<string:post_slug>", methods=["GET"])
def processpostdelete(post_slug):
    if request.method == "GET":
        db.execute("DELETE FROM process WHERE slug=:slug_number", {"slug_number": post_slug})
        db.commit()
        # posts = db.execute("SELECT * FROM posts where slug=:slug_number", {"slug_number": post_slug})
        return redirect(url_for('home'))
    return render_template('index.html')


# Mail configuration

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'pandey.somnath007@gmail.com'
app.config['MAIL_PASSWORD'] = 'mail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'pandey.somnath007@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = True

mail = Mail(app)


@app.route('/new-post-send-mail/<subject>', methods=['GET', 'POST'])
def newpostsendmail(subject):
    if request.method == "GET":
        msg = Message('New post in CSS IntUse', recipients=['pandey.somnath007@gmail.com'])
        msg.html = 'Hello Team, <br><br> New post in CSS IntUse, here is the subject line "<b>' + subject + '</b>".Please login in CSS IntUse and see the new post.<br><br><b>NOTE:</b>This is auto generated mail, please do not reply on this mail.<br><br>Regards<br>CSS IntUse'
        mail.send(msg)
        return redirect(url_for('home'))
    return "Error while sending mail"


@app.route('/update-post-send-mail', methods=['GET', 'POST'])
def updatepostsendmail():
    if request.method == "GET":
        msg = Message('New updated post in CSS IntUse', recipients=['pandey.somnath007@gmail.com'])
        msg.html = 'Hello Team,<br><br> New updated post in CSS IntUse. Please login in CSS IntUse and see the new updated post.<br><br><b>NOTE:</b>This is auto generated mail, please do not reply on this mail.<br><br>Regards<br>CSS IntUse'
        mail.send(msg)
        return redirect(url_for('home'))

    return "Error while sending mail"


app.run(debug=True)
