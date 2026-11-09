# Car Showroom

A Tkinter desktop app for browsing a car showroom catalog.

## Requirements

- Python 3.10 or later
- MySQL Server, running locally or on a reachable host

The app creates the `car_showroom` database and its `cars` table automatically
when it starts. Configure the MySQL connection in `Trial01/.env` before
launching the app.

Create your local environment file from the example:

```powershell
Copy-Item .\Trial01\.env.example .\Trial01\.env
```

Edit `Trial01/.env` with your MySQL credentials. The file is ignored by Git and
should contain only local secrets. `Trial01/.env.example` lists the supported
settings. The JWT settings are reserved for JWT authentication; the current
desktop login does not use JWT.

The app loads `Trial01/.env` using Python's standard library, so no additional
package is needed for environment-file support. Environment variables already
set in Windows take precedence over values in the file.

## Install

From the repository root, open PowerShell and run:

```powershell
cd .\Trial01
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents virtual environment activation, you can invoke its Python
directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

From the `Trial01` directory, with the virtual environment activated:

```powershell
python Main.py
```

Or, without activating the environment:

```powershell
.\.venv\Scripts\python.exe Main.py
```

`Main.py` starts the app. The Tkinter screens are in `app/frontend`, business
logic is in `app/backend`, and repository implementations remain in
`app/repositories`.
