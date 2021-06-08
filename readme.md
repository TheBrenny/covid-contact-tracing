# Covid Tracker
> Passively and securely track your location so when a new hotspot is defined, you can become notified if you've been exposed!

## Requirements

Client side:
- `adb`
- `flutter`
- `dart`
  - `nodejs` for testing

Server side:
- `python3`
- `pip`

## Installation

### Front End:
~~Download from the Google Play Store or the Apple App Store~~

Otherwise:
```shell
$ cd cct_front_end
$ flutter build apk
$ adb install build\app\outputs\apk\release\app-release.apk
```

### Front End Mock Server

```shell
$ cd mock_server
$ npm install
```

### Server:
```shell
$ pip install -r requirements.txt
```

## Usage

- Run server: `python3 server.py`
- Run app: `flutter run`
- Run mock server: `cd mock_server && npm start`
