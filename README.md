# Car Showroom

A Tkinter desktop app for browsing a car showroom catalog.

## Requirements

- Python 3.10 or later
- MySQL Server, running locally or on a reachable host

The app creates the `car_showroom` database and its `cars` table automatically
when it starts. By default, it connects to `127.0.0.1:3306` as `root` with
password `admin`.

To use different MySQL connection settings, set these environment variables
before launching the app:

- `CARSHOWROOM_DB_HOST`
- `CARSHOWROOM_DB_PORT`
- `CARSHOWROOM_DB_USER`
- `CARSHOWROOM_DB_PASSWORD`
- `CARSHOWROOM_DB_NAME`

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
python -m app.front
```

Or, without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m app.front
```
