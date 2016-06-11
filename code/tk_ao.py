__author__ = 'Fabian Gebhart'

# This file "tk_ao.py" provides a GUI for controlling
# the Adaptive Optics Model. It mainly uses Tkinter
# and is able to run other programs in background.
# The design is chosen to fit to the RPI 7inch
# touchscreen. For more info see:
# https://github.com/fgebhart/adaptive-optics-model


# import the necessary packages
import Tkinter as tk
import os


def delete_log():
    """function checks if log file exists and removes it
    if so. The log file is essential for closing active
    programs in the background. All the camera based programs
    create the log file each startup and then they are
    checking each frame if the log file exists. By pressing
    the "stop"-button the log file will be deleted and so
    the programs stop."""
    if os.path.isfile('/home/pi/close.log') is True:
        os.remove('/home/pi/close.log')
    else:
        pass

# initialize the total variable for the hidden buttons
total = []


class Mainpage:
    # Starting page with all the relevant buttons and info on it
    def __init__(self, master):
        self.master = master
        master.geometry("800x480+0+0")
        # set background image:
        background_image = tk.PhotoImage(file=
                    "/home/pi/background.gif")
        background_label = tk.Label(master,
                    image=background_image)
        background_label.place(x=-1, y=-1)
        background_label.image = background_image

        # set label to fullscreen
        master.attributes('-fullscreen', True)

        # create new window which is used as 'instructions'
        def new_window():
            newwindow = tk.Toplevel()
            app = Instructions(newwindow)

        # manage buttons:
        button1 = tk.Button(text='Anleitung', width=25,
                    height=2, command=lambda: new_window())
        button1.place(relx=0.8, y=180, anchor="c")

        def start_ao():
            """function to run, when 'start'-button is pressed.
            Creates the 'stop'-button and runs the
            'AO_just_stabi.py' file"""
            os.system('sudo python AO_just_stabi.py &')
            button7.place(relx=0.25, y=260, anchor="c")

        # manage images for start and stop button
        start_button_image = tk.PhotoImage(file=
                    "/home/pi/start_button.gif")
        stop_button_image = tk.PhotoImage(file=
                    "/home/pi/stop_button.gif")

        button2 = tk.Button(text='Start Adaptive Optik',
                    width=275, height=275,
                    highlightthickness=0, bd=0,
                    command=lambda: start_ao(),
                    image=start_button_image)
        button2.image = start_button_image
        button2.place(relx=0.25, y=260, anchor="c")

        button3 = tk.Button(text='Reset', width=25, height=2,
                    command=lambda:
                    os.system('sudo python AO_reset.py &'))
        button3.place(relx=0.8, y=260, anchor="c")

        def cam_view():
            """function to run, when 'cam-view'-button is
            pressed. Creates the 'stop'-button and runs
            the 'just_cam.py' file"""
            os.system('sudo python just_cam.py &')
            button7.place(relx=0.25, y=260, anchor="c")

        button4 = tk.Button(text='Kamera Sicht', width=25,
                    height=2, command=lambda: cam_view())
        button4.place(relx=0.8, y=340, anchor="c")

        # manage the hidden buttons + function:
        def hidden_button(count):
            """There a three hidden buttons: 1 in upper
            right corner, 2 in bottom right corner and 3
            in bottom left corner. If you press them in
            the order 1-2-3 the GUI quits. All other
            combinations will lead to no action. To
            shut down the RPI find a 'shutdown' shortcut
            on the desktop"""
            global total
            total.append(count)

            # if length of list total is bigger than 3,
            # empty the list total
            if total[0] == 1 and len(total) == 1:
                pass
            elif total[0] == 1 and total[1] == 2\
                    and len(total) == 2:
                pass
            elif total[0] == 1 and total[1] == 2\
                    and total[2] == 3:
                master.quit()
            elif len(total) == 4:
                total = []
            else:
                total = []

        # manage image for the hidden button, which is the same
        # as the background color of the main background image
        hidden_button_background_image = tk.PhotoImage(file=
                    "/home/pi/hidden_button.gif")

        # 3 hidden buttons (5, 8, 9):
        button5 = tk.Button(text ='', width=78, height=38,
                    highlightthickness=0, bd=0,
                    command=lambda: hidden_button(1),
                    image=hidden_button_background_image)
        button5.image = hidden_button_background_image
        button5.place(relx=1, y=20, anchor="c")

        button8 = tk.Button(text='', width=78, height=38,
                    highlightthickness=0, bd=0,
                    command=lambda: hidden_button(2),
                    image=hidden_button_background_image)
        button8.image = hidden_button_background_image
        button8.place(relx=1, y=460, anchor="c")

        button9 = tk.Button(text='', width=78, height=38,
                    highlightthickness=0, bd=0,
                    command=lambda: hidden_button(3),
                    image=hidden_button_background_image)
        button9.image = hidden_button_background_image
        button9.place(relx=0, y=460, anchor="c")

        def stop_button():
            """function to run, when 'stop'-button is pressed.
            Creates the 'stop'-button and runs the
            'AO_just_stabi.py' file"""
            delete_log()
            button7.place_forget()

        button7 = tk.Button(text='Stop', width=275, height=275,
                     fg="red",  highlightthickness=0, bd=0,
                     command=lambda: stop_button(),
                     image=stop_button_image)
        button7.image = stop_button_image


class Instructions:
    def __init__(self, master):
        self.master = master
        master.geometry("400x400+370-110")
        # set background image:
        background_image = tk.PhotoImage(file=
                    "/home/pi/anleitung.gif")
        background_label = tk.Label(master,
                    image=background_image)
        background_label.place(x=-1, y=-1)
        background_label.image = background_image

        # manage close button:
        self.button1 = tk.Button(self.master, text='Schliessen',
                    width=25, command=lambda: master.destroy())
        self.button1.place(relx=0.5, y=370, anchor="c")


def main():
    root = tk.Tk()
    app = Mainpage(root)
    root.mainloop()

if __name__ == '__main__':
    main()