_color_codes = {
    "SUCCESS": "\033[92m",
    "EXISTS": "\033[93m",
    "FAIL": "\033[91m",
    "ERROR": "\033[95m"
}

_reset_code = "\033[0m"


def log_with_color(code, status, message):
    color_code = _color_codes.get(code, _reset_code)
    print(f"{color_code}[{status}]{_reset_code} {message}")
