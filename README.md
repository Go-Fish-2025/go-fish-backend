# go-fish-backend
The Python [Flask](https://flask.palletsprojects.com/en/stable/) backend for the GoFish application.

## Built By
Abhishek Paul

## Pre-Requisites

In order for the entire application to be functional end-to-end, please perform the following steps:

### Downloading Firebase Service Account Key

1. Create a new GoFish [Firebase](https://firebase.google.com/) Project. The same one you will create or have created for the [mobile app](https://github.com/Go-Fish-2025/go-fish-mobile-app/tree/main).
2. Go to Project Settings > Service Accounts.
3. Click on Generate new private key.
4. Download the `serviceAccountKey.json` file and store it in the root folder of this project (`/go-fish-backend`)

### Getting the Fishial API Key

1. Create a developers account in [Fishial AI](https://docs.fishial.ai/api).
2. Generate an API Key.
3. You need to then get the Fishial API Key ID and Secret Key and paste them [here](https://github.com/Go-Fish-2025/go-fish-backend/blob/eea4486e78219aa076050df5115cf6ad6b8822bc/routes/fish.py#L13).

### Setting the server address in the mobile app
Once your backend is up and running (locally or deployed), make sure you enter its complete address with the port number (5001) in the android mobile app code so that they can communicate with each other. You need to just replace the url in [this](https://github.com/Go-Fish-2025/go-fish-mobile-app/blob/1b5199a8bb6967818b7bd11ca703a96728bf85f7/app/src/main/java/com/garlicbread/gofish/retrofit/RetrofitInstance.kt#L10) line 

## Installation and Execution

You can clone the repo using the command given below,

```bash
git clone https://github.com/Go-Fish-2025/go-fish-backend.git
```
or download a zip file of this repo.

Once, you're in the repository in your terminal, type the following commands

### Create a virtual environment

```bash
python3 -m venv venv
```

### Activate the virtual environment

```bash
source venv/bin/activate
```

### Install all the required dependencies

```bash
pip3 install -r requirements.txt
```

### Run the application

```bash
python3 server.py
```

This will run the server in port 5001.

**Note**<br>
The above instructions are mentioned for macOS / Linux systems. Run the appropriate commands if you are using a Windows System.

**Assumption**<br>
You have python3 and pip3 available in your system.
If not, you can get it from [Python Downloads](https://www.python.org/downloads/) and
[Pip Installation](https://pip.pypa.io/en/stable/installation/) respectively.

## API Endpoints

### POST /fish/identify

- **Headers** - `Authorization: Bearer [JWT]`
- **FormData** - Fish image in 'file' field
- **Response**
  - `200 OK` with a fish details json
  - `401 Unauthorized` if Auth header is invalid
  - Other 400 errors

### GET /weather

- **Headers** - `Authorization: Bearer [JWT]`
- **Query Params**
  - `location`: City / Region Name
  - `latitide`: Latitude of a location
  - `longitude`: Longitude of a location
  - `timezone`: Timezone the data is to be returned in
  - Either (latitude, longitude, timezone) or (location) needs to be present.
- **Response**
  - `200 OK` with weather forecast json data of the place
  - `401 Unauthorized` if Auth header is invalid
  - Other 400 errors

### POST /auth/login

- **Body** - `firebase_token: [id_token]`
- **Response**
  - `200 OK` with json having a fresh JWT valid for 90 days
  - `401 Unauthorized` if firebase id_token is invalid
  - Other 400 errors
