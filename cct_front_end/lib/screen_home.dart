import 'package:cct_front_end/covid_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_platform_widgets/flutter_platform_widgets.dart';
import 'package:shared_preferences/shared_preferences.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _registered = false;

  void initState() {
    super.initState();
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
                              print("registered: " + _registered.toString());
                              print("snapshot:   " + (snapshot.data!).toString());

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
