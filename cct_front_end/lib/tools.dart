import 'dart:convert';
import 'dart:math' as Math;
import 'package:location/location.dart';
import 'package:shared_preferences/shared_preferences.dart';

const String server = "https://pfs-cct-demo.herokuapp.com";

class Endpoint {
  static const Endpoint requestAuth = Endpoint._("/auth_request_code");
  static const Endpoint checkAuth = Endpoint._("/auth_check_code");
  static const Endpoint dataEntry = Endpoint._("/data_entry");

  final String route;
  const Endpoint._(this.route);

  String get url => server + route;
}

const int fourteenDays = 14 * 24 * 60 * 60 * 1000;

double getDistance(LocationData locA, LocationData locB) {
  int earthRadius = 6371;
  double deltaLon = _radians(locB.longitude! - locA.longitude!);
  double deltaLat = _radians(locB.latitude! - locA.latitude!);
  double a = Math.pow(Math.sin(deltaLat / 2), 2) + Math.cos(_radians(locA.latitude!)) * Math.cos(_radians(locB.latitude!)) * Math.pow(Math.sin(deltaLon / 2), 2);
  double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  double d = earthRadius * c;
  return d;
}

double _radians(double deg) => deg * (Math.pi / 180);

double getTimegap(LocationData a, LocationData b) {
  return b.time! - a.time!;
}

Future<bool> isRegistered() async {
  return getPhoneNumber().then((value) => value != null);
}

Future<String?> getPhoneNumber() async {
  return SharedPreferences.getInstance().then((value) => value.getString("phone_number")).catchError((e) {
    print(e);
    return null;
  });
}

Future<bool> setPhoneNumber(String number) async {
  return SharedPreferences.getInstance().then((p) => p.setString("phone_number", number));
}


Future<List<String>?> getLocations() async {
  return await SharedPreferences.getInstance().then((value) => value.getStringList("locations")).catchError((e) {
    print(e);
    return null;
  });
}

Future<String?> addLocation(LocationData loc) async {
  List<String>? locs = (await getLocations()) ?? [];
  String locJson = jsonEncode({
    "lon": loc.longitude,
    "lat": loc.latitude,
    "time": loc.time!.toInt(),
  });
  locs.add(locJson);
  return SharedPreferences.getInstance().then((value) => value.setStringList("locations", locs)).then((success) => success ? locJson : null);
}

Future<List<String>?> removeOldLocations() async {
  List<String>? locs = (await getLocations()) ?? [];
  locs.removeWhere((e) => jsonDecode(e).time < DateTime.now().millisecondsSinceEpoch - fourteenDays);
}
