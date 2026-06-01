from enum import Enum
class TOKEN_KIND(Enum):
    CHAR = 1
    DELIM = 2
    #HASH = 2
    #STAR = 3
    #UNDERSCORE = 4
    BACK_SLASH = 5
    NEW_LINE = 6
    SPACE = 7
    EOF = 8

class token:
    def __init__(self, token_kind, token = "", lc = None, count = 0):
        self.token_kind = token_kind
        self.token = token
        self.lc = lc
        self.count = count

def toknize(str):
    token_array = []
    i = 0
    while i < len(str):
        match str[i]:
            case '#':
                hash_count = 0
                for j in range(i, len(str)):
                    if str[j] != '#':
                        break
                    hash_count = hash_count + 1
                if hash_count > 6:
                    token_array = token_array + [token(TOKEN_KIND.CHAR, str[i]) for _ in range(hash_count)]
                else:
                    token_array.append(token(TOKEN_KIND.DELIM, str[i], i, hash_count))
                i = i + hash_count
            case '*':
                star_count = 0
                for j in range(i, len(str)):
                    if str[j] != '*':
                        break
                    star_count = star_count + 1
                token_array.append(token(TOKEN_KIND.DELIM, str[i], i, star_count))
                i = i + star_count
            case '_':
                underscore_count = 0
                for j in range(i, len(str)):
                    if str[j] != '_':
                        break
                    underscore_count = underscore_count + 1
                token_array.append(token(TOKEN_KIND.DELIM, str[i], i, underscore_count))
                i = i + underscore_count
            case '\\':
                token_array.append(token(TOKEN_KIND.BACK_SLASH, str[i], i))
                i = i + 1
            case '\n':
                token_array.append(token(TOKEN_KIND.NEW_LINE, str[i], i))
                i = i + 1
            case ' ':
                token_array.append(token(TOKEN_KIND.SPACE, str[i], i))
                i = i + 1
            case _:
                token_array.append(token(TOKEN_KIND.CHAR, str[i], i))
                i = i + 1
    token_array.append(token(TOKEN_KIND.EOF))
    return token_array
    
def token_peek(token_array):
    return token_array[0]

def token_next(token_array):
    return token_array[1]

# maybe can optimize this with a hashtable
def search_through_stack(token_stack, token):
    i = 0
    for tok in reversed(token_stack):
        if token.token == tok.token and abs(token.count - tok.count) >= 0:
            diff = token.count - tok.count
            return tok, diff, i
        i = i + 1
    return None, 0, 0

def split_tokens(token_stack, token_kind, str, opening, diff, i):
    if diff < 0:
        diff = abs(diff)
        first_tok = token(token_kind, str, opening.lc, diff)
        second_tok = token(token_kind, str, opening.lc + diff, opening.count - diff)
        token_stack = token_stack[:i] + token_stack[i + 1:]

        new_token_stack = []
        new_token_stack.append(first_tok)
        new_token_stack.append(second_tok)
        new_token_stack = token_stack[:i] + new_token_stack + token_stack[i:]
        return new_token_stack
    else:
        first_tok = token(token_kind, str, token_stack[-1].lc, token_stack[-1].count - diff)
        second_tok = token(token_kind, str, token_stack[-1].lc + (token_stack[-1].count - diff), diff)

    token_stack = token_stack[:-1]
    token_stack.append(first_tok)
    token_stack.append(second_tok)
    return token_stack

def update_locations(token_stack, count):
    for tok in token_stack:
        if tok.token_kind == TOKEN_KIND.DELIM and tok.token != '#':
            tok.lc = tok.lc + count
    return token_stack

def parse_new(token_array, output_str, token_stack, back_track = False):
    curr_tok = token_peek(token_array)
    match curr_tok.token_kind:
        case TOKEN_KIND.DELIM:
            match curr_tok.token:
                case '#':
                    if token_next(token_array).token_kind == TOKEN_KIND.SPACE:
                        curr_tok.lc = len(output_str)
                        token_stack.append(curr_tok)
                        return parse_new(token_array[2:], output_str, token_stack, False)
                        
                    output_str = output_str + curr_tok.token
                    return parse_new(token_array[1:], output_str, token_stack, False)
                case '*':
                    curr_tok.lc = len(output_str)
                    token_stack.append(curr_tok)
                    return parse_new(token_array[1:], output_str, token_stack, False)
                case '_':
                    curr_tok.lc = len(output_str)
                    token_stack.append(curr_tok)
                    return parse_new(token_array[1:], output_str, token_stack, False)
                
        case TOKEN_KIND.BACK_SLASH:
            pass
        case TOKEN_KIND.NEW_LINE:
            pass
        case TOKEN_KIND.SPACE:
            output_str = output_str + curr_tok.token
            return parse_new(token_array[1:], output_str, token_stack, False)
        case TOKEN_KIND.CHAR:
            output_str = output_str + curr_tok.token
            return parse_new(token_array[1:], output_str, token_stack, False)
        case TOKEN_KIND.EOF:
            if not token_stack:
                return output_str
            elif token_stack[-1].token == '#':
                if token_stack[-1].count < 7:
                    output_str = f"<h{token_stack[-1].count}>" + output_str[token_stack[-1].lc:] + f"</h{token_stack[-1].count}>"
            elif token_stack[-1].token == '*':
                opening, diff, i = search_through_stack(token_stack[:-1], token_stack[-1])       
                if not opening:
                    output_str = output_str[:token_stack[-1].lc] + '*'*token_stack[-1].count + output_str[token_stack[-1].lc:]
                    return parse_new(token_array, output_str, token_stack[:-1], False)
                if abs(diff) > 0:
                    token_stack = split_tokens(token_stack, TOKEN_KIND.DELIM, '*', opening, diff, i)     
                    return parse_new(token_array, output_str, token_stack, False)    
                if token_stack[-1].count == 1:
                    output_str = output_str[:opening.lc] + "<i>" + output_str[opening.lc:token_stack[-1].lc] + "</i>" + output_str[token_stack[-1].lc:]
                    token_stack = update_locations(token_stack, len("<i>"))
                elif token_stack[-1].count == 2:
                    output_str = output_str[:opening.lc] + "<b>" + output_str[opening.lc:token_stack[-1].lc] + "</b>" + output_str[token_stack[-1].lc:]
                    token_stack = update_locations(token_stack, len("<b>"))
                elif token_stack[-1].count == 3:
                    output_str = output_str[:opening.lc] + "<b><i>" + output_str[opening.lc:token_stack[-1].lc] + "</i></b>" + output_str[token_stack[-1].lc:]
                    token_stack = update_locations(token_stack, len("<b><i>"))
                token_stack.remove(opening)
            elif token_stack[-1].token == '_':
                opening, diff, i = search_through_stack(token_stack[:-1], token_stack[-1])       
                if not opening:
                    output_str = output_str[:token_stack[-1].lc] + '_' * token_stack[-1].count + output_str[token_stack[-1].lc:]
                    return parse_new(token_array, output_str, token_stack[:-1], False)
                if token_stack[-1].count == 1:
                    output_str = output_str[:opening.lc] + "<u>" + output_str[opening.lc:token_stack[-1].lc] + "</u>" + output_str[token_stack[-1].lc:]
                    token_stack = update_locations(token_stack, len("<u>"))
                token_stack.remove(opening)
            return parse_new(token_array, output_str, token_stack[:-1], False)

def print_token(token_array):
    for tok in token_array:
        print("type: ", tok.token_kind, " count: ", tok.count)
        
def parse_markdown(str):
    token_array= toknize(str)
    output_str = parse_new(token_array, "", [], False)
    print(output_str)
    return output_str

assert parse_markdown("# H1") == "<h1>H1</h1>"
assert parse_markdown("## H1") == "<h2>H1</h2>"
assert parse_markdown("### H1") == "<h3>H1</h3>"
assert parse_markdown("#### H1") == "<h4>H1</h4>"
assert parse_markdown("##### H1") == "<h5>H1</h5>"
assert parse_markdown("###### H1") == "<h6>H1</h6>"
assert parse_markdown("####### H1") == "####### H1"
assert parse_markdown("## Hello from python") == "<h2>Hello from python</h2>"
assert parse_markdown("# WHAT #") == "<h1>WHAT #</h1>"
assert parse_markdown("*test") == "*test"
assert parse_markdown("**test") == "**test"
assert parse_markdown("***test") == "***test"
assert parse_markdown("test*") == "test*"
assert parse_markdown("test**") == "test**"
assert parse_markdown("t*****************") == "t*****************"
assert parse_markdown("*****************t") == "*****************t"
assert parse_markdown("*test*") == "<i>test</i>"
assert parse_markdown("**test**") == "<b>test</b>"
assert parse_markdown("***test***") == "<b><i>test</i></b>"
assert parse_markdown("## *Hello from python*") == "<h2><i>Hello from python</i></h2>"
assert parse_markdown("_meow_") == "<u>meow</u>"
assert parse_markdown("**_meow_**") == "<b><u>meow</u></b>"
assert parse_markdown("_meow") == "_meow"
assert parse_markdown("meow_") == "meow_"
assert parse_markdown("**meow_") == "**meow_"
assert parse_markdown("***test**") == "*<b>test</b>"
