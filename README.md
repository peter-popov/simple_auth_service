Simple Authentication Service Example
====================

Example of an Auth service using python Flask and client tokens

Run container
---------------------
Make sure that docker is installed. Build docker image and start service on port 5000:
    
    ➜ docker-compose up

Open [localhost:5000/apidocs](http://localhost:5000/apidocs) to see the Swagger documentation. Use provided postman collection for some manual tests.


Run API tests
---------------------
First run the container, tests are run agains the locally running service. You need to restart the service before running the test suit.

Make sure that pyhton 3.x and venv are installed. And then do the following in the project root:

    ➜ python3 -m venv testenv
    ➜ source testenv/bin/activate
    ➜ pip install -r requirements.txt
    ➜ py.test test/scenarios

You should see the follwoing output:
![](/docs/img/test_output.png)

Main design decisions
---------------------
Main goal was to desing a proper APIs flow. Many corners were cut.

### python 3.x + Flask
Would not do this for real production servie :)
Other dependecies:
- [flask_httpauth](https://flask-httpauth.readthedocs.io/en/latest/) for conveniet auth decorators
- [itsdangerous](https://pythonhosted.org/itsdangerous/) for [JWS](https://en.wikipedia.org/wiki/JSON_Web_Signature) tokens
- [tavern](https://taverntesting.github.io/) for API testing
- [flasgger](https://github.com/flasgger/flasgger) for generating swagger documentation

### We use client side tokens for everything
In has pros and cons in general. But in this case allowed creating secure API without much codding

### No schema validation... yet
Didn't do it in the code. I would fully rely on swagger for this. The schema has to be written diligently for this to work. For which I didn't have enough time. I added simplified swagger schema to show how it can be done in principle.

### Fake user DB
It's just a dictionaly in memeory. Can easily be extended to use any DB.

### Fake email
Since I don't have SMTP server I fake email related feature. All APIs which suppose to send emails will simply expose the verification link in the response. Obviously it's not how it should be done.

### Fake MFA device
This could have been done actually. I checked this [library](https://pyotp.readthedocs.io/en/latest/) and it seems to be a perfect fit and even support Goole Authenticator or Authy. But again would take some extra time to figure out how it works.

Insted we fake MFA device. User can send device ID and one time password is always assumed to be `deviceID + 17`.

API sequences
---------------------
![](/docs/img/signup.png)
![](/docs/img/login.png)
![](/docs/img/set_mfa.png)
