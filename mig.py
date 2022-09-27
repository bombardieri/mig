#!/usr/bin/python3

"""
GUI tool that generates a Markdown index of a document written in Markdown.
"""

import tkinter as tk
import tkinter.filedialog as fd
from tkinter import ttk
import collections


class Mainwindow(tk.Frame):

    """
    Specialization of tkinter's Frame that defines the tool's main window.
    """

    def __init__(self, master):
        """ Main window initialization method """
        super().__init__(master)
        self.markdown_index = ''
        self.make_widgets()
        self.pack()

    @staticmethod
    def make_title(title_nums, tokens):
        """ Make titles from tokens in the form "2.3.4. Title" """
        return ".".join(map(str, title_nums)) + ". " + " ".join(tokens[1:])

    def walk_headings(self, filepath):
        """ Update index view and generated md index using file given """
        self.markdown_index = ''
        title_nums = collections.deque([0])
        parents = collections.deque([""])
        latest = ""
        with open(filepath, encoding='utf-8') as file:
            for row in file:
                tokens = row.split(" ")
                if len(tokens) and len(tokens[0]) and \
                        all(map(lambda c: c == '#', tokens[0])):
                    curr_head_depth = len(tokens[0])
                    if curr_head_depth == len(title_nums):
                        title_nums.append(title_nums.pop()+1)
                        latest = self.index_view.insert(
                                parents[-1], tk.END,
                                text=self.make_title(title_nums, tokens)
                            )
                    elif curr_head_depth > len(title_nums):
                        while curr_head_depth > len(title_nums):
                            title_nums.append(1)
                            parents.append(latest)
                            if curr_head_depth == len(title_nums):
                                latest = self.index_view.insert(
                                        parents[-1], tk.END,
                                        text=self.make_title(
                                                        title_nums,
                                                        tokens
                                                    )
                                    )
                            else:
                                latest = self.index_view.insert(
                                        parents[-1], tk.END, text="-"
                                    )
                    else:
                        while curr_head_depth <= len(title_nums):
                            new_title_num = title_nums.pop()+1
                            if curr_head_depth <= len(title_nums):
                                parents.pop()
                        title_nums.append(new_title_num)
                        latest = self.index_view.insert(
                                parents[-1], tk.END,
                                text=self.make_title(title_nums, tokens)
                            )
                    self.markdown_index += " "*4*(len(title_nums)-1)
                    self.markdown_index += str(title_nums[-1])
                    self.markdown_index += ". ["
                    self.markdown_index += row[len(title_nums):].strip()
                    self.markdown_index += "](#"
                    self.markdown_index += "-".join(map(
                                                    lambda s:
                                                    s.strip().lower(),
                                                    tokens[1:]
                                                    ))
                    self.markdown_index += ")\n"

    def open_md(self):
        """ Show a file dialog to open a MD file to generate index """
        filepath = fd.askopenfilename(title="Select markdown file",
                                      filetypes=(('Markdown file', '*.md'),
                                                 ('All files', '*.*')))
        if not filepath:
            return
        for child in self.index_view.get_children():
            self.index_view.delete(child)
        self.filepath_lbl['text'] = filepath
        self.walk_headings(filepath)
        self.btn_export_cb['state'] = tk.NORMAL
        self.btn_export_cb['text'] = 'On clipboard'
        self.btn_export_file['state'] = tk.NORMAL

    def make_widgets(self):
        """ Create application widgets """
        open_pane = tk.LabelFrame(self, text="Chose input file")
        open_pane.pack(padx=10, pady=5, expand=True, fill=tk.X)
        open_btn = tk.Button(open_pane,
                             text="Open markdown file",
                             command=self.open_md)
        open_btn.pack(padx=10, pady=10, expand=True, fill=tk.X)
        self.filepath_lbl = tk.Label(open_pane, text="-")
        self.filepath_lbl.pack(padx=10, pady=0)
        index_pane = tk.LabelFrame(self, text="Generated index")
        index_pane.pack(padx=10, pady=10, expand=True, fill=tk.X)
        self.index_view = ttk.Treeview(index_pane, show="tree")
        self.index_view.pack(padx=10, pady=10, expand=True, fill=tk.X)
        export_pane = tk.LabelFrame(self, text="Export index as markdown")
        export_pane.pack(padx=10, pady=5, expand=True, fill=tk.X)
        self.btn_export_cb = tk.Button(export_pane,
                                       text="On clipboard",
                                       command=self.export_as_md_in_cb,
                                       state=tk.DISABLED)
        self.btn_export_cb.pack(padx=10, pady=5, expand=True, fill=tk.X)
        self.btn_export_file = tk.Button(export_pane,
                                         text="To file",
                                         command=self.export_as_md_in_file,
                                         state=tk.DISABLED)
        self.btn_export_file.pack(padx=10, pady=5, expand=True, fill=tk.X)

    def export_as_md_in_cb(self):
        """ Export generated index to clipboard """
        self.clipboard_clear()
        self.clipboard_append(self.markdown_index)
        self.btn_export_cb['text'] = 'Copied!'

    def export_as_md_in_file(self):
        """ Export generated index to file """
        file = fd.asksaveasfile(mode="w", defaultextension=".md")
        if not file:
            return
        file.write(self.markdown_index)
        file.close()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("350x500")
    root.title("MIG - Markdown Index Generator")
    main_window = Mainwindow(root)
    root.mainloop()
