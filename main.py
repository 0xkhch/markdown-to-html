from enum import Enum
class TOKEN(Enum):
    CHAR = 1
    HASH = 2
    STAR = 3
    UNDERSCORE = 4
    BACK_SLASH = 5
    NEW_LINE = 6
    EOF = 7
    
def toknize(str):
    token_array = []
    for char in str:
        if char == "#":
            token_array.append(TOKEN.HASH)
        elif char == "*":
            token_array.append(TOKEN.STAR)
        elif char == "_":
            token_array.append(TOKEN.UNDERSCORE)
        elif char == "\\":
            token_array.append(TOKEN.BACK_SLASH)
        elif char == "\n":
            token_array.append(TOKEN.NEW_LINE)
        else:
            token_array.append(TOKEN.CHAR)
    token_array.append(TOKEN.EOF)
    return token_array
    
def token_peek(token_array):
    return token_array[0]

def token_next(token_array):
    return token_array[1]
    
def parse_hdr(token_array, hdr_cnt):
    if token_peek(token_array) != TOKEN.HASH:
        return hdr_cnt
    return parse_hdr(token_array[1:], hdr_cnt + 1)

def parse_star(token_array, star_cnt):
    if token_peek(token_array) != TOKEN.STAR:
        return star_cnt
    return parse_star(token_array[1:], star_cnt + 1)
    
def parse(token_array, input_str, output_str, token_stack, back_track = False):
    if token_peek(token_array) == TOKEN.HASH:
        hdr_cnt = parse_hdr(token_array, 0)
        if hdr_cnt > 6:
            output_str = output_str + '#' * hdr_cnt
            return parse(token_array[hdr_cnt:], input_str[hdr_cnt:], output_str, token_stack, False)
        else:
            if input_str[hdr_cnt] != ' ':
                output_str = output_str + '#' * hdr_cnt
                return parse(token_array[hdr_cnt:], input_str[hdr_cnt:], output_str, token_stack, False)
        
        output_str = output_str + f"<h{hdr_cnt}>"
        token_stack.append(f"h{hdr_cnt}")
        
        # +1 to remove space
        return parse(token_array[hdr_cnt + 1:], input_str[hdr_cnt + 1:], output_str, token_stack, False)
        
    elif token_peek(token_array) == TOKEN.STAR:
        if back_track:
            return parse(token_array[1:], input_str[1:], output_str, token_stack, True)
            
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
            
        return parse(token_array[star_cnt:], input_str[star_cnt:], output_str, token_stack, False)
        
    elif token_peek(token_array) == TOKEN.UNDERSCORE:
        if back_track:
            return parse(token_array[1:], input_str[1:], output_str, token_stack, True)
        output_str = output_str + "<u>"
        token_stack.append("u")
        return parse(token_array[1:], input_str[1:], output_str, token_stack, False)
        
    elif token_peek(token_array) == TOKEN.BACK_SLASH:
        if token_next(token_array) != TOKEN.CHAR:
            output_str = output_str + input_str[1]
            return parse(token_array[2:], input_str[2:], output_str, token_stack, False)
        output_str = output_str + input_str[0]
        return parse(token_array[1:], input_str[1:], output_str, token_stack, False)
        
    elif token_peek(token_array) == TOKEN.NEW_LINE:
        output_str = output_str + "<br/>"
        return parse(token_array[1:], input_str[1:], output_str, token_stack, False)
        
    elif token_peek(token_array) == TOKEN.CHAR:
        output_str = output_str + input_str[0]
        if token_next(token_array) != TOKEN.CHAR and (TOKEN.CHAR not in token_array[1:]):
            return parse(token_array[1:], input_str[1:], output_str, token_stack, True)
    
        return parse(token_array[1:], input_str[1:], output_str, token_stack, False)
        
    elif token_peek(token_array) == TOKEN.EOF:
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

            return parse(token_array, input_str, output_str, token_stack[:-1], False)

def parse_markdown(str):
    token_array = toknize(str)
    output_str = parse(token_array, str, "", [])
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
