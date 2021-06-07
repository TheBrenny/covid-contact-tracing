import 'package:flutter/material.dart';
import 'package:flutter_platform_widgets/flutter_platform_widgets.dart';

class CovidButton extends StatelessWidget {
  static final Icon unknownButtonIcon = CovidButton._getUnknownButtonIcon();
  static final Image placeholderImage = CovidButton._getPlaceholderButtonImage();

  final String name;
  late final Widget image;

  CovidButton(
    String this.name, {
    Widget? image,
  }) : this.image = image ?? unknownButtonIcon;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      flex: 1,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 10, horizontal: 10),
        child: PlatformButton(
          onPressed: () => print("Pressed: " + (this.name)),
          child: Padding(
            padding: EdgeInsets.all(6),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Flexible(child: this.image),
                Text(
                  this.name,
                  style: DefaultTextStyle.of(context).style.apply(fontSizeFactor: 1.5),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  static Icon _getUnknownButtonIcon() {
    return Icon(Icons.device_unknown, color: Colors.red);
  }

  static Image _getPlaceholderButtonImage() {
    return Image.asset("images/placeholder.png");
  }
}
