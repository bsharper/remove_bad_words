import sys

def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class LineUpdate:
    def __init__(self, total, title='', **things):
        self.title = title
        self.is_first_update = True

    def __call__(self, text):
        if not self.is_first_update:
            # Move the cursor up one line and clear the line
            sys.stdout.write('\x1b[1A\x1b[2K')
        else:
            self.is_first_update = False

        # Print the updated line
        if isFloat(text) and float(text) <=1.0:
            text = f"{int(float(text)*100)}% complete"
        sys.stdout.write(f'{self.title} {text}\n')
        sys.stdout.flush()

    def complete(self):
        # Clear the last line
        sys.stdout.write('\x1b[1A\x1b[2K')
        sys.stdout.flush()
    def text(self, t):
        self.fake_text = t

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.complete()

if __name__ == "__main__":
    import time
    with LineUpdate("Process running:") as updater:
        for i in range(101):
            #updater(f"{i}% complete")
            updater(i/100)
            # Simulate some processing
            time.sleep(0.1)
