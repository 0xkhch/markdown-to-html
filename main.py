from enum import Enum
class TOKEN_KIND(Enum):
    CHAR = 1
    HASH = 2
    STAR = 3
    UNDERSCORE = 4
    BACK_SLASH = 5
    NEW_LINE = 6
    EOF = 7

class token:
    def __init__(self, token_kind, token):
        self.token_kind = token_kind
        self.token = token

def toknize(str):
    token_array = []
    seen_header = False
    seen_char = False
    for char in str:
        if char == "#":
            seen_header = True
            if seen_char:
                token_array.append(token(TOKEN_KIND.CHAR, char))
            else:
                token_array.append(token(TOKEN_KIND.HASH, char))
        elif char == "*":
            token_array.append(token(TOKEN_KIND.STAR, char))
        elif char == "_":
            token_array.append(token(TOKEN_KIND.UNDERSCORE, char))
        elif char == "\\":
            token_array.append(token(TOKEN_KIND.BACK_SLASH, char))
        elif char == "\n":
            token_array.append(token(TOKEN_KIND.NEW_LINE, char))
        else:
            if seen_header:
                seen_char = True
            token_array.append(token(TOKEN_KIND.CHAR, char))
            
    token_array.append(token(TOKEN_KIND.EOF, "EOF"))
    return token_array
    
def token_peek(token_array):
    return token_array[0]

def token_next(token_array):
    return token_array[1]
    
def search_through_tokens(token_array, token_kind):
    for token in token_array:
        if token.token_kind == token_kind:
            return True
    return False
    
def parse_hdr(token_array, hdr_cnt):
    if token_peek(token_array).token_kind != TOKEN_KIND.HASH:
        return hdr_cnt
    return parse_hdr(token_array[1:], hdr_cnt + 1)

def parse_star(token_array, star_cnt):
    if token_peek(token_array).token_kind != TOKEN_KIND.STAR:
        return star_cnt
    return parse_star(token_array[1:], star_cnt + 1)
    
def parse(token_array, output_str, token_stack, back_track = False):
    if token_peek(token_array).token_kind == TOKEN_KIND.HASH:

        hdr_cnt = parse_hdr(token_array, 0)
        if hdr_cnt > 6:
            output_str = output_str + '#' * hdr_cnt
            return parse(token_array[hdr_cnt:], output_str, token_stack, False)
        else:
            if token_array[hdr_cnt].token != ' ':
                output_str = output_str + '#' * hdr_cnt
                return parse(token_array[hdr_cnt:], output_str, token_stack, False)
        
        output_str = output_str + f"<h{hdr_cnt}>"
        token_stack.append(f"h{hdr_cnt}")
        
        # +1 to remove space
        return parse(token_array[hdr_cnt + 1:], output_str, token_stack, False)
        
    elif token_peek(token_array).token_kind == TOKEN_KIND.STAR:
        if back_track:
            return parse(token_array[1:], output_str, token_stack, True)
            
        star_cnt = parse_star(token_array, 0)
        if star_cnt == 1:
            output_str = output_str + "<i>"
            token_stack.append("i")
        elif star_cnt == 2:
            output_str = output_str + "<b>"
            token_stack.append("b")
        elif star_cnt == 3:
            output_str = output_str + "<b><i>"
            token_stack.append("bi")
            
        return parse(token_array[star_cnt:], output_str, token_stack, False)
        
    elif token_peek(token_array).token_kind == TOKEN_KIND.UNDERSCORE:
        if back_track:
            return parse(token_array[1:], output_str, token_stack, True)
        output_str = output_str + "<u>"
        token_stack.append("u")
        return parse(token_array[1:], output_str, token_stack, False)
        
    elif token_peek(token_array).token_kind == TOKEN_KIND.BACK_SLASH:
        if token_next(token_array).token_kind != TOKEN_KIND.CHAR:
            output_str = output_str + token_array[1].token
            return parse(token_array[2:], output_str, token_stack, False)
        output_str = output_str + token_array[0].token
        return parse(token_array[1:], output_str, token_stack, False)
        
    elif token_peek(token_array).token_kind == TOKEN_KIND.NEW_LINE:
        output_str = output_str + "<br/>"
        return parse(token_array[1:], output_str, token_stack, False)
        
    elif token_peek(token_array).token_kind == TOKEN_KIND.CHAR:
        output_str = output_str + token_array[0].token
        if token_next(token_array).token_kind != TOKEN_KIND.CHAR and(not search_through_tokens(token_array[1:], TOKEN_KIND.CHAR)):
            return parse(token_array[1:], output_str, token_stack, True)
    
        return parse(token_array[1:], output_str, token_stack, False)
        
    elif token_peek(token_array).token_kind == TOKEN_KIND.EOF:
        if not token_stack:
            return output_str
        else:
            if token_stack[-1][0] == "h":
                output_str = output_str + f"</{token_stack[-1]}>"
            elif token_stack[-1] == "i":
                output_str = output_str + "</i>"
            elif token_stack[-1] == "b":
                output_str = output_str + "</b>"
            elif token_stack[-1] == "bi":
                output_str = output_str + "</i></b>"
            elif token_stack[-1] == "u":
                output_str = output_str + "</u>"

            return parse(token_array, output_str, token_stack[:-1], False)

def parse_markdown(str):
    token_array = toknize(str)
    output_str = parse(token_array, "", [], False)
    return output_str


assert parse_markdown("# H1") == "<h1>H1</h1>"
assert parse_markdown("## H1") == "<h2>H1</h2>"
assert parse_markdown("### H1") == "<h3>H1</h3>"
assert parse_markdown("#### H1") == "<h4>H1</h4>"
assert parse_markdown("##### H1") == "<h5>H1</h5>"
assert parse_markdown("###### H1") == "<h6>H1</h6>"
assert parse_markdown("####### H1") == "####### H1"
assert parse_markdown("## Hello from python") == "<h2>Hello from python</h2>"
assert parse_markdown("*test*") == "<i>test</i>"
assert parse_markdown("**test**") == "<b>test</b>"
assert parse_markdown("***test***") == "<b><i>test</i></b>"
assert parse_markdown("## *Hello from python*") == "<h2><i>Hello from python</i></h2>"
assert parse_markdown("## *Hello from **python***") == "<h2><i>Hello from <b>python</b></i></h2>"
assert parse_markdown("_meow_") == "<u>meow</u>"
assert parse_markdown("**_meow_**") == "<b><u>meow</u></b>"
assert parse_markdown("# WHAT #") == "<h1>WHAT #</h1>"
