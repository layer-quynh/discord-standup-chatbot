import pyperclip
s1 = "Hello world"
pyperclip.copy(s1)
s2 = pyperclip.paste()
print(s2)