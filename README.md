> [!WARNING]
> This does not support unbalanced delimiters, this ```**test*``` will not become ```*<i>test</i>```, soley because markdown is evil.
> Some things are restrained, for strikethroughs it has to be one ~ on each side, likewise for underscores and codeblocks to three, 
> e.g ~~ \~strike\~ ~~ =>  ```~~ <del>strike</del> ~~```.

# Markdown to html converter
Currently supports:
- Headers
- Bold, italic, nested bolds or italics
- Code blocks
- strikethroughs
- escaping characters
