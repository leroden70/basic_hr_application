def func(arg1, arg2 = "0"):
    print(f"arg1 = {arg1}")
    if arg2:
        print(f"arg2 (after check) = {arg2}")
    print(f"arg2 (no check) = {arg2}")

func("A")