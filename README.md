# opsdroid skill shell

A skill for [opsdroid](https://github.com/opsdroid/opsdroid) to respond to Please run messages.

## Requirements

None.

## Configuration

You can configure:

* scriptdir - where the skill will search for shell scripts
* initialtalkbacktimeout - the timeout for sending the first stdout lines from the script back to the chat
* talkbacktimeout - the maximum time the skill will wait until the gathered stdout lines are sent back to the chat
* argumentumseparator - if the script is able to accept argumentums this will be the separator between the args

## Usage

Place a shell scipt like this:


```
#!/bin/bash
ls . | grep -v "*.lib"
```

in the *scriptdir* and then you can tell [opsdroid](https://github.com/opsdroid/opsdroid): **Please run ls**

[opsdroid](https://github.com/opsdroid/opsdroid) will run the script *ls* in the *scriptdir* and answer with
the output of the script.

The output will be like:

> Starting the script named ls on 2018-06-17 11:42:54.705303...
> Please be patient...
```
ls
```
> The command ls ended with the return code of 0 on 2018-06-17 11:42:54.905555 and was running 0:00:00.205305 seconds long.
