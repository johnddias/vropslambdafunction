# vropslambdafunction
AWS Lambda Function for Alexa Trigger

Works with vropsrelay.py installed as a "DZ" to allow the function indirect access to vR Ops API.  See https://github.com/johnddias/vropsrelay for information.

This function leverages third-party Python modules.  You will need to upload the zip file to your lambda instance, which contains:

  rainbow.py - the lambda function code
  contents of venv/lib/python2.7/site-packages
  contents of venv/lib64/pyton2.7/site-packages

Be sure to configure rainbow.py with the correct URL for your vropsrelay!
