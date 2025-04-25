# go-fish-backend
The Python Flask backend for the GoFish application.

## Built By
Abhishek Paul

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

## Pre-Requisites

In order for the entire application to be functional end-to-end, please perform the following steps:

1. Create a new GoFish Firebase Project.
1. Go to Project Settings > Service Accounts.
2. Click on Generate new private key.
3. Download the `serviceAccountKey.json` file and store it in the root folder of this project (`/go-fish-backend`)


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
  - `200 OK` with weather forecast data of the place
  - `401 Unauthorized` if Auth header is invalid
  - Other 400 errors

### POST /auth/login

- **Body** - `firebase_token: [id_token]`
- **Response**
  - `200 OK` with json having a fresh JWT valid for 90 days
  - `401 Unauthorized` if firebase id_token is invalid
  - Other 400 errors