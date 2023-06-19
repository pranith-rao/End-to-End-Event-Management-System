from asyncio import events
from flask import *
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import os, random, re, requests, json, smtplib
import io, csv, cloudinary, qrcode
from datetime import timedelta, date, datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import To
import cloudinary.uploader

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///event_db.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_NAME"] = "login-system"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=5)

cloudinary.config(cloud_name="eventx", api_key="", api_secret="")

# client_id="505348922138-a10mfp737qq5lmgi33opfis1ln0cka5j.apps.googleusercontent.com",
# client_secret='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',

db = SQLAlchemy(app)


# creating tables
class Organizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=False)
    event_org_id = db.relationship("Event", cascade="all,delete", backref="owner")
    alert_org_id = db.relationship("Alert", cascade="all,delete", backref="owner")

    def __repr__(self):
        return "<Organizer %r>" % self.email


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    qrlink = db.Column(db.String(50), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    pevent_id = db.relationship("Plist", cascade="all,delete", backref="owner")

    def _repr_(self):
        return "<Participant %r>" % self.email


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    location = db.Column(db.String(100), nullable=False)

    def _repr_(self):
        return "<Organization %r>" % self.email


class Coorganizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    organizer = db.Column(db.String(50), nullable=False)
    coorg_id = db.relationship("Event", cascade="all,delete", backref="owner1")
    jcoorg_id = db.relationship("Judge", cascade="all,delete", backref="owner1j")

    def _repr_(self):
        return "<coorganizer %r>" % self.email


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    coorg_mail = db.Column(db.String(80), db.ForeignKey("coorganizer.email"))
    org_id = db.Column(db.Integer, db.ForeignKey("organizer.id"))
    participant_id = db.relationship(
        "Participant", cascade="all,delete", backref="participants"
    )
    judge_event_id = db.relationship("Judge", cascade="all,delete", backref="ownersj")
    part_event_id = db.relationship("Plist", cascade="all,delete", backref="ownersjp")

    def __repr__(self):
        return "<Event %r>" % self.name


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attendee = db.Column(db.String(50), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey("organizer.id"), nullable=True)

    def __repr__(self):
        return self.attendee


class Judge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    coorg_mail = db.Column(db.String(80), db.ForeignKey("coorganizer.email"))

    def __repr__(self):
        return self.attendee


class Plist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey("participant.id"), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=True)
    score = db.Column(db.Integer, nullable=True)


# db.create_all()
# db.drop_all()


# home page
@app.route("/")
def home():
    return render_template("home.html")


def send_mail(recipient, subject, body):
    FROM = "gtafive5one@gmail.com"
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body + "\n\nThanks & Regards,\nTeam EventX"

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (
        FROM,
        ", ".join(TO),
        SUBJECT,
        TEXT,
    )
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login("gtafive5one@gmail.com", "cuagyxlpxfcpczzf")
        server.sendmail(FROM, TO, message)
        server.close()
    except:
        flash("Check your internet connection", "error")
        return redirect(url_for("home"))


# login page
@app.route("/alllog")
def alllog():
    return render_template("alllog.html")


@app.route("/admin_log")
def admin_log():
    return render_template("admin_log.html")


@app.route("/admin_dash")
def admin_dash():
    if "admin" in session:
        organizations = Organization.query.count()
        organizers = Organizer.query.count()
        return render_template("admin_dash.html", data=[organizations, organizers])
    else:
        flash("Session Expired", "error")
        return redirect(url_for("admin_log"))


# main admin login
@app.route("/adminlog", methods=["POST"])
def mainadmin_log():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email == "mainadmin@gmail.com" and password == "event123":
            session["admin"] = True
            session["admin_name"] = email
            flash("Login Successfull", "success")
            return redirect(url_for("admin_dash"))
        else:
            flash("Invalid Credentials", "error")
            return redirect(url_for("admin_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participantreg")
def participantreg():
    return render_template("participantreg.html")


def upload(file, **options):
    res = cloudinary.uploader.upload(file)
    return res["secure_url"]


# participant registeration
@app.route("/participant_register", methods=["POST"])
def participant_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        category = request.form["category"]
        password = request.form["password"]
        email_check = Participant.query.filter_by(email=email).first()
        if not email_check:
            phone_check = Participant.query.filter_by(phone=phone).first()
            if not phone_check:
                flag = 0
                while True:
                    if len(password) < 8:
                        flag = -1
                        break
                    elif not re.search("[a-z]", password):
                        flag = -1
                        break
                    elif not re.search("[A-Z]", password):
                        flag = -1
                        break
                    elif not re.search("[0-9]", password):
                        flag = -1
                        break
                    elif not re.search("[_@$]", password):
                        flag = -1
                        break
                    elif re.search("\\s", password):
                        flag = -1
                        break
                    else:
                        flag = 0
                        break
                if flag == -1:
                    flash("Not a Valid Password", "error")
                    return redirect(url_for("participantreg"))
                hash_pass = sha256_crypt.hash(password)
                participant = Participant(
                    name=name,
                    email=email,
                    phone=phone,
                    category=category,
                    password=hash_pass,
                )
                db.session.add(participant)
                db.session.commit()
                data = Participant.query.filter_by(email=email).first()
                link = str(
                    "ID: "
                    + str(data.id)
                    + "\nName: "
                    + data.name
                    + "\nEmail: "
                    + data.email
                    + "\nPhone: "
                    + str(data.phone)
                )
                qr_image = qrcode.QRCode(version=1, box_size=10, border=5)
                qr_image.add_data(link)
                qr_image.make(fit=True)
                img = qr_image.make_image(fill="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                img_url = upload(buffer)
                part_data = Participant(qrlink=img_url)
                db.session.commit()
                send_mail(
                    email,
                    "Registration Successfull",
                    "Thank you for registering on our website.Hope you have a good experience.Your unique QR code is: "
                    + img_url,
                )
                flash("Registeration successfully", "success")
                return redirect(url_for("participantlog"))
            else:
                flash("Phone Number already registered", "error")
                return redirect(url_for("participantreg"))
        else:
            flash("Email ID already registered", "error")
            return redirect(url_for("participantreg"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participantlog")
def participantlog():
    return render_template("participant_log.html")


# participant login
@app.route("/participant_login", methods=["POST"])
def participant_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        response = Participant.query.filter_by(email=email).first()
        if not response:
            flash("Email ID not registered", "error")
            return redirect(url_for("participantlog"))
        else:
            checkpass = sha256_crypt.verify(password, response.password)
            if email == response.email and checkpass == True:
                session["participant"] = True
                session["participant_id"] = response.id
                session["participant_name"] = response.name
                session["participant_email"] = response.email
                session["participant_phone"] = response.phone
                session["participant_category"] = response.category
                flash("You were successfully logged in", "success")
                return redirect(url_for("participantdash"))
            else:
                flash("Invalid Credentials", "error")
                return redirect(url_for("participantlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participantdash")
def participantdash():
    if "participant" in session:
        events = Event.query.count()
        reg_event = Plist.query.filter_by(part_id=session["participant_id"]).count()
        return render_template("participant_dash.html", data=[events, reg_event])
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


@app.route("/participant_forpass")
def participant_forpass():
    return render_template("participant_forpass.html")


# participant forgot password
@app.route("/participant_send_otp", methods=["POST"])
def participant_send_otp():
    if request.method == "POST":
        email = request.form["email"]
        email_check = Participant.query.filter_by(email=email).first()
        if email_check:
            session["participant"] = True
            session["email"] = email_check.email
            otp = random.randint(000000, 999999)
            session["otp"] = otp
            send_mail(
                email,
                "OTP for Password change",
                "Dear participant, your verification code is: " + str(otp),
            )
            flash("OTP sent", "success")
            return redirect(url_for("participant_otp"))
        else:
            flash(
                "Email ID not registered. Please check your email id or create a new account",
                "error",
            )
            return redirect(url_for("participantlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participant_otp")
def participant_otp():
    return render_template("participant_otp.html")


# participant otp verification for forgot password
@app.route("/participant_verify", methods=["POST"])
def participant_verify():
    if request.method == "POST":
        if "participant" in session:
            participant_otp = request.form["participant_otp"]
            if session["otp"] == int(participant_otp):
                return redirect(url_for("participant_forpass_form"))
            else:
                flash("Wrong OTP. Please try again", "error")
                return redirect(url_for("participant_otp"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("participantlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participant_forpass_form")
def participant_forpass_form():
    return render_template("participant_forpass_form.html")


# participant change password after otp verification
@app.route("/change_participant_pass", methods=["POST"])
def change_participant_pass():
    if request.method == "POST":
        if "participant" in session:
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("participant_forpass_form"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data = Participant.query.filter_by(email=session["email"]).first()
                data.password = hash_pass
                db.session.commit()
                session.pop("participant", None)
                session.pop("email", None)
                flash("Password changed successfully", "success")
                return redirect(url_for("participantlog"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("participant_forpass_form"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("participantlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participant_profile")
def participant_profile():
    if "participant" in session:
        return render_template("participant_profile.html")
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


@app.route("/participant_profile_update")
def participant_profile_update():
    if "participant" in session:
        get_participant_data = Participant.query.filter_by(
            id=session["participant_id"]
        ).first()
        return render_template("participant_profupdate.html", data=get_participant_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


# participant profile update
@app.route("/update_participant_profile/<int:id>", methods=["POST"])
def update_participant_profile(id):
    if "participant" in session:
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            phno = request.form["phno"]
            category = request.form["category"]
            data = Participant.query.filter_by(id=id).first()
            email_check = Participant.query.filter_by(email=email).first()
            if email_check:
                if email_check.id != id:
                    flash("Email ID is already used by someone else", "error")
                    data = Participant.query.filter_by(id=id).first()
                    return render_template("participant_profupdate.html", data=data)
                elif email_check.id == id:
                    data.email = email
                    data.name = name
                    phno_check = Participant.query.filter_by(phone=phno).first()
                    if phno_check:
                        if phno_check.id != id:
                            flash(
                                "Phone number is already used by someone else", "error"
                            )
                            data = Participant.query.filter_by(id=id).first()
                            return render_template(
                                "participant_profupdate.html", data=data
                            )
                        elif phno_check.id == id:
                            data.phone = phno
                            data.category = category
                            db.session.commit()
                            session.clear()
                            flash(
                                "Participant details updated successfully.Login again to see changes",
                                "success",
                            )
                            return redirect(url_for("participantlog"))
                    else:
                        data.phone = phno
                        data.category = category
                        db.session.commit()
                        session.clear()
                        flash(
                            "Participant details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("participantlog"))
            else:
                data.email = email
                data.name = name
                phno_check = Participant.query.filter_by(phone=phno).first()
                if phno_check:
                    if phno_check.id != id:
                        flash("Phone number is already used by someone else", "error")
                        data = Participant.query.filter_by(id=id).first()
                        return render_template("participant_profupdate.html", data=data)
                    elif phno_check.id == id:
                        data.phone = phno
                        data.category = category
                        db.session.commit()
                        session.clear()
                        flash(
                            "Participant details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("participantlog"))
                else:
                    data.phone = phno
                    data.category = category
                    db.session.commit()
                    session.clear()
                    flash(
                        "Participant details updated successfully.Login again to see changes",
                        "success",
                    )
                    return redirect(url_for("participantlog"))
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


@app.route("/change_pass_participant")
def change_pass_participant():
    if "participant" in session:
        get_participant_data = Participant.query.filter_by(
            id=session["participant_id"]
        ).first()
        return render_template(
            "change_pass_participant.html", data=get_participant_data
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


# participant change password after login
@app.route("/participant_change_pass", methods=["POST"])
def participant_change_pass():
    if request.method == "POST":
        if "participant" in session:
            email = request.form["email"]
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("changepass_participant"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                email_check = Participant.query.filter_by(email=email).first()
                if email_check:
                    hash_pass = sha256_crypt.hash(pass1)
                    email_check.password = hash_pass
                    db.session.commit()
                    flash("Password changed successfully", "success")
                    return redirect(url_for("participantdash"))
                else:
                    flash("Check your email and try again", "error")
                    return redirect(url_for("changepass_participant"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("changepass_participant"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("participantlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/organization")
def organization():
    if "admin" in session:
        return render_template("add_organization.html")
    else:
        flash("Session Expired", "error")
        return redirect(url_for("admin_log"))


# adding organization
@app.route("/add_organization", methods=["POST"])
def add_organization():
    if request.method == "POST":
        if "admin" in session:
            name = request.form["name"]
            email = request.form["email"]
            location = request.form["location"]
            email_check = Organization.query.filter_by(email=email).first()
            if not email_check:
                organization = Organization(name=name, email=email, location=location)
                db.session.add(organization)
                db.session.commit()
                send_mail(
                    email,
                    "Your organization has been added!",
                    "Your organization has been successfully added under EventX. Hope you have a wonderful experience",
                )
                flash("Organization added successfully", "success")
                return redirect(url_for("admin_dash"))
            else:
                flash("Email ID already used", "error")
                return redirect(url_for("organization"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("admin_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/organizationsList")
def organizationsList():
    if "admin" in session:
        organizations = Organization.query.all()
        return render_template("organizations_list.html", data=organizations)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("admin_log"))


@app.route("/organizer")
def organizer():
    if "admin" in session:
        organizations = Organization.query.count()
        if not organizations:
            flash("Add atleast one organization", "error")
            return redirect(url_for("admin_dash"))
        else:
            get_organization_data = Organization.query.all()
            return render_template("add_organizer.html", data=get_organization_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("admin_log"))


# adding organizer
@app.route("/add_organizer", methods=["POST"])
def add_organizer():
    if request.method == "POST":
        if "admin" in session:
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            organization = request.form["organization"]
            email_check = Organizer.query.filter_by(email=email).first()
            if not email_check:
                phone_check = Organizer.query.filter_by(phone=phone).first()
                if not phone_check:
                    hash_pass = sha256_crypt.hash(email)
                    organizer = Organizer(
                        name=name,
                        email=email,
                        phone=phone,
                        password=hash_pass,
                        organization=organization,
                    )
                    db.session.add(organizer)
                    db.session.commit()
                    send_mail(
                        email,
                        "You are a Organizer!",
                        "You have been successfully added as a ORGANIZER under the organization "
                        + str(organization).upper()
                        + ". Please use your email as your password on your first login and change it later for security purposes",
                    )
                    flash("Organizer added successfully", "success")
                    return redirect(url_for("admin_dash"))
                else:
                    flash("Phone Number already registered", "error")
                    return redirect(url_for("organizer"))
            else:
                flash("Email ID already used", "error")
                return redirect(url_for("organizer"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("admin_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/organizersList")
def organizersList():
    if "admin" in session:
        organizers = Organizer.query.all()
        return render_template("organizers_list.html", data=organizers)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("admin_log"))


@app.route("/organizer_log", methods=["GET", "POST"])
def organizer_log():
    return render_template("organizer_log.html")


# organizer login
@app.route("/organizerlog", methods=["POST"])
def organizerlog():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        response = Organizer.query.filter_by(email=email).first()
        if not response:
            flash("Email ID not registered", "error")
            return redirect(url_for("organizer_log"))
        else:
            checkpass = sha256_crypt.verify(password, response.password)
            if email == response.email and checkpass == True:
                session["organizer"] = True
                session["organizer_id"] = response.id
                session["organizer_name"] = response.name
                session["organizer_email"] = response.email
                session["organizer_phone"] = response.phone
                session["organizer_organization"] = response.organization
                flash("You were successfully logged in", "success")
                return redirect(url_for("organizerdash"))
            else:
                flash("Invalid Credentials", "error")
                return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/organizerdash")
def organizerdash():
    if "organizer" in session:
        co_organizers = Coorganizer.query.count()
        events = Event.query.count()
        return render_template("organizer_dash.html", data=[co_organizers, events])
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/organizer_profile")
def organizer_profile():
    if "organizer" in session:
        return render_template("organizer_profile.html")
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/organizer_profile_update")
def organizer_profile_update():
    if "organizer" in session:
        get_organizer_data = Organizer.query.filter_by(
            id=session["organizer_id"]
        ).first()
        return render_template("organizer_profupdate.html", data=get_organizer_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


# organizer profile update
@app.route("/update_organizer_profile/<int:id>", methods=["POST"])
def update_organizer_profile(id):
    if "organizer" in session:
        if request.method == "POST":
            name = request.form["name"]
            phno = request.form["phno"]
            if name == session["organizer_name"] and phno == session["organizer_phone"]:
                flash("No changes made", "warning")
                return redirect(url_for("organizerdash"))
            else:
                data = Organizer.query.filter_by(id=id).first()
                phno_check = Organizer.query.filter_by(phone=phno).first()
                if phno_check:
                    if phno_check.id != id:
                        flash("Phone number is already used by someone else", "error")
                        data = Organizer.query.filter_by(id=id).first()
                        return render_template("organizer_profupdate.html", data=data)
                    elif phno_check.id == id:
                        data.phone = phno
                        data.name = name
                        db.session.commit()
                        session.clear()
                        flash(
                            "Organizer details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("organizer_log"))
                else:
                    data.phone = phno
                    data.name = name
                    db.session.commit()
                    session.clear()
                    flash(
                        "Organizer details updated successfully.Login again to see changes",
                        "success",
                    )
                    return redirect(url_for("organizer_log"))
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/change_pass_organizer")
def change_pass_organizer():
    if "organizer" in session:
        get_organizer_data = Organizer.query.filter_by(
            id=session["organizer_id"]
        ).first()
        return render_template("change_pass_organizer.html", data=get_organizer_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


# organizer change password after login
@app.route("/organizer_change_pass/<string:email>", methods=["POST"])
def organizer_change_pass(email):
    if request.method == "POST":
        if "organizer" in session:
            data = Organizer.query.filter_by(email=email).first()
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("change_pass_organizer"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data.password = hash_pass
                db.session.commit()
                flash("Password changed successfully", "success")
                return redirect(url_for("organizerdash"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("change_pass_organizer"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/organizer_forpass")
def organizer_forpass():
    return render_template("organizer_forpass.html")


# organizer forgot password
@app.route("/organizer_send_otp", methods=["POST"])
def organizer_send_otp():
    if request.method == "POST":
        email = request.form["email"]
        email_check = Organizer.query.filter_by(email=email).first()
        if email_check:
            session["organizer"] = True
            session["email"] = email_check.email
            otp = random.randint(000000, 999999)
            session["otp"] = otp
            send_mail(
                email,
                "OTP for Password change",
                "Dear organizer, your verification code is: " + str(otp),
            )
            flash("OTP sent", "success")
            return redirect(url_for("organizer_otp"))
        else:
            flash(
                "Email ID not registered. Please check your email id or ask admin to create a new account",
                "error",
            )
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/organizer_otp")
def organizer_otp():
    return render_template("organizer_otp.html")


# organizer otp verification for forgot password
@app.route("/organizer_verify", methods=["POST"])
def organizer_verify():
    if request.method == "POST":
        if "organizer" in session:
            organizer_otp = request.form["organizer_otp"]
            if session["otp"] == int(organizer_otp):
                return redirect(url_for("organizer_forpass_form"))
            else:
                flash("Wrong OTP. Please try again", "error")
                return redirect(url_for("organizer_otp"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/organizer_forpass_form")
def organizer_forpass_form():
    return render_template("organizer_forpass_form.html")


# organizer change password after otp verification
@app.route("/change_organizer_pass", methods=["POST"])
def change_organizer_pass():
    if request.method == "POST":
        if "organizer" in session:
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("organizer_forpass_form"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data = Organizer.query.filter_by(email=session["email"]).first()
                data.password = hash_pass
                db.session.commit()
                session.pop("organizer", None)
                session.pop("email", None)
                flash("Password changed successfully", "success")
                return redirect(url_for("organizer_log"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("organizer_forpass_form"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/add_event")
def add_event():
    if "organizer" in session:
        coOrganizer = Coorganizer.query.count()
        if not coOrganizer:
            flash("Add Co-organizer to be assigned first", "error")
            return redirect(url_for("organizerdash"))
        else:
            get_coOrganizer_data = Coorganizer.query.all()
            return render_template("add_event.html", data=get_coOrganizer_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/addevent", methods=["POST"])
def addevent():
    if request.method == "POST":
        if "organizer" in session:
            org_id = session["organizer_id"]
            name = request.form["name"]
            description = request.form["description"]
            date_str = request.form["date"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = request.form["time"]
            category = request.form["category"]
            coOrganizer = request.form["co-organizer"]
            today = date.today()
            if date_obj < today:
                flash(Markup("Selected date is older than today's date"), "error")
                return redirect(url_for("add_event"))
            data = Coorganizer.query.filter_by(name=coOrganizer).first()
            email = data.email
            name_check = Event.query.filter_by(name=name).first()
            if not name_check:
                event = Event(
                    name=name,
                    description=description,
                    date=date_str,
                    time=time,
                    category=category,
                    coorg_mail=email,
                    org_id=org_id,
                )
                db.session.add(event)
                db.session.commit()
                send_mail(
                    email,
                    "Event Alloted!",
                    "You have been assigned to co-ordinate the "
                    + str(name).upper()
                    + " event. Please login into your dashboard and check for the event details.",
                )
                flash("Event added successfully", "success")
                return redirect(url_for("organizerdash"))
            else:
                flash("Name already used", "error")
                return redirect(url_for("add_event"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/view_event")
def view_event():
    if "organizer" in session:
        events = Event.query.all()
        for i in events:
            data1 = Organizer.query.filter_by(id=i.org_id).first()
            i.org_id = data1.name
        return render_template("view_event.html", data=events)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/edit_event/<int:id>", methods=["GET", "POST"])
def edit_event(id):
    if "organizer" in session:
        event = Event.query.filter_by(id=id).first()
        get_coOrganizer_data = Coorganizer.query.all()
        if session["organizer_id"] == int(event.org_id):
            return render_template(
                "edit_event.html", data=event, coorg=get_coOrganizer_data
            )
        else:
            flash("You can only edit the events added by you", "error")
            return redirect(url_for("view_event"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/editevent/<int:id>", methods=["POST"])
def editevent(id):
    if request.method == "POST":
        if "organizer" in session:
            event = Event.query.filter_by(id=id).first()
            name = request.form["name"]
            description = request.form["description"]
            date_str = request.form["date"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = request.form["time"]
            category = request.form["category"]
            coOrganizer = request.form["co-organizer"]
            today = date.today()
            if date_obj < today:
                flash(Markup("Selected date is older than today's date"), "error")
                return redirect(url_for("view_event"))
            name_check = Event.query.filter_by(name=name).first()
            if not name_check:
                event.name = name
                event.description = description
                event.date = date_str
                event.time = time
                event.category = category
                if event.coorg_mail != coOrganizer:
                    event.coorg_mail = coOrganizer
                    db.session.commit()
                    send_mail(
                        coOrganizer,
                        "Event Alloted!",
                        "You have been assigned to co-ordinate the "
                        + str(name).upper()
                        + " event. Please login into your dashboard and check for the event details.",
                    )
                    flash("Event updated successfully", "success")
                    return redirect(url_for("organizerdash"))
                else:
                    db.session.commit()
                    flash("Event updated successfully", "success")
                    return redirect(url_for("organizerdash"))
            elif name_check.id == id:
                event.description = description
                event.date = date_str
                event.time = time
                event.category = category
                if event.coorg_mail != coOrganizer:
                    event.coorg_mail = coOrganizer
                    db.session.commit()
                    send_mail(
                        coOrganizer,
                        "Event Alloted!",
                        "You have been assigned to co-ordinate the "
                        + str(name).upper()
                        + " event. Please login into your dashboard and check for the event details.",
                    )
                    flash("Event updated successfully", "success")
                    return redirect(url_for("organizerdash"))
                else:
                    db.session.commit()
                    flash("Event updated successfully", "success")
                    return redirect(url_for("organizerdash"))
            else:
                flash("Name already used", "error")
                return redirect(url_for("view_event"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/del_event/<int:id>")
def del_event(id):
    if "organizer" in session:
        event = Event.query.filter_by(id=id).first()
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted successfully", "success")
        return redirect(url_for("view_event"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))
    
@app.route("/del_Org/<int:id>")
def del_Org(id):
    if "admin" in session:
        organization = Organization.query.filter_by(id=id).first()
        db.session.delete(organization)
        db.session.commit()
        flash("Organization deleted successfully", "success")
        return redirect(url_for("organizationsList"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("admin_log"))
    
@app.route("/del_Organizer/<int:id>")
def del_Organizer(id):
    if "admin" in session:
        organizer = Organizer.query.filter_by(id=id).first()
        db.session.delete(organizer)
        db.session.commit()
        flash("Organizer deleted successfully", "success")
        return redirect(url_for("organizersList"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("admin_log"))


@app.route("/add_coOrganizer")
def add_coOrganizer():
    if "organizer" in session:
        return render_template("add_coOrganizer.html")
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


# adding organizer
@app.route("/addcoOrganizer", methods=["POST"])
def addcoOrganizer():
    if request.method == "POST":
        if "organizer" in session:
            organization = session["organizer_organization"]
            organizer = session["organizer_name"]
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            email_check = Coorganizer.query.filter_by(email=email).first()
            if not email_check:
                phone_check = Coorganizer.query.filter_by(phone=phone).first()
                if not phone_check:
                    hash_pass = sha256_crypt.hash(email)
                    coOrganizer = Coorganizer(
                        name=name,
                        email=email,
                        phone=phone,
                        password=hash_pass,
                        organizer=organizer,
                    )
                    db.session.add(coOrganizer)
                    db.session.commit()
                    send_mail(
                        email,
                        "You are a Co-Organizer!",
                        "You have been successfully added as a CO-ORGANIZER under the organization "
                        + str(organization).upper()
                        + ". Please use your email as your password on your first login and change it later for security purposes",
                    )
                    flash("Co-Organizer added successfully", "success")
                    return redirect(url_for("organizerdash"))
                else:
                    flash("Phone Number already registered", "error")
                    return redirect(url_for("add_coOrganizer"))
            else:
                flash("Email ID already used", "error")
                return redirect(url_for("add_coOrganizer"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/view_coOrganizer")
def view_coOrganizer():
    if "organizer" in session:
        coorgs = Coorganizer.query.all()
        return render_template("view_coOrganizer.html", data=coorgs)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/del_coOrganizer/<int:id>")
def del_coOrganizer(id):
    if "organizer" in session:
        cidd = Coorganizer.query.filter_by(id=id).first()
        cemail = cidd.email
        event = Event.query.filter_by(coorg_mail=cemail).first()
        if not event:
            coOrganizer = Coorganizer.query.filter_by(id=id).first()
            db.session.delete(coOrganizer)
            db.session.commit()
            flash("Co-Organizer deleted successfully", "success")
            return redirect(url_for("view_coOrganizer"))
        else:
            flash("This Co-Organizer has events assigned", "error")
            return redirect(url_for("view_coOrganizer"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/send_alert")
def send_alert():
    if "organizer" in session:
        alerts = Alert.query.all()
        for i in alerts:
            org_name = Organizer.query.filter_by(id=i.org_id).first()
            i.org_id = org_name.name
        return render_template("send_alert.html", data=alerts)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/sendalert", methods=["POST"])
def sendalert():
    if request.method == "POST":
        if "organizer" in session:
            subject = request.form["subject"]
            message = request.form["message"]
            attendees = Alert.query.all()
            if attendees:
                for i in attendees:
                    send_mail(str(i),subject,message)
                flash("Alert message broadcasted", "success")
                return redirect(url_for("send_alert"))
            else:
                flash("Add atleast one attendee", "error")
                return redirect(url_for("send_alert"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("organizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/add_attendee/<string:email>")
def add_attendee(email):
    if "organizer" in session:
        data = Alert.query.filter_by(attendee=email).first()
        if not data:
            alert = Alert(attendee=email, org_id=session["organizer_id"])
            db.session.add(alert)
            db.session.commit()
            flash("Attendee added successfully", "success")
            return redirect(url_for("send_alert"))
        else:
            flash("Attendee already added", "error")
            return redirect(url_for("send_alert"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/del_attendee/<int:id>")
def del_attendee(id):
    if "organizer" in session:
        attendee = Alert.query.filter_by(id=id).first()
        db.session.delete(attendee)
        db.session.commit()
        flash("Attendee removed successfully", "success")
        return redirect(url_for("send_alert"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("organizer_log"))


@app.route("/coOrganizer_log", methods=["GET", "POST"])
def coOrganizer_log():
    return render_template("coOrganizer_log.html")


# co-organizer login
@app.route("/coOrganizerlog", methods=["POST"])
def coOrganizerlog():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        response = Coorganizer.query.filter_by(email=email).first()
        if not response:
            flash("Email ID not registered", "error")
            return redirect(url_for("coOrganizer_log"))
        else:
            checkpass = sha256_crypt.verify(password, response.password)
            if email == response.email and checkpass == True:
                session["coorganizer"] = True
                session["coorganizer_id"] = response.id
                session["coorganizer_name"] = response.name
                session["coorganizer_email"] = response.email
                session["coorganizer_phone"] = response.phone
                session["coorganizer_organizer"] = response.organizer
                flash("You were successfully logged in", "success")
                return redirect(url_for("coOrganizerdash"))
            else:
                flash("Invalid Credentials", "error")
                return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/coOrganizerdash")
def coOrganizerdash():
    if "coorganizer" in session:
        events = Event.query.filter_by(coorg_mail=session["coorganizer_email"]).count()
        judges = Judge.query.filter_by(coorg_mail=session["coorganizer_email"]).count()
        return render_template("coOrganizer_dash.html", data=[events, judges])
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/coOrganizer_profile")
def coOrganizer_profile():
    if "coorganizer" in session:
        return render_template("coOrganizer_profile.html")
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/coOrganizer_profile_update")
def coOrganizer_profile_update():
    if "coorganizer" in session:
        get_coOrganizer_data = Coorganizer.query.filter_by(
            id=session["coorganizer_id"]
        ).first()
        return render_template("coOrganizer_profupdate.html", data=get_coOrganizer_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


# coOrganizer profile update
@app.route("/update_coOrganizer_profile/<int:id>", methods=["POST"])
def update_coOrganizer_profile(id):
    if "coorganizer" in session:
        if request.method == "POST":
            name = request.form["name"]
            phno = request.form["phno"]
            if (
                name == session["coorganizer_name"]
                and phno == session["coorganizer_phone"]
            ):
                flash("No changes made", "warning")
                return redirect(url_for("coOrganizerdash"))
            else:
                data = Coorganizer.query.filter_by(id=id).first()
                phno_check = Coorganizer.query.filter_by(phone=phno).first()
                if phno_check:
                    if phno_check.id != id:
                        flash("Phone number is already used by someone else", "error")
                        data = Coorganizer.query.filter_by(id=id).first()
                        return render_template("coOrganizer_profupdate.html", data=data)
                    elif phno_check.id == id:
                        data.phone = phno
                        data.name = name
                        db.session.commit()
                        session.clear()
                        flash(
                            "Co-Organizer details updated successfully.Login again to see changes",
                            "success",
                        )
                        return redirect(url_for("coOrganizer_log"))
                else:
                    data.phone = phno
                    data.name = name
                    db.session.commit()
                    session.clear()
                    flash(
                        "Co-Organizer details updated successfully.Login again to see changes",
                        "success",
                    )
                    return redirect(url_for("coOrganizer_log"))
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/change_pass_coOrganizer")
def change_pass_coOrganizer():
    if "coorganizer" in session:
        get_coOrganizer_data = Coorganizer.query.filter_by(
            id=session["coorganizer_id"]
        ).first()
        return render_template(
            "change_pass_coOrganizer.html", data=get_coOrganizer_data
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


# coOrganizer change password after login
@app.route("/coOrganizer_change_pass/<string:email>", methods=["POST"])
def coOrganizer_change_pass(email):
    if request.method == "POST":
        if "coorganizer" in session:
            data = Coorganizer.query.filter_by(
                email=session["coorganizer_email"]
            ).first()
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("change_pass_coOrganizer"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data.password = hash_pass
                db.session.commit()
                flash("Password changed successfully", "success")
                return redirect(url_for("coOrganizerdash"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("change_pass_coOrganizer"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/coOrganizer_forpass")
def coOrganizer_forpass():
    return render_template("coOrganizer_forpass.html")


# coOrganizer forgot password
@app.route("/coOrganizer_send_otp", methods=["POST"])
def coOrganizer_send_otp():
    if request.method == "POST":
        email = request.form["email"]
        email_check = Coorganizer.query.filter_by(email=email).first()
        if email_check:
            session["coorganizer"] = True
            session["email"] = email_check.email
            otp = random.randint(000000, 999999)
            session["otp"] = otp
            send_mail(
                email,
                "OTP for Password change",
                "Dear Co-Organizer, your verification code is: " + str(otp),
            )
            flash("OTP sent", "success")
            return redirect(url_for("coOrganizer_otp"))
        else:
            flash(
                "Email ID not registered. Please check your email id or ask organizer to create a new account",
                "error",
            )
            return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/coOrganizer_otp")
def coOrganizer_otp():
    return render_template("coOrganizer_otp.html")


# Co-Organizer otp verification for forgot password
@app.route("/coOrganizer_verify", methods=["POST"])
def coOrganizer_verify():
    if request.method == "POST":
        if "coorganizer" in session:
            coOrganizer_otp = request.form["coOrganizer_otp"]
            if session["otp"] == int(coOrganizer_otp):
                return redirect(url_for("coOrganizer_forpass_form"))
            else:
                flash("Wrong OTP. Please try again", "error")
                return redirect(url_for("coOrganizer_otp"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/coOrganizer_forpass_form")
def coOrganizer_forpass_form():
    return render_template("coOrganizer_forpass_form.html")


# Co-Organizer change password after otp verification
@app.route("/change_coOrganizer_pass", methods=["POST"])
def change_coOrganizer_pass():
    if request.method == "POST":
        if "coorganizer" in session:
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("coOrganizer_forpass_form"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data = Coorganizer.query.filter_by(email=session["email"]).first()
                data.password = hash_pass
                db.session.commit()
                session.pop("coorganizer", None)
                session.pop("email", None)
                flash("Password changed successfully", "success")
                return redirect(url_for("coOrganizer_log"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("coOrganizer_forpass_form"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/coOrganizer_view_event")
def coOrganizer_view_event():
    if "coorganizer" in session:
        events = Event.query.filter_by(coorg_mail=session["coorganizer_email"])
        return render_template("coOrganizer_view_event.html", data=events)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/coOrganizer_event_page/<int:id>", methods=["POST"])
def coOrganizer_event_page(id):
    if "coorganizer" in session:
        get_event_data = Event.query.filter_by(id=id).first()
        get_judge_data = Judge.query.filter_by(event_id=id).all()
        part_data = Plist.query.filter_by(event_id=id).all()
        p_data = []
        for i in part_data:
            p_data.append(Participant.query.filter_by(id=i.part_id).first())

        return render_template(
            "coOrganizer_event_page.html",
            data=get_event_data,
            data2=get_judge_data,
            data3=part_data,
            data4=p_data,
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/coOrganizer_event_update/<int:id>", methods=["GET", "POST"])
def coOrganizer_event_update(id):
    if "coorganizer" in session:
        event = Event.query.filter_by(id=id).first()
        judge = Judge.query.filter_by(event_id=id).all()
        org_id = event.org_id
        organizer = Organizer.query.filter_by(id=org_id).first()
        return render_template(
            "coOrganizer_event_update.html",
            data=event,
            judge=judge,
            organizer=organizer,
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/coOrganizer_update_event/<int:id>", methods=["POST"])
def coOrganizer_update_event(id):
    if request.method == "POST":
        if "coorganizer" in session:
            event = Event.query.filter_by(id=id).first()
            name = request.form["name"]
            description = request.form["description"]
            date = request.form["date"]
            time = request.form["time"]
            category = request.form["category"]
            name_check = Event.query.filter_by(name=name).first()
            if not name_check:
                event.name = name
                event.description = description
                event.date = date
                event.time = time
                event.category = category
                db.session.commit()
                flash("Event updated successfully", "success")
                return redirect(url_for("coOrganizer_view_event"))
            elif name_check.id == id:
                event.description = description
                event.date = date
                event.time = time
                event.category = category
                db.session.commit()
                flash("Event updated successfully", "success")
                return redirect(url_for("coOrganizer_view_event"))
            else:
                flash("Name already used", "error")
                return redirect(url_for("coOrganizer_view_event"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/judge")
def judge():
    if "coorganizer" in session:
        events = Event.query.filter_by(coorg_mail=session["coorganizer_email"]).all()
        if not events:
            flash("No events assigned to you", "error")
            return redirect(url_for("coOrganizerdash"))
        else:
            return render_template("add_judge.html", data=events)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/add_judge", methods=["POST"])
def add_judge():
    if request.method == "POST":
        if "coorganizer" in session:
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            event = request.form["event"]
            email_check = Judge.query.filter_by(email=email).first()
            event_data = Event.query.filter_by(name=event).first()
            if not email_check:
                name_check = Judge.query.filter_by(name=name).first()
                if not name_check:
                    hash_pass = sha256_crypt.hash(email)
                    judge = Judge(
                        name=name,
                        email=email,
                        phone=phone,
                        event_id=event_data.id,
                        password=hash_pass,
                        coorg_mail=session["coorganizer_email"],
                    )
                    # event_data.judge = name
                    db.session.add(judge)
                    db.session.commit()
                    flash("Judge added successfully", "success")
                    return redirect(url_for("coOrganizerdash"))
                else:
                    flash("Name already used", "error")
                    return redirect(url_for("judge"))
            else:
                flash("Email ID already used", "error")
                return redirect(url_for("judge"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("coOrganizerlog"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


# participant view event
@app.route("/participant_view_event")
def participant_view_event():
    if "participant" in session:
        events = Event.query.all()
        return render_template("participant_view_event.html", data=events)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


# participant reg event
@app.route("/participant_event_register/<int:id>", methods=["GET", "POST"])
def participant_event_register(id):
    if "participant" in session:
        part_id = session["participant_id"]
        entry_check = Plist.query.filter_by(part_id=part_id, event_id=id).first()
        if entry_check is None:
            part = Plist(part_id=part_id, event_id=id)
            db.session.add(part)
            db.session.commit()
            flash("Event Registration Successful", "success")
            return redirect(url_for("participant_view_event"))
        else:
            flash("Already Registered", "error")
            return redirect(url_for("participant_view_event"))

    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


# judge login
@app.route("/judge_log", methods=["GET", "POST"])
def judge_log():
    return render_template("judge_log.html")


@app.route("/judgelog", methods=["POST"])
def judgelog():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        response = Judge.query.filter_by(email=email).first()
        if not response:
            flash("Email ID not registered", "error")
            return redirect(url_for("judge_log"))
        else:
            checkpass = sha256_crypt.verify(password, response.password)
            if email == response.email and checkpass == True:
                session["judge"] = True
                session["judge_id"] = response.id
                session["judge_name"] = response.name
                session["judge_email"] = response.email
                session["judge_phone"] = response.phone
                session["event_id"] = response.event_id
                flash("You were successfully logged in", "success")
                return redirect(url_for("judgedash"))
            else:
                flash("Invalid Credentials", "error")
                return redirect(url_for("judge_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/judgedash")
def judgedash():
    if "judge" in session:
        return render_template("judge_dash.html", data=0)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("judge_log"))


@app.route("/judge_profile")
def judge_profile():
    if "judge" in session:
        return render_template("judge_profile.html")
    else:
        flash("Session Expired", "error")
        return redirect(url_for("judge_log"))


@app.route("/judge_profile_update")
def judge_profile_update():
    if "judge" in session:
        get_judge_data = Judge.query.filter_by(id=session["judge_id"]).first()
        return render_template("judge_profupdate.html", data=get_judge_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("judge_log"))


# judge profile update
@app.route("/update_judge_profile/<int:id>", methods=["POST"])
def update_judge_profile(id):
    if "judge" in session:
        if request.method == "POST":
            name = request.form["name"]
            phno = request.form["phno"]
            data = Judge.query.filter_by(id=id).first()
            phno_check = Judge.query.filter_by(phone=phno).first()
            if phno_check:
                if phno_check.id != id:
                    flash("Phone number is already used by someone else", "error")
                    data = Judge.query.filter_by(id=id).first()
                    return render_template("judge_profupdate.html", data=data)
                elif phno_check.id == id:
                    data.phone = phno
                    data.name = name
                    db.session.commit()
                    session.clear()
                    flash(
                        "Judge details updated successfully.Login again to see changes",
                        "success",
                    )
                    return redirect(url_for("judge_log"))
            else:
                data.phone = phno
                data.name = name
                db.session.commit()
                session.clear()
                flash(
                    "Judge details updated successfully.Login again to see changes",
                    "success",
                )
                return redirect(url_for("judge_log"))
        else:
            session.clear()
            flash("Unauthorized access", "error")
            return redirect(url_for("home"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("judge_log"))


@app.route("/del_judge/<int:id>")
def del_judge(id):
    if "coorganizer" in session:
        judge = Judge.query.filter_by(id=id).first()
        db.session.delete(judge)
        db.session.commit()
        flash("Judge removed successfully", "success")
        return redirect(url_for("coOrganizerdash"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizerlog"))


@app.route("/change_pass_judge", methods=["GET", "POST"])
def change_pass_judge():
    if "judge" in session:
        get_judge_data = Judge.query.filter_by(id=session["judge_id"]).first()
        return render_template("change_pass_judge.html", data=get_judge_data)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("judge_log"))


# judge change password after login
@app.route("/judge_change_pass/<string:email>", methods=["POST"])
def judge_change_pass(email):
    if request.method == "POST":
        if "judge" in session:
            data = Judge.query.filter_by(email=email).first()
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("change_pass_judge"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data.password = hash_pass
                db.session.commit()
                flash("Password changed successfully", "success")
                return redirect(url_for("judgedash"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("change_pass_judge"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("judge_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/judge_forpass")
def judge_forpass():
    return render_template("judge_forpass.html")


# judge forgot password
@app.route("/judge_send_otp", methods=["POST"])
def judge_send_otp():
    if request.method == "POST":
        email = request.form["email"]
        email_check = Judge.query.filter_by(email=email).first()
        if email_check:
            session["judge"] = True
            session["email"] = email_check.email
            otp = random.randint(000000, 999999)
            session["otp"] = otp
            send_mail(
                email,
                "OTP for Password change",
                "Dear judge, your verification code is: " + str(otp),
            )
            flash("OTP sent", "success")
            return redirect(url_for("judge_otp"))
        else:
            flash(
                "Email ID not registered. Please check your email id or ask admin to create a new account",
                "error",
            )
            return redirect(url_for("judge_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/judge_otp")
def judge_otp():
    return render_template("judge_otp.html")


# judge otp verification for forgot password
@app.route("/judge_verify", methods=["POST"])
def judge_verify():
    if request.method == "POST":
        if "judge" in session:
            judge_otp = request.form["judge_otp"]
            if session["otp"] == int(judge_otp):
                return redirect(url_for("judge_forpass_form"))
            else:
                flash("Wrong OTP. Please try again", "error")
                return redirect(url_for("judge_otp"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("judge_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/judge_forpass_form")
def judge_forpass_form():
    return render_template("judge_forpass_form.html")


# judge change password after otp verification
@app.route("/change_judge_pass", methods=["POST"])
def change_judge_pass():
    if request.method == "POST":
        if "judge" in session:
            pass1 = request.form["pass1"]
            flag = 0
            while True:
                if len(pass1) < 8:
                    flag = -1
                    break
                elif not re.search("[a-z]", pass1):
                    flag = -1
                    break
                elif not re.search("[A-Z]", pass1):
                    flag = -1
                    break
                elif not re.search("[0-9]", pass1):
                    flag = -1
                    break
                elif not re.search("[_@$]", pass1):
                    flag = -1
                    break
                elif re.search("\\s", pass1):
                    flag = -1
                    break
                else:
                    flag = 0
                    break
            if flag == -1:
                flash("Not a Valid Password", "error")
                return redirect(url_for("judge_forpass_form"))
            pass2 = request.form["pass2"]
            if pass1 == pass2:
                hash_pass = sha256_crypt.hash(pass1)
                data = Judge.query.filter_by(email=session["email"]).first()
                data.password = hash_pass
                db.session.commit()
                session.pop("judge", None)
                session.pop("email", None)
                flash("Password changed successfully", "success")
                return redirect(url_for("judge_log"))
            else:
                flash("Passwords dont match", "error")
                return redirect(url_for("judge_forpass_form"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("judge_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participant_registered_event")
def participant_registered_event():
    if "participant" in session:
        event_names = []
        par_data = Plist.query.filter_by(part_id=session["participant_id"]).all()
        for i in par_data:
            data1 = Event.query.filter_by(id=i.event_id).first()
            event_names.append(data1)
        return render_template("participant_registered_event.html", data=event_names)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


@app.route("/unregister_event/<int:id>")
def unregister_event(id):
    if "participant" in session:
        part_id = session["participant_id"]
        del_p = Plist.query.filter_by(part_id=part_id, event_id=id).first()
        db.session.delete(del_p)
        db.session.commit()
        flash("Unregistered successfully", "success")
        return redirect(url_for("participantdash"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


@app.route("/judge_event")
def judge_event():
    if "judge" in session:
        event = Event.query.filter_by(id=session["event_id"]).first()
        participants = Plist.query.filter_by(event_id=session["event_id"]).all()
        for i in participants:
            pname = Participant.query.filter_by(id=i.part_id).first()
            i.pname = pname.name
        return render_template("judge_event.html", data=event, data2=participants)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("judge_log"))


@app.route("/add_score/<int:id>", methods=["POST"])
def add_score(id):
    if request.method == "POST":
        if "judge" in session:
            score = request.form["mark"]
            part_data = Plist.query.filter_by(id=id).first()
            part_data.score = score
            db.session.commit()
            return redirect(url_for("judge_event"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("judge_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/send_alert_coorganizer", methods=["GET", "POST"])
def send_alert_coorganizer():
    if "coorganizer" in session:
        events = Event.query.filter_by(coorg_mail=session["coorganizer_email"])
        return render_template("send_alert_coorganizer.html", data=events)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/coOrganizer_sendalert/<int:id>", methods=["GET", "POST"])
def coOrganizer_sendalert(id):
    if "coorganizer" in session:
        mail = []
        plist = Plist.query.filter_by(event_id=id).all()
        for i in plist:
            a = Participant.query.filter_by(id=i.part_id).first()
            mail.append(a.email)
        return render_template("coorg_event_send_alert.html", data=mail, data2=id)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/sendeventalert/<int:id>", methods=["POST"])
def sendeventalert(id):
    if request.method == "POST":
        if "coorganizer" in session:
            subject = request.form["subject"]
            messages = request.form["message"]
            mail = []
            plist = Plist.query.filter_by(event_id=id).all()
            for i in plist:
                a = Participant.query.filter_by(id=i.part_id).first()
                mail.append(a.email)
            recp = []
            for i in mail:
                recp.append(str(i))
            if not recp:
                flash("No Registrations Yet", "error")
                return redirect(url_for("coOrganizerdash"))
            message = Mail(
                from_email=("eventxsjec@gmail.com", "EventX"),
                to_emails=recp,
                subject=subject,
                html_content=messages,
            )
            sg = SendGridAPIClient(
                "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"
            )
            sg.send(message)
            flash("Alert message broadcasted", "success")
            return redirect(url_for("coOrganizerdash"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/view_judge")
def view_judge():
    if "coorganizer" in session:
        judges = Judge.query.all()
        for i in judges:
            data1 = Coorganizer.query.filter_by(email=i.coorg_mail).first()
            i.coorg_mail = data1.name
        return render_template("view_judge.html", data=judges)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/del_judge_list/<int:id>")
def del_judge_list(id):
    if "coorganizer" in session:
        jd = Judge.query.filter_by(id=id).first()
        if jd.event_id is None:
            judge = Judge.query.filter_by(id=id).first()
            db.session.delete(judge)
            db.session.commit()
            flash("Judge deleted successfully", "success")
            return redirect(url_for("view_judge"))
        else:
            flash("This Judge is assigned", "error")
            return redirect(url_for("view_judge"))
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/send_certificate", methods=["GET", "POST"])
def send_certificate():
    if "coorganizer" in session:
        events = Event.query.filter_by(coorg_mail=session["coorganizer_email"])
        return render_template("send_certificate.html", data=events)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


@app.route("/coOrganizer_sendcertificate/<int:id>", methods=["GET", "POST"])
def coOrganizer_sendcertificate(id):
    if "coorganizer" in session:
        mail = []
        plist = Plist.query.filter_by(event_id=id).all()
        for i in plist:
            a = Participant.query.filter_by(id=i.part_id).first()
            mail.append(a.email)
        return render_template("coorg_send_certificate.html", data=mail, data2=id)
    else:
        flash("Session Expired", "error")
        return redirect(url_for("coOrganizer_log"))


def rowToListContact(obj):
    lst = []
    data = Participant.query.filter_by(id=obj.part_id).first()
    name = data.name
    email = data.email
    lst.append(name)
    lst.append(email)
    lst.append("EventX")
    return lst


@app.route("/sendeventcertificate/<int:id>", methods=["POST"])
def sendeventcertificate(id):
    if request.method == "POST":
        if "coorganizer" in session:
            plist = Plist.query.filter_by(event_id=id).all()
            if len(plist) == 0:
                flash("No participants registered", "error")
                return redirect(url_for("coOrganizerdash"))
            si = io.StringIO()
            cw = csv.writer(si, delimiter=",")
            cw.writerow(["Name", "Email", "CourseName"])
            for row in plist:
                row = rowToListContact(row)
                cw.writerow(row)
                output = make_response(si.getvalue())
                output.headers[
                    "Content-Disposition"
                ] = "attachment; filename=participants.csv"
                output.headers["Content-type"] = "text/csv"
            flash("Alert message broadcasted", "success")
            return output
            # return redirect(url_for("coOrganizerdash"))
        else:
            flash("Session Expired", "error")
            return redirect(url_for("coOrganizer_log"))
    else:
        session.clear()
        flash("Unauthorized access", "error")
        return redirect(url_for("home"))


@app.route("/participant_view_result")
def participant_view_result():
    if "participant" in session:
        event_names = []
        event_results = []
        par_data = Plist.query.filter_by(part_id=session["participant_id"]).all()
        if not par_data:
            flash("No events registered", "error")
            return redirect(url_for("participantdash"))
        for i in par_data:
            sb = i.event_id
            data1 = Event.query.filter_by(id=sb).all()
            order = (
                Plist.query.filter_by(event_id=sb)
                .order_by(Plist.score.desc())
                .limit(2)
                .all()
            )
            for k in order:
                info = Participant.query.filter_by(id=k.part_id).first()
                cont = str(info.name + " (" + info.email + ")")
                k.details = cont
                db.session.commit()
            event_names.append(data1)
            event_results.append(order)
        return render_template(
            "part_view_results.html",
            data=event_names,
            data10=event_results,
            leng=len(event_names),
        )
    else:
        flash("Session Expired", "error")
        return redirect(url_for("participantlog"))


# logout function for all
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=9876)
