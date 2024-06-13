# EventX
Welcome to EventX, an innovative end-to-end event management system designed to simplify and streamline the creation, management, and updating of personal and corporate events, regardless of their scale. EventX aims to provide organizations with a comprehensive application that centralizes all aspects of event management, ensuring a seamless experience from start to finish. This project was developed as the capstone of my engineering studies, serving as my final year project.

To have a glimpse of how this website works watch this https://youtu.be/QUijwQY3nM8

## Getting Started
1. Clone this repo into your local machine and open it using VS code or any other editor of your choice.
2. Open the terminal and create a virtual environment using the command "python -m venv yourenvname".
3. Activate the virtual env created using the command "yourenvname\Scripts\activate".
4. Once activated, install all the packages using the command "pip install -r requirements.txt".
5. Once all packages are installed create a .env file to two variables namely EMAIL & SECRET_KEY (This will be the email and it's secret key that you will be using to send emails). Steps to setup this is given below
6. Now you are ready to run the application. Type 'py app.py' in the terminal and hit enter.
7. A link like http://127.0.0.1:9876/ will pop up in the terminal. Press Ctrl and click on the link to open it in the browser to see the landing page of the application.
8. Note! Since we are using SQLite for database management you need to uncomment line 160(db.create_all()) in app.py the first time you run the command "py app.py" so that the tables are created. Comment the line once the tables are created so that new tables are not created again and again whenever you perform an action.

## Mail Auth
To set up the app password for the Gmail ID you will be used for sending emails:
1. Enable 2-factor authentication on your mail ID.
2. Go to this website https://myaccount.google.com/apppasswords
3. Enter the app name you wish and a app password will be created. You have to use this as the secret key and paste it in the .env file.
5. Yea! You are all set to send alerts using the mailing services.

## Operations that can be performed
### Main Admin
1. Access to this is not given directly on UI like others. Append '/admin_log' to the home url to access the main admin login page.
2. Credentials for the main admin are hard coded. Use 'mainadmin@gmail.com' and 'event123' as credentials to log in.
3. Add organization and organizer and notify the same via email respectively.
4. View the list of organization and organizer added.

### Organizer
1. Has to use his/her email and email as the password for the first login(As mentioned on the mail).
2. Change their password.
3. Update his/her Profile.
4. Add co-organizers first and then the events so that each event can be assigned a co-organzier to manage them.
5. Update & delete the events if necessary.
6. View the list of co-organziers and events added.
7. Broadcast announcements to guests and other VIPs using send alerts.
8. View payemnts made by the participants while registering for events.
9. Recover their password by using the forgot password on the login page.

### Co-Organizer
1. Has to use his/her email and email as the password for the first login(As mentioned on the mail).
2. Change their password.
3. Update his/her Profile.
4. Add judges and assign them to the alloted events.
5. Update & delete the judge assignment if necessary.
6. View the list of events alloted.
7. Broadcast announcements to the registered participants using send alerts.
8. Issue certificates to participants of respective events.
9. Recover their password by using the forgot password on the login page.

### Participant
1. Register and log in.
2. Update his/her profile.
3. Change their password if needed.
4. View the list of available events.
5. Register for events and make payments of entry fee.
6. View the list of registered events and unregister if necessary.
7. View results.
8. Recover their password by using the forgot password on the login page.

### Judge
1. Has to use his/her email and email as the password for the first login.
2. Change their password.
3. Update his/her Profile.
4. Enter the scores in the judging panel.
5. Recover their password by using the forgot password on the login page.

## Snapshots
### Home Page
![Screenshot (1989)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/cae7dc0f-d19d-4980-9157-b9f1f1692876)

### Main Admin Login
![Screenshot (1990)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/f40ae9c5-7ad6-444e-b6fa-62d893dca70c)

### Main Admin Dashboard
![Screenshot (1991)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/7274a074-c99a-45a3-84a3-30497d47c4c7)

### List of Organizations
![Screenshot (1992)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/08fef6ce-a644-4f29-915f-a7d1d355f4ca)

### List of Organizers
![Screenshot (1992)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/54e96523-772e-4f0f-88cf-1b3081fc4abc)

### Mail Notification on Successfull addition of Organization & Organizer
![Screenshot (2019)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/f6f2d621-ef9f-484d-8a81-9dca9bf07ac9)
![Screenshot (2020)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/a0989c1c-1f36-449a-928f-1733f932e66b)

### Organizer Dashboard
![Screenshot (1994)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/2d08e946-4ed1-4c8c-bb4b-fb7e160f4849)

### Add Co-Organzier
![Screenshot (1997)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/9302f138-98cc-4681-a6c2-ddf24a8ac2b5)

### Add Events
![Screenshot (1996)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/79bd3730-2200-4a88-8571-1a1f89a084d8)

### List of Events
![Screenshot (1995)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/57cfa9f4-0d58-41a6-80c4-0378a0c9a4c9)

### Mail Notification on co-organizer getting added & event getting alloted
![Screenshot (2021)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/bccada8d-1103-4b37-ab44-ace779bb2256)
![Screenshot (2022)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/0ba7de46-5772-4d38-a8fa-a044f85083b5)

### Send Announcements
![Screenshot (1998)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/c243d46c-0b13-4f66-9152-aaa34c955030)

### Razorpay Payment Dashboard
![Screenshot (1999)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/f64e41b8-041a-40d6-bf9d-50192c22c2c9)

### Update Profile
![Screenshot (2000)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/e096742f-bbe5-42cc-8df3-5e98c0687fd6)

### Change Password
![Screenshot (2001)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/17bf7f7b-2cbc-43e7-a0da-e7695608773e)

### Co-Organizer Dashboard
![Screenshot (2002)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/abc9c6a8-fc78-4ef0-b46d-259ef03b31f6)

### Alloted Events List
![Screenshot (2003)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/0007a978-97a8-4dbe-88fe-4686c4a40436)

### View & Update Event
![Screenshot (2004)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/1fe71b05-a3f8-4e55-96c3-6e0e9d5e7772)

### Add Judge
![Screenshot (2005)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/e1e67466-02dc-4431-b7a3-1a7455b121e0)

### Send Announcements to Participants
![Screenshot (2006)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/e2714d39-f240-4c0e-a458-fa40d8696ad8)
![Screenshot (2007)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/11b388d3-c96a-497d-9f4e-5beb45cce4cf)

### Issue Certificates
![Screenshot (2008)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/99a92d74-3f70-4f33-9338-8fd5f39e89ab)

### Mail Notification of event getting alloted to judge & certificate being sent & received by the participants
![Screenshot (2023)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/26bca673-88a4-45d9-8f92-64be8a9bec3b)
![Screenshot (2027)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/fc9272b7-9957-433a-888c-bbbf6a070c62)

### Participant Registration
![Screenshot (2017)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/21a043a8-734f-4145-85dc-7f6ab70c38e4)

### Participant Dashboard
![Screenshot (2009)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/13723bc0-0feb-48bd-9fa4-c2dcbdde6a96)

### Available Events List
![Screenshot (2010)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/d3667030-346b-4818-87c9-48c307e98b4b)

### Payment Gateway
![Screenshot (2011)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/8369e7b0-4d2b-4b59-a044-4c26bf37d95b)

### Registered Events List
![Screenshot (2012)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/6ddc1a1b-3c82-406d-84de-64538a9193f5)

### View Results
![Screenshot (2013)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/935bc358-9447-4526-960f-54aea45cb36e)

### Mail Notification on successfull Participant Registration & Payment
![Screenshot (2024)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/6421379e-82e1-4ed9-b773-226f63f5adef)
![Screenshot (2026)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/5de9b7bd-d666-4dcf-bbde-419898ebdeda)

### Participant QR on Registration
![QR](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/8e33ae38-02f0-4f34-9bc8-c343bf0b8a9f)

### Judge Dashboard
![Screenshot (2014)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/116d2764-070f-4e11-82cd-d60c7c86286a)

### Judging Panel
![Screenshot (2015)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/a9a42718-2906-43db-9883-4865031f9614)

### OTP Mail Notification for Forgot Password Functionality
![Screenshot (2025)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/fc3030f8-0897-40c4-828e-5ca59f7715e0)

### Sweet Alerts for every action performed
![Screenshot (2016)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/dae38dc6-6ff7-4685-a62b-8ecbb4803625)
![Screenshot (2018)](https://github.com/pranith-rao/End-to-End-Event-Management-System/assets/65860350/e69063f3-92a4-4fd4-819f-0960b6006e9a)

