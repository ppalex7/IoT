# What is it about
Collecting data from water meters to Amazon Timestream.

Meters connected to [Neptun ProW](https://sstcloud.ru/en/neptun19), which sends data to SST Cloud.
We will periodically read data from it's [API](https://api.sst-cloud.com/docs/) and save it to our database.

# Setup

## Timestream
TODO, setup

## Lambda function
1. Open Lambda service in AWS console
1. Click **Create function** button
1. On "Create function" page:
   1. Choose **Author from scratch**
   1. Enter **Function name**, for example `read-water-meters`
   1. Choose `Python 3.9` **Runtime**
   1. Choose `arm64` **Architecture** (our code isn't platform-specific and this architecture offers lower cost)
   1. Confirm creation by **Create function** button (predefined value for _execution role_ `Create a new role with basic Lambda permissions` is good for us).
   We will be redirected to lambda function page.



TODO: describe how to create&configure

[Building package instruction](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-package-with-dependency)


### Environment variables
`TOKEN_SECRET_NAME`
TODO

### Policies
TODO
