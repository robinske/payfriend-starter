# Payment Authorization with Authy

Sample application that shows how to use Authy push authorization to validate actions like payment transactions.

[Demo video showing how the application works](https://s3-us-west-1.amazonaws.com/krobinson.me/files/payfriend.gif)

## Create an Authy Application

Sign up for a free Twilio account and create an Authy application in the  console:
https://www.twilio.com/console/authy/applications

Copy `.env.example` to `.env` and add your `AUTHY_API_KEY`.

<img width="775" alt="screen shot 2018-12-07 at 3 37 50 pm" src="https://user-images.githubusercontent.com/3673341/49674022-16a6ac80-fa36-11e8-9d28-fb7c8d9d62a1.png">

## Install

On Mac/Linux:

    python3 -m venv venv
    . venv/bin/activate

Or on Windows cmd:

    py -3 -m venv venv
    venv\Scripts\activate.bat

Install Requirements:

    pip install -r requirements.txt

## Run

    export FLASK_APP=payfriend
    export FLASK_ENV=development
    flask init-db
    flask run

Or on Windows cmd:

    set FLASK_APP=payfriend
    set FLASK_ENV=development
    flask init-db
    flask run


You'll need a publicly accessible route that Authy can access. Download [ngrok](https://ngrok.com/) and run:

    ngrok http 5000

Copy the Forwarding url:
<img width="757" alt="screen shot 2018-12-07 at 3 41 47 pm" src="https://user-images.githubusercontent.com/3673341/49674178-a3516a80-fa36-11e8-9b36-ddb7726e896e.png">

Head back to the [Authy Console](https://www.twilio.com/console/authy/applications) and update your Application's Push Authentication callback URL with `/payments/callback` appended.

<img width="1071" alt="screen shot 2018-12-07 at 3 44 42 pm" src="https://user-images.githubusercontent.com/3673341/49674279-0c38e280-fa37-11e8-910f-9ca15b27309e.png">

Open http://127.0.0.1:5000 in a browser.
