import traceback

real_print = print


def print(text):
    if not isinstance(text, str):
        text = str(text)

    real_print("#INTERPRETER#" + text + "#ENDPARSE#", end="", flush=True)


def parseCall(*arg):
    result = ""
    try:
        if len(arg) > 1:
            eval_result = eval(arg[0] + '("' + '","'.join(arg[1:]) + '")')
        else:
            eval_result = eval(arg[0] + "()")

        if isinstance(eval_result, numbers.Number) and not isinstance(
            eval_result, bool
        ):
            result = str(eval_result)
        else:
            result = '"' + str(eval_result) + '"'

    except (RuntimeError, TypeError, NameError):
        result = '"' + "Unexpected error:" + str(sys.exc_info()) + '"'

    real_print("#PYTHONFUNCTION#" + result + "#ENDPARSE#", flush=True, end="")


def getAndExecuteInputOnce():
    command_buffer = ""

    while True:
        code_input = input("")

        # when empty line is found, execute code
        if code_input == "":
            try:
                exec(command_buffer, globals(), globals())
            except:
                traceback.print_exc()
            return
        else:
            command_buffer += code_input + "\n"


def getAndExecuteInput():
    command_buffer = ""

    while True:
        code_input = input("")
        # when empty line is found, execute code
        if code_input == "":
            try:
                exec(command_buffer, globals(), globals())

                # onlyprint COMANDCOMPLETE when the input doesn't start with parseCall,
                # since it's a special internal Python call
                # which requires a single print between exec and return
                if not command_buffer.startswith("parseCall"):
                    real_print("#COMMANDCOMPLETE##ENDPARSE#", end="", flush=True)
            except:
                traceback.print_exc()
            command_buffer = ""
        else:
            command_buffer += code_input + "\n"
