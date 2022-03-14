#!/usr/bin/env python3

import platform
import socket
import subprocess
import sys

targets = {
    4505: "salt.prod.hivecell.io",
    4506: "salt.prod.hivecell.io",
    8443: "device.identity.prod.hivecell.io",
    2222: "5310ca99f9c54e508814a3e3b849307d.rssh.prod.hivecell.io"
}

check_list = {
    1: "1. Check default gateway is available",
    2: "2. Check Hive Control DNS names",
    3: "3. Check ports are open"
}


def _get_human_readable_os_type():
    if platform.system() == "Darwin":
        return "MacOs"
    else:
        return platform.system()


def _ping(host):
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


def _hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False


def _check_port_is_open(host, port):
    try:
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        location = (host, port)
        result_of_check = a_socket.connect_ex(location) == 0
        return result_of_check
    except socket.error:
        return False


def _get_default_gateway():
    if platform.system() == "Darwin":
        command = "route -n  get  default | grep gateway | head -n 1 | awk '{print $2}'"
    elif platform.system() == "Linux":
        command = "ip r | grep default | head -n 1 | awk '{print $3}'"

    route_default_result = subprocess.check_output(command, shell=True)
    route_default_result.decode('utf-8')

    if route_default_result:
        return route_default_result
    else:
        return None


def _run_with_ui():
    try:
        import tkinter
    except ImportError:  # python 2
        import Tkinter as tkinter

    mainWindow = tkinter.Tk()
    cross_mark = "\u274c"
    check_mark = "\u2714"

    mainWindow.title("Hivecell Network Diagnostic Tool")
    mainWindow.geometry('800x480-8-200')
    mainWindow.configure(bg='light gray')
    mainWindow.columnconfigure(0, weight=1000)
    mainWindow.rowconfigure(2, weight=1)

    label = tkinter.Label(mainWindow, text="OS: " + _get_human_readable_os_type(), bg='light gray', fg='black')
    label.grid(row=0, column=0, columnspan=2, pady=10)
    # log area
    scrollbar = tkinter.Scrollbar(mainWindow)
    scrollbar.grid(row=1, column=2, sticky='nsew')
    log_area = tkinter.Text(mainWindow, yscrollcommand=scrollbar.set, width=70, bg='light gray', fg='black')
    scrollbar.config(command=log_area.yview)
    log_area.grid(row=1, column=1, sticky="nsew")
    log_area['state'] = 'disabled'

    left_side = tkinter.Frame(mainWindow, bg='light gray')
    left_side.grid(row=1, column=0, sticky="nw", padx=20)

    check_label_1 = tkinter.Label(left_side, text=check_list[1], bg='light gray', fg='black')
    check_label_1.grid(row=0, column=0, sticky='w')
    check_label_2 = tkinter.Label(left_side, text=check_list[2], bg='light gray', fg='black')
    check_label_2.grid(row=1, column=0, sticky='w')
    check_label_3 = tkinter.Label(left_side, text=check_list[3], bg='light gray', fg='black')
    check_label_3.grid(row=2, column=0, sticky='w')

    def _add_label_mark(lbl, mark):
        lbl["text"] = lbl["text"] + " " + mark
        lbl.update()

    def _set_label_text(lbl, text):
        lbl["text"] = text
        lbl.update()

    def _insert_text_into_text_area(area, text):
        area.insert("end", "{}\n".format(text))
        area.update()

    def _check_network():
        log_area['state'] = 'normal'
        log_area.delete("1.0", tkinter.END)
        _set_label_text(check_label_1, check_list[1])
        _set_label_text(check_label_2, check_list[2])
        _set_label_text(check_label_3, check_list[3])
        okButton["state"] = "disabled"

        # first check
        def_gateway = _get_default_gateway()

        if def_gateway:
            if _ping(def_gateway):
                _add_label_mark(check_label_1, check_mark)
                _insert_text_into_text_area(log_area, "Default gateway is resolved!")
            else:
                _add_label_mark(check_label_1, cross_mark)
                _insert_text_into_text_area(log_area, "Default gateway can`t be resolved!!")
        else:
            _insert_text_into_text_area(log_area, "Default gateway can`t be resolved!!")

        _insert_text_into_text_area(log_area, "\n" + (10 * "*") + "\n")
        # second check
        successful_count_check_2 = 0
        for host in set(targets.values()):
            if _hostname_resolves(host):
                _insert_text_into_text_area(log_area, "Host {} resolved!".format(host))
                successful_count_check_2 += 1
            else:
                _insert_text_into_text_area(log_area, "Host {} can`t be resolved!".format(host))

        if successful_count_check_2 == len(set(targets.values())):
            _add_label_mark(check_label_2, check_mark)
        else:
            _add_label_mark(check_label_2, cross_mark)
        _insert_text_into_text_area(log_area, "\n" + (10 * "*") + "\n")
        # third check
        successful_count_check_3 = 0
        for port, h_name in targets.items():
            if _check_port_is_open(h_name, port):
                _insert_text_into_text_area(log_area, "Port {} is OPEN!".format(port))
                successful_count_check_3 += 1
            else:
                _insert_text_into_text_area(log_area, "Port {} is CLOSED!".format(port))

        if successful_count_check_3 == len(targets):
            _add_label_mark(check_label_3, check_mark)
        else:
            _add_label_mark(check_label_3, cross_mark)
        _insert_text_into_text_area(log_area, "\n" + (10 * "*") + "\n")

        okButton["state"] = "normal"
        log_area['state'] = 'disabled'

    # Buttons
    bframe = tkinter.Frame(mainWindow, bg="light gray")
    bframe.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="se")

    okButton = tkinter.Button(bframe, text="Start", command=_check_network, borderwidth=0,
                              highlightbackground="light gray",
                              highlightthickness=0, fg="black")
    okButton.grid(row=0, column=0, sticky='e', padx=2)
    tkinter.Button(bframe, text="Cancel", command=mainWindow.destroy, highlightbackground="light gray",
                   highlightthickness=0, borderwidth=0, fg="black").grid(row=0, column=1, sticky='w', padx=2)

    mainWindow.mainloop()


def _run_conlose():
    report = 50 * "="
    # first check
    def_gateway = _get_default_gateway()
    if def_gateway:
        if _ping(def_gateway):
            report += "\nDefault gateway is resolved!"
        else:
            report += "\nDefault gateway can`t be resolved!!"
    else:
        report += "\nDefault gateway can`t be resolved!!"

    # second check
    report += "\n" + 50 * "*"
    for host in set(targets.values()):
        if _hostname_resolves(host):
            report += "\nHost {} resolved!".format(host)
        else:
            report += "\nHost {} can`t be resolved!".format(host)

    # third check
    report += "\n" + 50 * "*"
    for port, h_name in targets.items():
        if _check_port_is_open(h_name, port):
            report += "\nPort {} is OPEN!".format(port)
        else:
            report += "\nPort {} is CLOSED!".format(port)

    report += "\n" + 50 * "*"
    print(report)


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        _run_conlose()
    else:
        _run_with_ui()

