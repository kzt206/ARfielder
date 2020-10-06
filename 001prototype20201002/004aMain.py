import tkinter as tk
import tkWindow


def main():
    root = tk.Tk()
    app = tkWindow.Application(master=root)#Inherit

    app.mainloop()


if __name__ == "__main__":
    main()