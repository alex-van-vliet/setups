# Setup

Easily setup projects, and much more.

## Configuration

First create a `.setups` directory in your home directory.

Then any directory inside `~/.setups` will be considered a setup, with the setup name being the name of the directory.

To configure a setup, create a `.config.setup` inside a setup directory.

The following commands are available:

- `echo [arguments...]`: print its arguments
- `file <filename>`: copy filename to the directory from where the script is run
- `command <command> [arguments...]`: run the command from where the script is run

The arguments are separated by spaces, and can be quoted.
For example (`_` is a space), `_command__"my_arg__1"__my_arg_2` is evaluated as `["command", "my_arg__1", "my", "arg", "2"]`.

Specials characters can be escaped with a backslash.

Colors can be added using:

- `${COLOR:n}` for numbered terminal colors (0 to 255),
- `${COLOR:r:g:b}` for rgb colors,
- `${RESET}` to reset the color.

### Example

With the following configuration, the `example` setup will:

- print a message,
- copy `myfile.txt` to the current directory,
- print a message,
- list the current directory,
- print a message,
- get the content from `myfile.txt` from the current directory,
- print a message.

```
$ ls ~/.setups
example
$ ls -a ~/.setups/example
.  ..  .config.setup  myfile.txt
$ ~/.setups/example/.config.setup
echo    ${COLOR:4}Copying myfile.txt${RESET}
file    myfile.txt
echo    ${COLOR:4}Checking list of files${RESET}
command ls
echo    ${COLOR:4}Checking content${RESET}
command cat myfile.txt
echo    ${COLOR:2}All good!${RESET}
```
