# What is it about
Collecting data from water meters to Amazon Timestream.

Meters connected to [Neptun ProW](https://sstcloud.ru/en/neptun19), which sends data to SST Cloud.
We will periodically read data from it's [API](https://api.sst-cloud.com/docs/) and save it to our database.

# Code preparation
We use [requests](https://requests.readthedocs.io/en/master/) library.
For ability to use it in other projects, we will upload it as a separate layer.
_The other way is bundle it with our code, for details see [Building package instruction](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-package-with-dependency)_

For library packing, do:
```
mkdir python
python3.9 -m pip install requests --target python
zip -r layer.zip python
```

# Obtaining SST Cloud token
There is two ways:
- Find the token in browser by _Network inspector_: after authorization in [SST Cloud web interface](https://web.sst-cloud.com) it will be used in `Authorization` header for each reqest to `api.sst-cloud.com`. Note that the word `Token` is not part of it.
- Get token by authorising via API https://api.sst-cloud.com/auth/login/. Check [docs](https://api.sst-cloud.com/docs/#/auth/login_create) for details.

# Setup

## Timestream
1. Open **Timestream** service in AWS console
1. Click **Create database** button (from service or _Databases_ page)
1. On "Create database" page:
   1. Choose **Standard database** in _Choose a configuration_
   1. Enter **Name**, for example `mydb`
   1. Confirm creation by clicking **Create database button**
   1. You will be redirected to _Databases_ page
1. Navigate to **Tables** page
1. Click **Create table**
1. On "Create table" page:
   1. Select `mydb` (previously created) in **Database name**
   1. Enter **Table name**, for example `meters`
   1. Enter **Memory store retention**, several weeks for example
   1. Enter **Magnetic store retention**, 10 years for example
   1. Select **Enable magnetic storage writes** option in _Magnetic Storage Writes_, if your are planning to import old data to this table
   (refer to [docs](https://docs.aws.amazon.com/timestream/latest/developerguide/writes.html#writes.timestamp-past-future) for details)
   1. Confirm creation by clicking **Create table** button

## Lambda function
1. Open **Lambda** service in AWS console
1. Open **Layers** page (from left menu in _Additional resources_)
1. Click **Create layer** button
1. On "Create layer" page:
   1. Enter **Name**, for example `python-requests`
   1. By clicking **Upload** button, upload previously created _layer.zip_ file
   1. Choose both *x86_64* and _arm64_ in **Compatible architectures**
   1. Choose _Python 3.9_ in **Compatible runtimes**
   1. Confirm creation by clicking **Create** button
1. Go to **Functions** page (from left menu)
1. Click **Create function** button
1. On "Create function" page:
   1. Choose **Author from scratch**
   1. Enter **Function name**, for example `read-water-meters`
   1. Choose `Python 3.9` **Runtime**
   1. Choose `arm64` **Architecture** (our code isn't platform-specific and this architecture offers lower cost)
   1. Confirm creation by **Create function** button (predefined value for _execution role_ `Create a new role with basic Lambda permissions` is good for us).
   We will be redirected to the lambda function page.
1. On function page, _Code_ tab
   1. Click **Add layer** button (in _Layers_ block)
   1. Choose **Custom layers** as _Layer source_
   1. Select `python-requests` in _Custom layers_
   1. Select latest available version in _Version_
   1. Click *Add** button.
   We will be redirected back to the lambda function page.
1. On function page, go to the _Configuration_ tab
   1. In section _General configuration_:
      - increase **Timeout** to 20 seconds
      - save
   1. Edit _Environment variables_ — add the following Key/Value pairs (_keep in mind, that value must be saved without leading or following whitespaces_), then save:
      - `DATABASE_NAME` / `mydb` (use the name from created Timestream database)
      - `TABLE_NAME` / `meters` (use the name of created table)
      - `LOCATION` / `home-sweet-home` (enter description for meters location)
      - `SST_CLOUT_TOKEN` / `your_token`


TODO: describe how to create&configure




### Environment variables
`TOKEN_SECRET_NAME`
TODO

## CloudWatch
Reduce retentions period for lambda function logs


### Policies
TODO
