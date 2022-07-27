from .util import unpack_le_uint16_from, unpack_le_uint32_from
from ...constants import P2PKH_VERBYTE, P2SH_VERBYTES
from .enum import Enumeration
from .base58 import Base58
from .hash import hash160


class ScriptError(Exception):
    '''Exception used for script errors.'''


OpCodes = Enumeration("Opcodes", [
    ("OP_0", 0), ("OP_PUSHDATA1", 76),
    "OP_PUSHDATA2", "OP_PUSHDATA4", "OP_1NEGATE",
    "OP_RESERVED",
    "OP_1", "OP_2", "OP_3", "OP_4", "OP_5", "OP_6", "OP_7", "OP_8",
    "OP_9", "OP_10", "OP_11", "OP_12", "OP_13", "OP_14", "OP_15", "OP_16",
    "OP_NOP", "OP_VER", "OP_IF", "OP_NOTIF", "OP_VERIF", "OP_VERNOTIF",
    "OP_ELSE", "OP_ENDIF", "OP_VERIFY", "OP_RETURN",
    "OP_TOALTSTACK", "OP_FROMALTSTACK", "OP_2DROP", "OP_2DUP", "OP_3DUP",
    "OP_2OVER", "OP_2ROT", "OP_2SWAP", "OP_IFDUP", "OP_DEPTH", "OP_DROP",
    "OP_DUP", "OP_NIP", "OP_OVER", "OP_PICK", "OP_ROLL", "OP_ROT",
    "OP_SWAP", "OP_TUCK",
    "OP_CAT", "OP_SUBSTR", "OP_LEFT", "OP_RIGHT", "OP_SIZE",
    "OP_INVERT", "OP_AND", "OP_OR", "OP_XOR", "OP_EQUAL", "OP_EQUALVERIFY",
    "OP_RESERVED1", "OP_RESERVED2",
    "OP_1ADD", "OP_1SUB", "OP_2MUL", "OP_2DIV", "OP_NEGATE", "OP_ABS",
    "OP_NOT", "OP_0NOTEQUAL", "OP_ADD", "OP_SUB", "OP_MUL", "OP_DIV", "OP_MOD",
    "OP_LSHIFT", "OP_RSHIFT", "OP_BOOLAND", "OP_BOOLOR", "OP_NUMEQUAL",
    "OP_NUMEQUALVERIFY", "OP_NUMNOTEQUAL", "OP_LESSTHAN", "OP_GREATERTHAN",
    "OP_LESSTHANOREQUAL", "OP_GREATERTHANOREQUAL", "OP_MIN", "OP_MAX",
    "OP_WITHIN",
    "OP_RIPEMD160", "OP_SHA1", "OP_SHA256", "OP_HASH160", "OP_HASH256",
    "OP_CODESEPARATOR", "OP_CHECKSIG", "OP_CHECKSIGVERIFY", "OP_CHECKMULTISIG",
    "OP_CHECKMULTISIGVERIFY",
    "OP_NOP1",
    "OP_CHECKLOCKTIMEVERIFY", "OP_CHECKSEQUENCEVERIFY",
    ("OP_CHECKCOLDSTAKEVERIFY", 209)
])


# Paranoia to make it hard to create bad scripts
assert OpCodes.OP_DUP == 0x76
assert OpCodes.OP_HASH160 == 0xa9
assert OpCodes.OP_EQUAL == 0x87
assert OpCodes.OP_EQUALVERIFY == 0x88
assert OpCodes.OP_CHECKSIG == 0xac
assert OpCodes.OP_CHECKMULTISIG == 0xae

def _match_ops(ops, pattern):
    if len(ops) != len(pattern):
        return False
    for op, pop in zip(ops, pattern):
        if pop != op:
            # -1 means 'data push', whose op is an (op, data) tuple
            if pop == -1 and isinstance(op, tuple):
                continue
            return False

    return True

def P2PKH_address_from_hash160(hash160):
    return Base58.encode_check(P2PKH_VERBYTE + hash160)

def P2PKH_address_from_pubkey(pubkey):
    return P2PKH_address_from_hash160(hash160(pubkey))

def P2SH_address_from_hash160(hash160):
    return Base58.encode_check(P2SH_VERBYTES + hash160)

def script_type(script):
    TO_P2SH_OPS = [OpCodes.OP_HASH160, -1, OpCodes.OP_EQUAL]
    TO_PUBKEY_OPS = [-1, OpCodes.OP_CHECKSIG]

    TO_ADDRESS_OPS = [
        OpCodes.OP_DUP, OpCodes.OP_HASH160, -1,
        OpCodes.OP_EQUALVERIFY, OpCodes.OP_CHECKSIG
    ]

    TO_COLDSTAKE_OPS = [
        OpCodes.OP_DUP, OpCodes.OP_HASH160, OpCodes.OP_ROT,
        OpCodes.OP_IF, OpCodes.OP_CHECKCOLDSTAKEVERIFY, -1, OpCodes.OP_ELSE, -1,
        OpCodes.OP_ENDIF, OpCodes.OP_EQUALVERIFY, OpCodes.OP_CHECKSIG
    ]

    try:
        ops = Script.get_ops(script)
    except ScriptError:
        return None, None

    match = _match_ops

    if match(ops, TO_ADDRESS_OPS):
        return "p2pkh", P2PKH_address_from_hash160(ops[2][-1])
    if match(ops, TO_P2SH_OPS):
        return "p2ps", P2SH_address_from_hash160(ops[1][-1])
    if match(ops, TO_PUBKEY_OPS):
        return "pubkey", P2PKH_address_from_pubkey(ops[0][-1])
    if match(ops, TO_COLDSTAKE_OPS):
        return "coldstake", P2PKH_address_from_hash160(ops[7][-1])
    if ops and ops[0] == OpCodes.OP_RETURN:
        return "op_return", None

    return None, None

class Script:

    @classmethod
    def get_ops(cls, script):
        ops = []

        # The unpacks or script[n] below throw on truncated scripts
        try:
            n = 0
            while n < len(script):
                op = script[n]
                n += 1

                if op <= OpCodes.OP_PUSHDATA4:
                    # Raw bytes follow
                    if op < OpCodes.OP_PUSHDATA1:
                        dlen = op
                    elif op == OpCodes.OP_PUSHDATA1:
                        dlen = script[n]
                        n += 1
                    elif op == OpCodes.OP_PUSHDATA2:
                        dlen, = unpack_le_uint16_from(script[n: n + 2])
                        n += 2
                    else:
                        dlen, = unpack_le_uint32_from(script[n: n + 4])
                        n += 4
                    if n + dlen > len(script):
                        raise IndexError
                    op = (op, script[n:n + dlen])
                    n += dlen

                ops.append(op)
        except Exception:
            # Truncated script; e.g. tx_hash
            # ebc9fa1196a59e192352d76c0f6e73167046b9d37b8302b6bb6968dfd279b767
            raise ScriptError('truncated script')

        return ops

    @classmethod
    def opcode_name(cls, opcode):
        if OpCodes.OP_0 < opcode < OpCodes.OP_PUSHDATA1:
            return f'OP_{opcode:d}'
        try:
            return OpCodes.whatis(opcode)
        except KeyError:
            return f'OP_UNKNOWN:{opcode:d}'
