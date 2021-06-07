import 'package:flutter/material.dart';
import 'package:flutter_platform_widgets/flutter_platform_widgets.dart';

class CovidButton extends StatelessWidget {
  static final Widget placeholderImage = CovidButton._getPlaceholderButtonImage();

  final String name;
  final void Function() onPressed;
  late final Widget image;
  late final double fontSizeFactor;

  CovidButton(
    String this.name,
    void Function() this.onPressed, {
    double? fontSizeFactor,
    Widget? image,
    Key? key,
  })  : this.image = image ?? placeholderImage,
        this.fontSizeFactor = fontSizeFactor ?? 1.0,
        super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 16, horizontal: 16),
        child: PlatformButton(
          onPressed: this.onPressed,
          child: Padding(
            padding: EdgeInsets.all(6),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Flexible(
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: this.image,
                  ),
                ),
                Text(
                  this.name,
                  style: DefaultTextStyle.of(context).style.apply(fontSizeFactor: this.fontSizeFactor),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  static Widget _getPlaceholderButtonImage() {
    return Image.asset("images/placeholder.png");
  }
}