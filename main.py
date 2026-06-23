from enum import Enum
class TOKEN_KIND(Enum):
    START = 0
    CHAR = 1
    HASH = 2
    STAR = 3
    UNDERSCORE = 4
    BACK_SLASH = 5
    NEW_PARA = 6
    SPACE = 7
    DELIM = 8
    O_DELIM = 9
    C_DELIM = 10
    TILDE = 11
    TICK = 12
    GT = 13
    EOF = 14

class token:
    def __init__(self, kind, char = "", count = 0):
        self.kind = kind
        self.char = char 
        self.count = count

def toknize(str):
    token_array = []
    token_array.append(token(TOKEN_KIND.START))
    if str == '':
        token_array.append(token(TOKEN_KIND.NEW_PARA))
    for c in str:
        if c.isalnum():
            token_array.append(token(TOKEN_KIND.CHAR, c))
        elif c == ' ':
            token_array.append(token(TOKEN_KIND.SPACE, c))
        elif c == '*':
            token_array.append(token(TOKEN_KIND.STAR, c))
        elif c == '#':
            token_array.append(token(TOKEN_KIND.HASH, c))
        elif c == '_':
            token_array.append(token(TOKEN_KIND.UNDERSCORE, c))
        elif c == '~':
            token_array.append(token(TOKEN_KIND.TILDE, c))
        elif c == '`':
            token_array.append(token(TOKEN_KIND.TICK, c))
        elif c == '>':
            token_array.append(token(TOKEN_KIND.GT, c))
        elif c == '\\':
            token_array.append(token(TOKEN_KIND.BACK_SLASH, c))
    token_array.append(token(TOKEN_KIND.EOF))
    return token_array
    
def token_peek(token_array):
    return token_array[0]

def token_peek_and_consume(token_array):
    return token_array[0], token_array[1:]

def token_next(token_array):
    return token_array[1]

def print_token(token_array):
    for tok in token_array:
        print("type: ", tok.kind, " character: ", tok.char)

def insert(src, insert, pos):
    return src[:pos] + insert + src[pos:]

def parse_escape(token_array, output_str):
    next_tok = token_next(token_array)
    if next_tok:
        output_str += next_tok.char
        token_array = token_array[1:]
    return token_array, output_str

# ts so bad and stupid
def patch_delims(token_array, delim, delim_count):
    new_token_array = []
    while token_array:
        currt = token_peek(token_array)
        if currt.kind == TOKEN_KIND.BACK_SLASH:
            next_tok = token_next(token_array)
            if next_tok:
                currt = token(TOKEN_KIND.CHAR, next_tok.char)
                token_array = token_array[1:]
        elif currt.kind == delim.kind:
            cnt = 1
            while True:
                currt = token_next(token_array)
                if currt.kind != delim.kind:
                    break
                cnt += 1
                token_array = token_array[1:]
            if cnt in delim_count:
                currt = token(TOKEN_KIND.DELIM, delim.char, cnt)
            else:
                currt = token(TOKEN_KIND.CHAR, delim.char * cnt, cnt)
        new_token_array.append(currt)
        token_array = token_array[1:]
    stack = []
    for i, tok in enumerate(new_token_array):
        if tok.kind == TOKEN_KIND.DELIM and tok.char == delim.char:
            matched = -1
            for j, (idx, s_tok) in enumerate(reversed(stack)):
                if s_tok.count == tok.count:
                    matched = len(stack) - 1 - j # matching delim in stack
                    break
            if matched != -1:
                index, o_token = stack.pop(matched)
                new_token_array[index] = token(TOKEN_KIND.O_DELIM, delim.char, tok.count)
                new_token_array[i] = token(TOKEN_KIND.C_DELIM, delim.char, tok.count)
            else:
                stack.append((i, tok))

    for i, tok in enumerate(new_token_array):
        if tok.kind == TOKEN_KIND.DELIM and tok.char == delim.char:
            new_token_array[i] = token(TOKEN_KIND.CHAR, delim.char * tok.count, tok.count)
    return new_token_array

def parse_open_delim(token_array, output_str):
    currt = token_peek(token_array)
    if currt.char == '*':
        if currt.count == 1:
            output_str += "<i>"
        elif currt.count == 2:
            output_str += "<b>"
        elif currt.count == 3:
            output_str += "<b><i>"
    elif currt.char == '_':
        output_str += "<u>"
    elif currt.char == '~':
        output_str += "<del>"
    elif currt.char == '`':
        output_str += "<code>"
    return token_array, output_str


def parse_close_delim(token_array, output_str):
    currt = token_peek(token_array)
    if currt.char == '*':
        if currt.count == 1:
            output_str = output_str + "</i>"
        elif currt.count == 2:
            output_str = output_str + "</b>"
        elif currt.count == 3:
            output_str = output_str + "</i></b>"
    elif currt.char == '_':
        output_str += "</u>"
    elif currt.char == '~':
        output_str += "</del>"
    elif currt.char == '`':
        output_str += "</code>"
    return token_array, output_str

def parse_new_para(token_array, output_str):
    output_str += "<br/>"
    return token_array, output_str

def parse_hdr(token_array, output_str, stack, in_hdr):
    hdr_cnt = 1
    while True:
        top_tok = token_peek(token_array)
        if token_next(token_array).kind != TOKEN_KIND.HASH:
            break
        hdr_cnt += 1
        token_array = token_array[1:]
    next_tok = token_next(token_array)
    if not in_hdr and next_tok.kind == TOKEN_KIND.SPACE and hdr_cnt <= 6:
        token_array = token_array[1:] # consume space
        output_str += f"<h{hdr_cnt}>"
        stack.append(f"<h{hdr_cnt}>")
        in_hdr = True
    else:
        output_str += top_tok.char * hdr_cnt

    return token_array, output_str, stack, in_hdr

def parse_block(token_array, output_str, stack, in_block):
    next_tok = token_next(token_array)
    if not in_block and next_tok.kind == TOKEN_KIND.SPACE:
        token_array = token_array[1:] # consume space
        output_str += "<blockquote>"
        stack.append("<blockquote>")
        in_block= True
    else:
        output_str += ">" 

    return token_array, output_str, stack, in_block 

def close_stack_tags(stack, output_str):
    while stack:
        to_append = stack[-1]
        output_str += insert(to_append, "/", 1)
        stack = stack[:-1]
    return output_str, stack

def parse_expression(token_array):
    output_str = ""
    in_hdr = False
    in_block = False
    stack = []
    openers = []
    prev_tok, token_array = token_peek_and_consume(token_array)
    while token_array:
        top_tok = token_peek(token_array)
        if top_tok.kind == TOKEN_KIND.HASH:
            token_array, output_str, stack, in_hdr = parse_hdr(token_array, output_str, stack, in_hdr)
        if top_tok.kind == TOKEN_KIND.GT:
            token_array, output_str, stack, in_block = parse_block(token_array, output_str, stack, in_block)
        elif top_tok.kind == TOKEN_KIND.STAR:
            token_array, output_str = parse_star(token_array, output_str, stack)
        elif top_tok.kind == TOKEN_KIND.CHAR or top_tok.kind == TOKEN_KIND.SPACE:
            output_str += top_tok.char
        elif top_tok.kind == TOKEN_KIND.BACK_SLASH:
            token_array, output_str = parse_escape(token_array, output_str)
        elif top_tok.kind == TOKEN_KIND.O_DELIM:
            token_array, output_str = parse_open_delim(token_array, output_str)
        elif top_tok.kind == TOKEN_KIND.C_DELIM:
            token_array, output_str = parse_close_delim(token_array, output_str)
        elif top_tok.kind == TOKEN_KIND.NEW_PARA:
            output_str, stack = close_stack_tags(stack, output_str)
            in_hdr = False
            in_block = False
            token_array, output_str = parse_new_para(token_array, output_str)
        elif top_tok.kind == TOKEN_KIND.EOF:
            output_str, stack = close_stack_tags(stack, output_str)
        prev_tok = top_tok
        token_array = token_array[1:]
    return output_str
        
def parse_markdown(str):
    line_array = str.split("\n")
    output_str = ""
    for line in line_array:
        token_array = toknize(line)
        token_array = patch_delims(token_array, token(TOKEN_KIND.STAR, "*"), [1, 2, 3])
        token_array = patch_delims(token_array, token(TOKEN_KIND.UNDERSCORE, "_"), [1])
        token_array = patch_delims(token_array, token(TOKEN_KIND.TILDE, "~"), [1])
        token_array = patch_delims(token_array, token(TOKEN_KIND.TICK, "`"), [3])
        # print_token(token_array)
        output_str += parse_expression(token_array)
    # print(output_str)
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
assert parse_markdown("# this is inside of a header\nthis is not hello 123\n\nnew paragraph") == "<h1>this is inside of a header</h1>this is not hello 123<br/>new paragraph"
assert parse_markdown("###### H1 #### H1") == "<h6>H1 #### H1</h6>"
assert parse_markdown("###### H1#### H1") == "<h6>H1#### H1</h6>"
assert parse_markdown("*test") == "*test"
assert parse_markdown("* test") == "* test"
assert parse_markdown("test*") == "test*"
assert parse_markdown("test *") == "test *"
assert parse_markdown("*test text") == "*test text"
assert parse_markdown("test* text") == "test* text"
assert parse_markdown("test * text") == "test * text"
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
assert parse_markdown("~strike") == "~strike"
assert parse_markdown("~~~strike") == "~~~strike"
assert parse_markdown("~~ ~strike~ ~~") == "~~ <del>strike</del> ~~"
assert parse_markdown("```strike```") == "<code>strike</code>"
assert parse_markdown("`strike`") == "`strike`"
assert parse_markdown(">strike`") == ">strike`"
assert parse_markdown(">strike>") == ">strike>"
assert parse_markdown("> strike>") == "<blockquote>strike></blockquote>"
assert parse_markdown("\\~strike\\~") == "~strike~"
