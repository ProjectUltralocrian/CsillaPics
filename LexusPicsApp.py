"""
This is the executable GUI program for downloading images from the Lexus config website
(https://prev.images.lexus-europe.com/Query.html).
"""

import tkinter as tk
from tkinter import messagebox, ttk, Label
import csillapics as cp
import validators

"""
The create_gui function sets up the GUI of the program, including the main window and the widgets.
"""

NUM_OF_URLS = 6
NUM_OF_EXTERIOR_SELECTORS = 6


def create_gui():

    # MAIN WINDOW
    window = tk.Tk()
    window.geometry("1250x460")
    window.resizable(False, False)


    # LABELS: (Text: Enter URL and File names)
    url_entries = {}
    for x in range(NUM_OF_URLS):
        tk.Label(window, text=f"URL{x + 1}: ", font=("Arial Bold", 12)).grid(row=x, column=0, sticky=tk.W, padx=20,
                                                                             pady=7)
        url_entry = tk.Entry(window, font=("Arial Italic", 8))
        filename_entry = tk.Entry(window)
        url_entries[url_entry] = filename_entry
        url_entry.grid(row=x, column=1, columnspan=1, sticky=tk.E, ipadx=70, padx=20, pady=7)
        filename_label = tk.Label(window, text="File names...: ", font=("Arial Bold", 12))
        filename_label.grid(row=x, column=2, sticky=tk.W, padx=20, pady=7)
        filename_entry.grid(row=x, column=3, columnspan=1, ipadx=70, padx=20, pady=7)

    def get_all_files():
        download_options_list = {}
        i = 0
        for k, v in url_entries.items():
            i += 1
            if k.get() == "" or v.get() == "":
                continue
            download_options_list[i] = (cp.DownloadOptions(k.get(),  # Builds a Downloadoptions object and passes it to the get_files function for validation and processing.
                                                           v.get(),
                                                           [e_sel.get() for e_sel in all_exterior_selects],
                                                           interior_selected.get(),
                                                           custom_sel_checked.get()))
        print(download_options_list.items())
        for i, download_options in download_options_list.items():
            get_files(download_options, i)

    def clear_all():

        for k, v in url_entries.items():
            v.delete(0, 'end')
            k.delete(0, 'end')

        for e_sel in all_exterior_selects:
            e_sel.configure(state="disabled")
            e_sel.set('')

        window.custom_sel_checked = False
        custom_sel_check_btn.deselect()

    # BUTTON FOR DOWNLOADING IMAGES
    submit_btn = tk.Button(window,
                           text="Download images",
                           command=get_all_files)
    submit_btn.grid(row=8, column=5, rowspan=2, ipadx=100, padx=20, pady=5)

    clearall_btn = tk.Button(window,
                             text="Clear all fields",
                             command=clear_all)
    clearall_btn.grid(row=10, column=5, rowspan=2, ipadx=112, padx=20, pady=5)

    # RADIO BUTTONS FOR SELECTING INTERIOR VS EXTERIOR
    interior_selected = tk.BooleanVar()

    int_or_ext_btn = tk.Radiobutton(text="Interior", variable=interior_selected, value=True)
    int_or_ext_btn.grid(row=7, column=0, padx=20)

    ext_or_int_btn = tk.Radiobutton(text="Exterior", variable=interior_selected, value=False)
    ext_or_int_btn.grid(row=8, column=0, padx=20)

    """
    The enable_ext_select function enables/disables the three combo boxes depending on whether the custom_sel_checked 
    Checkbutton is checked. 
    """

    def enable_ext_select():
        if custom_sel_checked.get():
            for e_sel in all_exterior_selects:
                e_sel.configure(state="enabled")

        if not custom_sel_checked.get():
            for e_sel in all_exterior_selects:
                e_sel.configure(state="disabled")
                e_sel.set('')

    # Check button for selecting whether original/default url or custom settings should be used for downloading the images.
    custom_sel_checked = tk.BooleanVar()
    custom_sel_check_btn = tk.Checkbutton(text="Customize colour", variable=custom_sel_checked,
                                          command=enable_ext_select)
    custom_sel_check_btn.grid(row=6, column=0, pady=20, padx=20)

    # 3 Comboboxes (drop down) for selecting the exterior colour to be downloaded. Enabled if custom_sel_checked is checked.
    # Their members are retrieved from the exterior.csv file.

    all_list_items = [tk.StringVar() for _ in range(NUM_OF_EXTERIOR_SELECTORS)]
    all_exterior_selects = [ttk.Combobox(window, textvariable=item) for item in all_list_items]

    for idx, ext_sel in enumerate(all_exterior_selects):
        ext_sel.config(state=tk.DISABLED)
        ext_sel['values'] = cp.get_list_of_exterior_codes()
        ext_sel.grid(row=(int(idx / 3) + 6), column=((idx % 3) + 1))



    window.mainloop()


"""
The get_files function, once the submit_btn is clicked, first validates whether the submitted information is sufficient
and correct. If it is, then it calls the get_files function of the csillapics module and passes it the download_options
it has received as an argument. Otherwise displays an error message and returns.
"""


def get_files(download_options, i):
    valid = validators.url(download_options.url)
    if not download_options.customize:
        if download_options.url == "" or download_options.filename == "":
            messagebox.showinfo("info", "Please fill in all fields.")
            return

    elif download_options.url == "" or download_options.filename == "" or download_options.exterior == "":
        messagebox.showinfo("info", "Please fill in all fields.")
        return

    if not valid:
        messagebox.showinfo("Error", f"Please enter a valid url for URL{i}.")
        return

    try:
        cp.get_files(download_options)

    except ValueError as ex:
        messagebox.showinfo("Error", f" ({ex})")


"""
MAIN ENTRY POINT TO THE PROGRAMME.
"""
if __name__ == "__main__":
    create_gui()
