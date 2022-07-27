RAPIDSD = ./src/rapidsd -printtoconsole -regtest -rpcuser=rpcuser -rpcpassword=111111
CLI = ./src/rapids-cli -regtest -rpcuser=rpcuser -rpcpassword=111111

ADDRESS_ISSUE = yKaKDLwGcvecU9CgNKd7fVpqg1NeEhyoP4
USDT_ADDRESS = xw3mizeu137xNBy7c3pAtMfyMT41V1ExCx
BTC_ADDRESS = y1px2qfDnaFbegyQGjVV5ycvQm5sJqTrag
BUY_ADDRESS = y2g3gqc5Wyet3gMBpy1jazrmq9gKM7y33q

DEX_SELL_ORDER = a35d544a9830dd99248ca69e4a5917037549255ff87de5d2800fe0dfd750edbe
DEX_ACCEPT = fc21fde75ec330fc1481dee2bcf36dfa5415b679233e95edfa46fb4fccadc2b7
DEX_PAY = 2454dde04255508d0276698c618480c78ac396dfe5396019f7dadd35f768e8f7


1) Send RPD to addresses

sendtoaddress ADDRESS_ISSUE 100
sendtoaddress USDT_ADDRESS 100
sendtoaddress BTC_ADDRESS 100
sendtoaddress BUY_ADDRESS 100


2) Issue tokens

sendtokenissuancefixed ADDRESS_ISSUE 1 1 0 "" "" "USDT Token" "USDT" "" "" 1000000

sendtokenissuancefixed ADDRESS_ISSUE 1 2 0 "" "" "Bitcoin" "BTC" "" "" 1000000


3) Send tokens to different addresses

sendtoken ADDRESS_ISSUE USDT_ADDRESS USDT 100

sendtoken ADDRESS_ISSUE BTC_ADDRESS BTC 100


4) Create DEX sell offer (USDT for RPD)

sendtokendexsell USDT_ADDRESS USDT 10 1 100 0.0001 1


5) Accept dex offer

sendtokendexaccept BUY_ADDRESS USDT_ADDRESS USDT 10


6) Pay for dex accept

sendtokendexpay BUY_ADDRESS USDT_ADDRESS USDT 10
