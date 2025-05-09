from src.runtime import run_ix

if __name__ == "__main__":
    with open("examples/hello_bot.ix") as f:
        code = f.read()
    run_ix(code)
