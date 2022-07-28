RAPIDSD = ./src/rapidsd -printtoconsole -regtest -rpcuser=rpcuser -rpcpassword=111111
CLI = ./src/rapids-cli -regtest -rpcuser=rpcuser -rpcpassword=111111

ADDRESS_ISSUE = yKaKDLwGcvecU9CgNKd7fVpqg1NeEhyoP4
USDT_ADDRESS = xw3mizeu137xNBy7c3pAtMfyMT41V1ExCx
BTC_ADDRESS = y1px2qfDnaFbegyQGjVV5ycvQm5sJqTrag
BUY_ADDRESS = y2g3gqc5Wyet3gMBpy1jazrmq9gKM7y33q

TOKEN_USDT_SELL = 1c04a21209678298e58debdf1a86d89ff07e5342fc0fcfc1448f510cfceb3d07
TOKEN_BTC_SELL = 05a12dda3cae432ce35c2fc0796fcb2ab8019bf49debd6995f9cf095d2c4aa1b
TOKEN_CLOSE_BY_PRICE = 53d6a9f28b9dd0dd000f31ee690124bbd16be835d25bc785831dc1a828aa9aef


1) Create order for USDT/BTC

sendtokentrade USDT_ADDRESS USDT 1 BTC 1


2) Create order for BTC/USDT

sendtokentrade BTC_ADDRESS BTC 1 USDT 1



sendtokentrade
sendtokencanceltradesbyprice
sendtokencanceltradesbypair
sendtokencancelalltrades
