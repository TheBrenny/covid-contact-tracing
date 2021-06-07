import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter_platform_widgets/flutter_platform_widgets.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sms_autofill/sms_autofill.dart';

const String server = "http://10.0.2.2:80";
const Map<String, String> endpoints = {
  "requestAuth": server + "/auth_request_code",
  "checkAuth": server + "/auth_check_code",
  "dataEntry": server + "/data_entry",
};
final RegExp phoneRegex = RegExp(r"^04\d{8}$");

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({Key? key}) : super(key: key);
  _RegisterScreenState createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  late final String _signature;
  final TextEditingController _textCtrl = TextEditingController();
  bool _textValid = true;

  void dispose() {
    _textCtrl.dispose();
    super.dispose();
  }

  bool validatePhoneNumber(String number) {
    return phoneRegex.hasMatch(number);
  }

  @override
  Widget build(BuildContext context) {
    return PlatformScaffold(
      appBar: PlatformAppBar(
        title: Text("Registration"),
      ),
      body: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              autofocus: true,
              autocorrect: false,
              controller: _textCtrl,
              keyboardType: TextInputType.number,
              inputFormatters: [],
              decoration: InputDecoration(
                labelText: "Mobile Number",
                errorText: !_textValid ? "Enter a valid mobile phone number." : null,
              ),
            ),
            PlatformButton(
              child: PlatformText("Send SMS Code"),
              onPressed: () async {
                setState(() {
                  _textValid = validatePhoneNumber(_textCtrl.text);
                });
                if (!_textValid) return;

                _signature = await SmsAutoFill().getAppSignature;

                Navigator.pushNamed(context, '/register/activate', arguments: {
                  "phoneNumber": _textCtrl.text,
                  "signature": _signature,
                });

                Uri url = Uri.parse(endpoints['requestAuth']!);
                Map<String, String> data = {
                  "phone_number": _textCtrl.text,
                  "signature": _signature,
                };
                Map<String, String> headers = {
                  "Content-Type": "application/json",
                };
                http.Response response = await http.post(
                  url,
                  headers: headers,
                  body: jsonEncode(data),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class ActivateScreen extends StatefulWidget {
  const ActivateScreen({Key? key}) : super(key: key);
  _ActivateScreenState createState() => _ActivateScreenState();
}

class _ActivateScreenState extends State<ActivateScreen> {
  String _phoneNumber = "";
  String _signature = "";
  String _code = "";
  bool _codeHasError = false;

  @override
  void initState() {
    SmsAutoFill().listenForCode;
    super.initState();
  }

  @override
  void dispose() {
    SmsAutoFill().unregisterListener();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const length = 6;
    Map<String, String> args = ModalRoute.of(context)!.settings.arguments as Map<String, String>;
    _signature = args["signature"]!;
    _phoneNumber = args["phoneNumber"]!;

    return PlatformScaffold(
      appBar: PlatformAppBar(
        title: Text("Activation"),
      ),
      body: Padding(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            PinFieldAutoFill(
              codeLength: length,
              currentCode: _code,
              onCodeChanged: (v) {
                print(v);
                _code = v!;
                if (_code.length == length) _submitCode(context); //submit;
              },
              decoration: UnderlineDecoration(
                colorBuilder: FixedColorBuilder(Colors.black.withOpacity(0.3)),
                errorText: _codeHasError ? "Something went wrong when verifying the code." : null,
              ),
            ),
            PlatformButton(
              child: PlatformText("Activate"),
              onPressed: () => _submitCode(context),
            ),
          ],
        ),
      ),
    );
  }

  void _submitCode(BuildContext context) async {
    Uri url = Uri.parse(endpoints['checkAuth']!);
    Map<String, String> data = {
      "phone_number": _phoneNumber,
      "signature": _signature,
      "code": _code,
    };
    Map<String, String> headers = {
      "Content-Type": "application/json",
    };
    http.Response response = await http.post(
      url,
      headers: headers,
      body: jsonEncode(data),
    );

    print(response.statusCode);
    if (response.statusCode == 200) {
      _codeHasError = false;
      final prefs = await SharedPreferences.getInstance();
      prefs.setBool("registered", true);
      
      Navigator.popUntil(context, ModalRoute.withName('/'));
    } else {
      // say bad code?
      setState(() {
        _codeHasError = true;
      });
    }
  }
}
