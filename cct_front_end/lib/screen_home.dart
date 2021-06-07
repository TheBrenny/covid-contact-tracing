import 'dart:async';

import 'package:cct_front_end/covid_button.dart';
import 'package:cct_front_end/tools.dart' as tools;
import 'package:flutter/material.dart';
import 'package:flutter_platform_widgets/flutter_platform_widgets.dart';
import 'package:location/location.dart';
import 'package:location_permissions/location_permissions.dart' as lp;
import 'package:shared_preferences/shared_preferences.dart';

const maxDistance = 1; // 1km
const maxTimegap = 30 * 1000; // 30 seconds

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _registered = false;
  Location _location = new Location();
  LocationData? _lastLocation;
  bool _serviceEnabled = false;
  late StreamSubscription<LocationData> _locationListener;
  PermissionStatus? _permissionGranted;

  void initState() {
    super.initState();
    _initLocationService();
  }

  void dispose() {
    super.dispose();
    // _locationListener.cancel();
  }

  void _initLocationService() async {
    await _location.changeSettings(
      distanceFilter: 0,
      interval: 17 * 1000,
      accuracy: LocationAccuracy.high,
    ); // 100 metre distance and one minute interval

    _serviceEnabled = await _location.serviceEnabled();
    if (!_serviceEnabled) {
      _serviceEnabled = await _location.requestService();
      if (!_serviceEnabled) return;
    }

    _permissionGranted = await _location.hasPermission();
    if (_permissionGranted == PermissionStatus.deniedForever) return;
    if (_permissionGranted == PermissionStatus.denied) {
      _permissionGranted = await _location.requestPermission();
      if (_permissionGranted != PermissionStatus.granted) return;
    }

    _locationListener = _location.onLocationChanged.listen((LocationData loc) {
      // use it somehow -- store and send to the server?
      if (_lastLocation == null)
        _updateLocation(loc);
      else {
        print(tools.getDistance(_lastLocation!, loc));
        bool update = tools.getDistance(_lastLocation!, loc) > maxDistance;
        update = update && (tools.getTimegap(_lastLocation!, loc) > maxTimegap);
        if (update) _updateLocation(loc);
      }
    });
    _location.enableBackgroundMode(enable: true).catchError((err) async {
      if (err.code == "PERMISSION_DENIED_NEVER_ASK") {
        bool showRationale = await lp.LocationPermissions().shouldShowRequestPermissionRationale(permissionLevel: lp.LocationPermissionLevel.locationAlways);
        if(showRationale) {
          // TODO: Actually show a rationale for spying on the user. it's legit, I swear.
        }
        return lp.LocationPermissions().openAppSettings();
      } else
        throw err;
    });
  }

  void _updateLocation(LocationData loc) {
    _lastLocation = loc;
    print(loc.accuracy);
    print(loc.longitude);
    print(loc.latitude);
    print(DateTime.fromMillisecondsSinceEpoch(loc.time!.toInt()));
    print(loc.provider);
  }

  void _handleRegistration(BuildContext context) async {
    await Navigator.pushNamed(context, '/register');
    setState(() {});
  }

  void _showMyData(BuildContext context) {
    Navigator.pushNamed(context, '/mydata');
  }

  @override
  Widget build(BuildContext context) {
    return PlatformScaffold(
      appBar: PlatformAppBar(
        title: Center(
          child: Text("Covid Contact Tracing App!"),
        ),
      ),
      body: Padding(
        padding: EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  Expanded(
                    flex: 3,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        FutureBuilder(
                          future: SharedPreferences.getInstance().then((prefs) => (prefs.getBool("registered") ?? false)),
                          builder: (BuildContext context, AsyncSnapshot<bool> snapshot) {
                            Widget widget;

                            if (snapshot.hasData) {
                              _registered = snapshot.data!;

                              if (_registered) {
                                widget = CovidButton(
                                  "My Location Data",
                                  () => _showMyData(context),
                                  fontSizeFactor: 1.5,
                                );
                              } else {
                                widget = CovidButton(
                                  "Register",
                                  () => _handleRegistration(context),
                                  fontSizeFactor: 1.5,
                                );
                              }
                            } else if (snapshot.hasError) {
                              widget = Icon(Icons.error_outline, color: Colors.red);
                            } else {
                              widget = CircularProgressIndicator();
                            }

                            return widget;
                          },
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        CovidButton(
                          "COVID Information",
                          () => print("Pressed: R"),
                        ),
                        CovidButton(
                          "About",
                          () => print("Pressed: R"),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        CovidButton(
                          "Help",
                          () => print("Pressed: R"),
                        ),
                        CovidButton(
                          "Settings",
                          () async {
                            SharedPreferences.getInstance().then((prefs) => prefs.clear());
                            setState(() {});
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/**
 * These are the buttons that are required. (In no particular order)
 * - Help
 * - About
 * - COVID Information
 * - Register // My Data
 * - Settings
 */
