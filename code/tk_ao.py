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
import time


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

delete_log()

# initialize the total variable for the hidden buttons
total = []


class Mainpage:
    # Starting page with all the relevant buttons and info on it
    def __init__(self, master):
        self.master = master
        master.geometry("800x480+0+0")
        # set background image:
        background_image = tk.PhotoImage(file=
                    "/home/pi/background2.gif")
        background_label = tk.Label(master,
                    image=background_image)
        background_label.place(x=-1, y=-1)
        background_label.image = background_image
        background_label.image = background_image


        # manage image for the hidden button, which is the same
        # as the background color of the main background image
        hidden_button_background_image = tk.PhotoImage(file=
                    "/home/pi/hidden_button_big.gif")

        # set images for status label
        status_image_on = tk.PhotoImage(file=
                    "/home/pi/aktiv.gif")
        status_image_off = tk.PhotoImage(file=
                    "/home/pi/deaktiviert.gif")
        status_image_camview = tk.PhotoImage(file=
                    "/home/pi/Sicht_der_Kamera_aktiv.gif")
        status_image_reset = tk.PhotoImage(file=
                    "/home/pi/status_reset.gif")


        # set label to fullscreen
        master.attributes('-fullscreen', True)

        # create new window which is used as 'instructions'
        def new_window():
            newwindow = tk.Toplevel()
            app = Instructions(newwindow)

        def start_ao():
            """function to run, when 'start'-button is pressed.
            Creates the 'stop'-button and runs the
            'AO_just_stabi.py' file"""
            if os.path.isfile('/home/pi/close.log') is False:
                os.system('sudo python AO_just_stabi.py &')
                time.sleep(1)
                button7.place(x=61, y=390, anchor="sw")
                status_label_off.place_forget()
                status_label_on.place(x=74, y=180)


        def reset():
            if os.path.isfile('/home/pi/close.log') is False:
                button7.place(x=61, y=390, anchor="sw")
                status_label_off.place_forget()
                status_label_reset.place(x=74, y=180)
                os.system('sudo python AO_reset.py &')
                # time.sleep(2)

                while os.path.isfile('/home/pi/close.log') is True:
                    time.sleep(1)
                else:
                    status_label_reset.place_forget()
                    status_label_off.place(x=74, y=180)
                    button7.place_forget()


        def cam_view():
            """function to run, when 'cam-view'-button is
            pressed. Creates the 'stop'-button and runs
            the 'just_cam.py' file"""
            if os.path.isfile('/home/pi/close.log') is False:
                os.system('sudo python just_cam.py &')
                time.sleep(1)
                button7.place(x=61, y=390, anchor="sw")
                status_label_camview.place(x=74, y=180)
                status_label_off.place_forget()


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

        def stop_button():
            """function to run, when 'stop'-button is pressed.
            Creates the 'stop'-button and runs the
            'AO_just_stabi.py' file"""
            delete_log()
            button7.place_forget()
            status_label_on.place_forget()
            status_label_camview.place_forget()
            status_label_reset.place_forget()
            status_label_off.place(x=74, y=180)


        # manage buttons:
        button1 = tk.Button(text='Anleitung', width=25,
                    height=2, command=lambda: new_window())
        button1.place(relx=0.8, y=160, anchor="c")


        button2 = tk.Button(text='Start Adaptive Optik',
                    width=39, height=4,
                    command=lambda: start_ao())
        button2.place(x=61, y=390, anchor="sw")


        button3 = tk.Button(text='Reset', width=25, height=2,
                    command=lambda: reset())
        button3.place(relx=0.8, y=240, anchor="c")


        button4 = tk.Button(text='Sicht der Kamera', width=25,
                    height=2, command=lambda: cam_view())
        button4.place(relx=0.8, y=320, anchor="c")


        # 3 hidden buttons (5, 8, 9):
        button5 = tk.Button(text ='', width=158, height=78,
                    highlightthickness=0, bd=0,
                    command=lambda: hidden_button(1),
                    image=hidden_button_background_image)
        button5.image = hidden_button_background_image
        button5.place(relx=1, y=20, anchor="c")

        button8 = tk.Button(text='', width=158, height=78,
                    highlightthickness=0, bd=0,
                    command=lambda: hidden_button(2),
                    image=hidden_button_background_image)
        button8.image = hidden_button_background_image
        button8.place(relx=1, y=460, anchor="c")

        button9 = tk.Button(text='', width=158, height=78,
                    highlightthickness=0, bd=0,
                    command=lambda: hidden_button(3),
                    image=hidden_button_background_image)
        button9.image = hidden_button_background_image
        button9.place(relx=0, y=460, anchor="c")


        # Stop Button:
        button7 = tk.Button(text='Stop', width=39, height=4,
                     fg="red", command=lambda: stop_button())



        # status label = ON:
        status_label_on = tk.Label(master, image=status_image_on)
        status_label_on.image = status_image_on
        # status label = OFF:
        status_label_off = tk.Label(master, image=status_image_off)
        status_label_off.image = status_image_off
        # status label cam_view = ON:
        status_label_camview = tk.Label(master, image=status_image_camview)
        status_label_camview.image = status_image_camview
        # status label reset = ON:
        status_label_reset = tk.Label(master, image=status_image_reset)
        status_label_reset.image = status_image_reset


        # flexible close button, uncomment if needed:
        closebutton = tk.Button(text='Close', width=25, height=2,
                    command=lambda: master.quit())
        # closebutton.place(relx=0.6, rely=0.9, anchor="c")


class Instructions:
    def __init__(self, master):
        self.master = master
        master.geometry("400x400+405-110")
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