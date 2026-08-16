from tkinter import Tk, ttk
from add_song import create_add_frame

root = Tk()
root.title("Disco Manager")
tab_control = ttk.Notebook(root)

add_tab = ttk.Frame(tab_control)
create_add_frame(add_tab)

tab_control.add(add_tab, text='Add Song')




remove_tab = ttk.Frame(tab_control)
tab_control.add(remove_tab, text='Remove Song')

tab_control.pack(expand=1, fill='both')

root.mainloop()
