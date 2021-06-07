import 'dart:math' as Math;
import 'package:location/location.dart';

double getDistance(LocationData locA, LocationData locB) {
  int earthRadius = 6371;
  double deltaLon = _radians(locB.longitude! - locA.longitude!);
  double deltaLat = _radians(locB.latitude! - locA.latitude!);
  double a = Math.pow(Math.sin(deltaLat/2), 2) +
              Math.cos(_radians(locA.latitude!)) *
              Math.cos(_radians(locB.latitude!)) * 
              Math.pow(Math.sin(deltaLon/2), 2);
  double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  double d = earthRadius * c;
  return d;
}

double _radians(double deg) => deg * (Math.pi/180);

double getTimegap(LocationData a, LocationData b) {
  return b.time! - a.time!;
}