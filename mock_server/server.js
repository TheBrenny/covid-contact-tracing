const crypto = require("crypto");
const Telnet = require("telnet-client");
const express = require("express");
const rl = require("readline-sync");

const keyspace = "0123456789";
const telnetConnectionParams = {
    host: "localhost",
    port: 5554,
    shellPrompt: "\n",
    timeout: 3000,
};
const telnetCommandParams = {
    shellPrompt: "\n",
    timeout: 3000,
};

const app = express();
const tnet = new Telnet();

const waitingAuths = [];
const waitingSchema = {
    phone_number: "",
    code: "",
    signature: "",
};


async function handleAuthRequest(req, res) {
    console.log(req.body);
    let waiter = {
        phone_number: req.body.phone_number,
        code: Array.from(crypto.randomBytes(6)).map(e => keyspace.charAt(parseInt(e) % keyspace.length)).join(""),
        signature: req.body.signature,
    };

    waitingAuths.push(waiter);

    // send to telnet
    let response = [
        "<#> Covid Contact Tracing",
        "Verifaction code: " + waiter.code,
        waiter.signature
    ].join("\\n");
    send("sms send 0459566685 " + response);

    res.status(200).end();
}

async function handleAuthCheck(req, res) {
    let phone = req.body.phone_number;
    let code = req.body.code;
    let signature = req.body.signature;

    let waiterIndex = waitingAuths.findIndex(e => e.phone_number === phone);
    if (waiterIndex >= 0) {
        let waiter = waitingAuths[waiterIndex];

        console.log(phone + " - " + waiter.phone_number);
        console.log(code + " - " + waiter.code);
        console.log(signature + " - " + waiter.signature);

        if (waiter.code === code && waiter.signature === signature) {
            waitingAuths.splice(waiterIndex, 1);
            res.status(200).json({
                message: "authed"
            }).end();
            return;
        }
    }
    res.status(400).end();
}

async function dataEntry(req, res) {

}

async function send(d) {
    try {
        return await tnet.exec(d, telnetCommandParams);
    } catch (e) {
        console.error(e);
    }
    return "";
}

async function end() {
    await tnet.end();
    await tnet.destroy();
    process.exit();
}

process.on("SIGINT", end);

(async function () {
    // setup telnet for Android emulation messaging
    try {
        await tnet.connect(telnetConnectionParams);
        await tnet.exec("help", telnetCommandParams);
    } catch (e) {
        console.error(e);
        process.exit(1);
    }

    let authCode = process.argv[2] || rl.question("auth ");
    let success = await send("auth " + authCode);
    console.log(success);

    // setup web server
    app.use(express.json());
    app.post("/auth_request_code", handleAuthRequest);
    app.post("/auth_check_code", handleAuthCheck);
    app.post("/data_entry", dataEntry);
    app.listen(80, () => {
        console.log("listening localhost:80");
    });
})();