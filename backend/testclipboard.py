import pyperclip
import pyautogui

s1 = "Test clipboard 1"
pyperclip.copy(s1)
s2 = pyperclip.paste()
pyautogui.hotkey('ctrl', 'v')
#print(s2)