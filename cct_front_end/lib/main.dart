import 'package:cct_front_end/screen_home.dart';
import 'package:cct_front_end/screen_register.dart';
import 'package:flutter/material.dart';
import 'package:flutter_platform_widgets/flutter_platform_widgets.dart';

void main() => runApp(new RootApp());

class RootApp extends StatelessWidget {
  Widget build(BuildContext context) {
    return PlatformApp(
      title: 'COVID Contact Tracing',
      initialRoute: '/',
      routes: {
        '/': (ctx) => HomeScreen(key: GlobalKey()),
        '/register': (ctx) => RegisterScreen(),
        '/register/activate': (ctx) => ActivateScreen(),
        // '/mydata': (ctx) => MyDataScreen(),
      },
    );
  }
}
