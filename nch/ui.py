#!/usr/bin/env python3

import csv
import io
import os
import os.path
import pickle
import sys
import tkinter as tk
from tkinter import ttk
import webbrowser

from pkg_resources import resource_filename

import nch
import nch.cargos

FILL = tk.N + tk.S + tk.W + tk.E


def save_config(data):
    os.makedirs(os.path.dirname(nch.CONFIG_PATH), exist_ok=True)
    with open(nch.CONFIG_PATH, 'wb') as f:
        pickle.dump(data, f)


def load_config():
    try:
        with open(nch.CONFIG_PATH, 'rb') as f:
            data = pickle.load(f)
    except (EOFError, IOError):
        data = None
    return data


class App(tk.Frame):
    def __init__(self, master=None):
        self.init_cargos()
        self.max_cc_lb_height = len(self.cargos.classes)
        tk.Frame.__init__(self, master)
        self.grid(sticky=FILL)
        self.top = self.winfo_toplevel()
        self.create_widgets()
        self.fill_unset()

    def clear_cargos(self):
        self.cargos = nch.cargos.Cargos(ignore_unknown_labels=True)

    def refresh_cargos(self):
        self.cargos.refresh()

    def init_cargos(self):
        conf = load_config()
        if isinstance(conf, nch.cargos.Cargos):
            self.cargos = conf
        else:
            self.clear_cargos()

    def save_cargos(self):
        save_config(self.cargos)

    def busy(self):
        self.top.config(cursor='watch')
        self.top.update()

    def notbusy(self):
        self.top.config(cursor='')
        self.top.update()

    def get_element_index(self, element, listbox):
        for i, e in enumerate(self.get_all_elements(listbox)):
            if e == element:
                return i
        raise KeyError('{} not found in {}'.format(element, listbox))

    def get_element(self, index, listbox):
        return self.element_mapping[listbox.get(index)]

    def get_all_elements(self, *listboxes):
        out = []
        for lb in listboxes:
            for i in range(0, lb.size()):
                out.append(self.get_element(i, lb))
        return tuple(out)

    def get_selected_elements(self, *listboxes):
        out = []
        for lb in listboxes:
            for i in lb.curselection():
                out.append(self.get_element(i, lb))
        return tuple(out)

    def button_command_factory(self, source_listbox, dest_listbox):
        def move(event=None):
            for s in source_listbox.curselection()[::-1]:
                dest_listbox.insert(tk.END, source_listbox.get(s))
                source_listbox.delete(s)
        return move

    def multi_command_factory(self, funcs):
        def iter_funcs(*args, **kwargs):
            for f in funcs:
                f(*args, **kwargs)
        return iter_funcs

    def hyperlink(self, parent, url, **kwargs):
        link = tk.Label(parent, fg='blue', cursor='hand2', **kwargs)
        link.bind('<Button-1>', lambda e: webbrowser.open_new(url))
        return link

    def listbox(self, parent, header, width=20, height=10, scrollbar=True,
                stretchable=True):
        """Make a listbox with header and (optional) scrollbar"""
        frame = tk.Frame(parent)
        lab = tk.Label(frame, text=header)
        lb = tk.Listbox(frame, activestyle='none', exportselection=0,
                        width=width, height=height, selectmode=tk.EXTENDED)
        if scrollbar:
            y_scroll = tk.Scrollbar(frame, command=lb.yview,
                                    orient=tk.VERTICAL)
            y_scroll.grid(column=1, row=1, sticky=tk.N+tk.S)
            lb.config(yscrollcommand=y_scroll.set)
            colspan = 2
        else:
            colspan = 1
        lab.grid(column=0, row=0, columnspan=colspan)
        lb.grid(column=0, row=1, sticky=FILL)
        if stretchable:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
        return frame, lb

    def movement_buttons(self, frame, add_spec, del_spec):
        """Button spec: ('text', source_listbox, target_listbox)"""
        fr = tk.Frame(frame)

        def add_button(spec, row, sticky):
            cmd = self.multi_command_factory([
                self.button_command_factory(spec[1], spec[2]),
                self.sort_listboxes,
                self.update_cc_logic_warnings])
            btn = tk.Button(fr, text=spec[0], command=cmd)
            btn.grid(column=0, row=row, sticky=sticky)
            return btn
        add_btn = add_button(add_spec, 0, tk.S)
        del_btn = add_button(del_spec, 1, tk.N)
        return fr, add_btn, del_btn

    def selectors(self, frame, text):
        fr = tk.Frame(frame)
        label = tk.Label(fr, text=text)
        label.grid(column=0, row=0)
        option_values = ('ANY', 'ALL', 'NONE')
        opts = ttk.Combobox(fr, values=option_values, width=7)
        opts.grid(column=1, row=0)
        opts.state(('!disabled', 'readonly'))
        opts.set('ANY')
        return fr, opts

    def create_widgets(self):
        # Window title
        self.top.title(nch.APPNAME)
        self.top.iconbitmap(resource_filename(__name__, 'newgrf.ico'))
        # Make main window stretchable
        self.top.rowconfigure(0, weight=1)
        self.top.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Menus
        self.menubar = tk.Menu(self.top)
        self.top.config(menu=self.menubar)
        self.submenu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='File', menu=self.submenu)
        clear_cmd = self.multi_command_factory([
            self.busy, self.clear_cargos, self.save_cargos, self.fill_unset,
            self.notbusy])
        self.submenu.add_command(label='Clear labels', command=clear_cmd)
        refresh_cmd = self.multi_command_factory([
            self.busy, self.refresh_cargos, self.save_cargos, self.fill_unset,
            self.notbusy])
        self.submenu.add_command(label='Refresh labels', command=refresh_cmd)
        self.submenu.add_command(label='Exit', command=self.quit)


        # Cargo labels
        # Selection type
        fr, self.cb_label = self.selectors(self, 'Select matching classes:')
        fr.grid(column=0, row=0)
        # Listboxes and buttons
        frame_labels = tk.Frame(self)
        frame_labels.grid(column=0, row=1, rowspan=2, sticky=FILL)
        fr, self.lb_label_allow = self.listbox(
            frame_labels, 'cargo_allow_refit')
        fr.grid(column=0, row=0, sticky=FILL)
        fr, self.lb_label_unset = self.listbox(
            frame_labels, 'Unset cargos')
        fr.grid(column=2, row=0, sticky=FILL)
        fr, self.lb_label_disallow = self.listbox(
            frame_labels, 'cargo_disallow_refit')
        fr.grid(column=4, row=0, sticky=FILL)
        fr, _, _ = self.movement_buttons(
            frame_labels,
            ('<-', self.lb_label_unset, self.lb_label_allow),
            ('->', self.lb_label_allow, self.lb_label_unset))
        fr.grid(column=1, row=0)
        fr, _, _ = self.movement_buttons(
            frame_labels,
            ('->', self.lb_label_unset, self.lb_label_disallow),
            ('<-', self.lb_label_disallow, self.lb_label_unset))
        fr.grid(column=3, row=0)
        frame_labels.rowconfigure(0, weight=1)
        frame_labels.columnconfigure(0, weight=1)
        frame_labels.columnconfigure(2, weight=1)
        frame_labels.columnconfigure(4, weight=1)
        self.label_listboxes = [
            self.lb_label_allow, self.lb_label_unset, self.lb_label_disallow]

        # Cargo classes
        # Selection type
        fr, self.cb_ccs = self.selectors(self, 'Select matching labels')
        fr.grid(column=1, row=0)
        # Listboxes and buttons
        frame_ccs = tk.Frame(self)
        frame_ccs.grid(column=1, row=1, sticky=FILL)
        fr, self.lb_cc_allow = self.listbox(
            frame_ccs, 'refittable_cargo_classes', width=27,
            height=self.max_cc_lb_height, scrollbar=False, stretchable=False)
        fr.grid(column=0, row=0, sticky=FILL)
        fr, self.lb_cc_unset = self.listbox(
            frame_ccs, 'Unset cargo classes', width=27,
            height=self.max_cc_lb_height, scrollbar=False, stretchable=False)
        fr.grid(column=2, row=0, sticky=FILL)
        fr, self.lb_cc_disallow = self.listbox(
            frame_ccs, 'non_refittable_cargo_classes', width=27,
            height=self.max_cc_lb_height, scrollbar=False, stretchable=False)
        fr.grid(column=4, row=0, sticky=FILL)
        fr, _, _ = self.movement_buttons(
            frame_ccs,
            ('<-', self.lb_cc_unset, self.lb_cc_allow),
            ('->', self.lb_cc_allow, self.lb_cc_unset))
        fr.grid(column=1, row=0)
        fr, _, _ = self.movement_buttons(
            frame_ccs,
            ('->', self.lb_cc_unset, self.lb_cc_disallow),
            ('<-', self.lb_cc_disallow, self.lb_cc_unset))
        fr.grid(column=3, row=0)
        self.cc_listboxes = [
            self.lb_cc_allow, self.lb_cc_unset, self.lb_cc_disallow]

        self.all_listboxes = self.label_listboxes + self.cc_listboxes

        # Bind actions to selectors and listboxes
        update_selected_ccs = self.update_listbox_selected_factory(
            self.label_listboxes, self.cc_listboxes, self.cb_label.get)
        self.cb_label.bind('<<ComboboxSelected>>', update_selected_ccs)
        for lb in self.label_listboxes:
            lb.bind('<<ListboxSelect>>', update_selected_ccs)
        update_selected_labels = self.update_listbox_selected_factory(
            self.cc_listboxes, self.label_listboxes, self.cb_ccs.get)
        self.cb_ccs.bind('<<ComboboxSelected>>', update_selected_labels)
        for lb in self.cc_listboxes:
            lb.bind('<<ListboxSelect>>', update_selected_labels)

        # Toolbar frame
        frame_tb = tk.Frame(self)
        frame_tb.grid(column=1, row=2, sticky=FILL)
        # Url to cc logic
        url = 'https://newgrf-specs.tt-wiki.net/wiki/Action0/Cargos#CargoClasses_.2816.29'
        cc_url = self.hyperlink(frame_tb, text=url, url=url)
        cc_url.grid(column=0, row=0, sticky=tk.W)
        # Warning frame
        frame_war = tk.LabelFrame(frame_tb, text='Warnings:')
        frame_war.grid(column=0, row=1, sticky=FILL)
        self.lb_warnings = tk.Label(frame_war, height=13, anchor=tk.NW,
                                    justify=tk.LEFT)
        self.lb_warnings.grid(sticky=FILL)
        # Export buttons
        frame_btns = tk.Frame(frame_tb)
        frame_btns.grid(column=0, row=2, sticky=tk.W)
        btn_export_tsv = tk.Button(frame_btns, text='Copy to clipboard (TSV)',
                                   command=self.export_tsv)
        btn_export_tsv.grid(column=0, row=0, sticky=tk.S+tk.W)
        btn_export_nml = tk.Button(frame_btns, text='Copy to clipboard (NML)',
                                   command=self.export_nml)
        btn_export_nml.grid(column=1, row=0, sticky=tk.S+tk.W)
        btn_export_nml = tk.Button(frame_btns, text='Export cargotable',
                                   command=self.export_cargotable)
        btn_export_nml.grid(column=2, row=0, sticky=tk.S+tk.W)
        frame_tb.rowconfigure(1, weight=1)
        frame_tb.columnconfigure(0, weight=1)

    def export_tsv(self):
        row = []
        row.append(', '.join(
            lb.label for lb in self.get_all_elements(self.lb_label_allow)))
        row.append(', '.join(
            lb.label for lb in self.get_all_elements(self.lb_label_disallow)))
        row.append(', '.join(
            cc.name_nml for cc in self.get_all_elements(self.lb_cc_allow)))
        row.append(', '.join(
            cc.name_nml for cc in self.get_all_elements(self.lb_cc_disallow)))
        # If last element is empty, it wont get pasted to google sheets
        if row[-1] == '':
            row[-1] = ' '

        f = io.StringIO()
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(row)
        self.clipboard_clear()
        self.clipboard_append(f.getvalue())

    def export_nml(self):
        out = []
        for spec in [(self.lb_label_allow, 'cargo_allow_refit'),
                     (self.lb_label_disallow, 'cargo_disallow_refit')]:
            cargos = ', '.join(
                lb.label for lb in self.get_all_elements(spec[0]))
            out.append('{}: [{}];'.format(spec[1], cargos))

        for spec in [(self.lb_cc_allow, 'refittable_cargo_classes'),
                     (self.lb_cc_disallow, 'non_refittable_cargo_classes')]:
            ccs = ', '.join(
                cc.name_nml for cc in self.get_all_elements(spec[0]))
            if ccs:
                ccs = 'bitmask({})'.format(ccs)
            else:
                ccs = 'NO_CARGO_CLASS'
            out.append('{}: {};'.format(spec[1], ccs))
        self.clipboard_clear()
        self.clipboard_append('\n'.join(out))

    def export_cargotable(self):
        labels = ', '.join([lbl.label for lbl in self.cargos.labels])
        self.clipboard_clear()
        self.clipboard_append('cargotable {{\n    {}\n}}'.format(labels))

    def fill_unset(self):
        for lb in self.all_listboxes:
            lb.delete(0, tk.END)
        # Assumes no label will ever have the same name as a class
        self.element_mapping = {}
        for label in self.cargos.labels:
            self.lb_label_unset.insert(tk.END, label)
            self.element_mapping[str(label)] = label
        for cc in self.cargos.classes:
            self.lb_cc_unset.insert(tk.END, cc)
            self.element_mapping[str(cc)] = cc

    def sort_listboxes(self):
        def sort(listboxes, source):
            for lb in listboxes:
                listed = self.get_all_elements(lb)
                lb.delete(0, tk.END)
                for elem in source:
                    if elem in listed:
                        lb.insert(tk.END, elem)
        label_boxes = [self.lb_label_allow, self.lb_label_unset,
                       self.lb_label_disallow]
        sort(label_boxes, self.cargos.labels)
        cc_boxes = [self.lb_cc_allow, self.lb_cc_unset, self.lb_cc_disallow]
        sort(cc_boxes, self.cargos.classes)

    def update_listbox_selected_factory(
            self, clicked_listboxes, target_listboxes, selection_func):

        def update(event):
            selection_mode = selection_func()
            for tlb in target_listboxes:
                tlb.selection_clear(0, tk.END)
            seen_classes = set()

            def any_selector():
                for sel in self.get_selected_elements(*clicked_listboxes):
                    # This is labels for classes, and vice versa
                    seen_classes.update(sel)
                for tlb in target_listboxes:
                    for i in range(0, tlb.size()):
                        if self.get_element(i, tlb) in seen_classes:
                            tlb.selection_set(i)

            def all_selector():
                for sel in self.get_selected_elements(*clicked_listboxes):
                    # This is labels for classes, and vice versa
                    these_classes = set(sel)
                    if not seen_classes:
                        seen_classes.update(these_classes)
                    elif these_classes.isdisjoint(seen_classes):
                        return
                    else:
                        seen_classes.intersection_update(these_classes)
                for tlb in target_listboxes:
                    for i in range(0, tlb.size()):
                        if self.get_element(i, tlb) in seen_classes:
                            tlb.selection_set(i)

            def none_selector():
                for sel in self.get_selected_elements(*clicked_listboxes):
                    # This is labels for classes, and vice versa
                    seen_classes.update(sel)
                for tlb in target_listboxes:
                    for i in range(0, tlb.size()):
                        if self.get_element(i, tlb) not in seen_classes:
                            tlb.selection_set(i)

            selection_modes = {
                'ANY': any_selector,
                'ALL': all_selector,
                'NONE': none_selector
            }

            selector_func = selection_modes[selection_mode]
            selector_func()

        return update

    def update_cc_logic_warnings(self):
        warnings = []
        exclusions = self.get_all_elements(self.lb_cc_disallow)
        for included in self.get_all_elements(self.lb_cc_allow):
            warning = self.cargos.check_inclusion(included, exclusions)
            if warning:
                warnings.append((included, warning))
        inclusions = self.get_all_elements(self.lb_cc_allow)
        for excluded in self.get_all_elements(self.lb_cc_disallow):
            warning = self.cargos.check_exclusion(excluded, inclusions)
            if warning:
                warnings.append((excluded, warning))
        lines = ['{}: {}'.format(w[0].name, w[1]) for w in warnings]
        self.lb_warnings.config(text='\n'.join(lines))
        # Take care to run this AFTER all sorting and moving of elements
        for w in warnings:
            for lb in [self.lb_cc_allow, self.lb_cc_disallow]:
                try:
                    i = self.get_element_index(w[0], lb)
                except KeyError as e:
                    continue
                else:
                    lb.itemconfigure(i, background='red',
                                     selectforeground='red')


def main():
    app = App()
    app.mainloop()
