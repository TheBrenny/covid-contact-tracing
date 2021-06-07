import 'package:flutter/material.dart';
import 'package:flutter_platform_widgets/flutter_platform_widgets.dart';

import 'covid_button.dart';

void main() => runApp(new MyApp());

class MyApp extends StatelessWidget {
  Widget build(BuildContext context) {
    return PlatformApp(
      title: 'COVID Contact Tracing',
      home: PlatformScaffold(
        appBar: PlatformAppBar(
          title: Center(
            child: Text("Covid Contact Tracing App!"),
          ),
        ),
        body: Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    Expanded(
                      flex: 2,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          CovidButton(
                            "Register",
                            image: CovidButton.placeholderImage,
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      flex: 1,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          CovidButton(
                            "COVID Information",
                            image: CovidButton.placeholderImage,
                          ),
                          CovidButton(
                            "Settings",
                            image: CovidButton.placeholderImage,
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      flex: 1,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          CovidButton(
                            "COVID Information",
                            image: CovidButton.placeholderImage,
                          ),
                          CovidButton(
                            "Settings",
                            image: CovidButton.placeholderImage,
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
