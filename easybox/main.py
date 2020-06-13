#!/usr/bin/env python3
from collections import OrderedDict
import glob
import os
from pathlib import Path
import sys

from PIL import Image as PIL_Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from tkinter import * # noqa

from tkinter.filedialog import askdirectory, askopenfile


class Config:
    def __init__(self):
        # Supported image formats
        self.supported_img_exts = ['jpg', 'JPG', 'png', 'PNG', 'jpeg', 'JPEG', 'bmp', 'BMP', 'jpe', 'JPE']

        # Default windows width
        self.default_win_width = 1600
        # Default windows height
        self.default_win_height = 760
        # Default canvas width
        self.default_canvas_width = 400
        # Default canvas height
        self.default_canvas_height = 400

        # Mimimal size of bounding box (in pixel).
        self.min_box_size = 2

        # Boundingbox width
        self.box_width = 2
        # Enhanced boundingbox (when selected in boundingbox list) width
        self.enhance_box_width = 5

        # Format of status bar shown at the bottom of windows
        self.status_format = "Directory: {} | Total: {}, Current: {}"

        # All different colors that used in easybox. I get this list from
        # http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
        self.box_colors = [
            'red', 'green', 'yellow', 'hot pink', 'DarkOrange3', 'cornflower blue', 'lime green', 'maroon1',
            'light slate blue', 'DarkSeaGreen3', 'turquoise', 'VioletRed2', 'MediumOrchid1', 'purple', 'black', 'brown',
            'forest green', 'LemonChiffon3', 'dark salmon', 'LightBlue2', 'blue4', 'alice blue', 'orchid3', 'SeaGreen1',
            'AntiqueWhite2', 'thistle1', 'light slate gray', 'firebrick3', 'midnight blue', 'goldenrod4', 'PeachPuff2',
            'DodgerBlue4', 'LavenderBlush4', 'LemonChiffon4', 'LightSkyBlue2', 'LightCyan4', 'dark violet', 'RosyBrown1',
            'firebrick4', 'medium aquamarine', 'salmon2', 'SkyBlue2', 'AntiqueWhite3', 'DarkOrange1', 'DarkOrange2',
            'sienna1', 'SkyBlue3', 'LightYellow2', 'powder blue', 'HotPink3', 'NavajoWhite2', 'SlateBlue2', 'red2',
            'DarkOliveGreen2', 'light goldenrod yellow', 'aquamarine4', 'bisque4', 'lavender', 'orange2', 'sandy brown',
            'linen', 'orchid2', 'gold3', 'LightGoldenrod4', 'SlateBlue3', 'pale goldenrod', 'DarkGoldenrod3'
        ]


cfg = Config()


class EasyBox(tk.Tk):
    def __init__(self):
        """ layout 4x8
        |aaa|bb|
        |aaa|bb|
        |aaa|bb|
        ----------
        |ccc|dd|
        ----------
        |eeeee|
        """
        super(EasyBox, self).__init__()
        self.cfg = cfg

        # Declare global variables
        self.folder_loaded = False
        self.img_paths = []
        self.img_idx = 0
        self.num_imgs = 0
        self.color_id = 0
        self.bboxes = []  # [top, left, bottom, right]

        self.win_width = cfg.default_win_width
        self.win_height = cfg.default_win_height
        self.canvas_height = cfg.default_canvas_height
        self.canvas_width = cfg.default_canvas_width
        self.status_format = cfg.status_format

        self.box_top = 0
        self.box_bottom = 0
        self.box_left = 0
        self.box_right = 0

        self.hor_line = None
        self.ver_line = None
        self.vis_rect = None
        self.vis_move_rect = None
        self.enhance_vis_rect = None
        self.toplevel = None
        self.vis_rect_list = []


        self.box_colors = []
        self.title('EasyBox')

        # Set default window size and offset
        self.geometry('{}x{}+0+0'.format(self.win_width, self.win_height))

        # Create menu
        menu_bar = Menu(self)

        # File
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open", command=self.open_folder, accelerator="Ctrl+O")
        file_menu.add_command(label="Exit", command=self.exit_program, accelerator="Ctrl+Q")

        # Help
        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        help_menu.add_command(label="Shortcut", command=self.open_help_window, accelerator="Ctrl+H")
        help_menu.add_command(label="About EasyBox", command=self.open_about_window, accelerator="Ctrl+A")

        self.config(menu=menu_bar)

        # 4x8
        self.frm_canvas = Frame(self, bg="red" ).grid(row=0, column=0, rowspan=3, columnspan=3)
        self.frm_box = Frame(self, bg="green").grid(row=0, column=3, rowspan=3, columnspan=2)
        self.frm_info = Frame(self, bg="yellow").grid(row=3, column=0, rowspan=1, columnspan=3)
        self.frm_status = Frame(self, bg="purple").grid(row=4, column=0, rowspan=1, columnspan=5)

        # canvas that show image to annotate
        self.canvas = Canvas(self.frm_canvas, height=self.canvas_height, width=self.canvas_width)
        self.canvas.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="NSEW")

        # button to previous / next image
        btn_previous = Button(self.frm_info, text="Previous", fg="red", command=self.load_previous_image)
        btn_previous.grid(row=3, column=0)
        btn_next = Button(self.frm_info, text="Next", fg="green", command=self.load_next_image)
        btn_next.grid(row=3, column=1)
        btn_save = Button(self.frm_info, text="Save", fg="green", command=self.save_bboxes_to_file)
        btn_save.grid(row=3, column=2)

        # box to show information of bboxes
        self.listbox = Listbox(self.frm_box)
        self.listbox.grid(row=0, column=3, rowspan=3, columnspan=2, sticky="NWSE")
        self.box_label = Label(self.frm_box, text="(top, left) -> (bottom, right)")
        self.box_label.grid(row=3, column=3, rowspan=1, columnspan=2, sticky="NW")

        # image status bar
        self.str_status = StringVar()
        label_status = Label(self.frm_status, textvariable=self.str_status)
        label_status.grid(row=4, column=0, rowspan=1, columnspan=5, sticky=W)

        self.bind_all('<Control-q>', self.exit_program)
        self.bind_all('<Control-o>', self.open_folder)
        self.bind_all('<Control-h>', self.open_help_window)
        self.bind_all('<Control-a>', self.open_about_window)
        self.bind_all('<Escape>', self.close_toplevel)

        # Movement
        self.bind_all('<a>', self.load_previous_image)
        self.bind_all('<d>', self.load_next_image)
        self.bind_all('<Left>', self.load_previous_image)
        self.bind_all('<Right>', self.load_next_image)
        self.bind_all('<Button-2>', self.load_previous_image)
        self.bind_all('<Button-3>', self.load_next_image)
        self.bind_all('<Control-s>', self.save_bboxes_to_file)

        # Draw
        self.canvas.bind('<Button-1>', self.left_mouse_click)
        self.canvas.bind('<B1-Motion>', self.left_mouse_motion)
        self.canvas.bind('<ButtonRelease-1>', self.left_mouse_release)
        self.canvas.bind('<Delete>', self.delete_box)
        self.canvas.bind('<Configure>', self.resize_canvas)

        # Edit
        self.listbox.bind('<Delete>', self.delete_box_and_bbox)
        self.bind_all('<Control-z>', self.delete_box)

        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        # when press 'X' on top right of window
        self.protocol("WM_DELETE_WINDOW", self.exit_program)

        self.grid_rowconfigure(0, weight=8)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.mainloop()

    def shorten_folder(self):
        """ When the folder path is too long or window is too small,
            shorten path for nice layout. """
        img_folder = str(self.img_folder)
        if len(img_folder) < self.canvas.winfo_width() / 7:
            return img_folder
        return img_folder[:20] + '...' + img_folder[-20:]

    def open_folder(self, event=None):
        self.img_paths = []
        self.img_folder = askdirectory()
        for ext in cfg.supported_img_exts:
            cur_img_paths = glob.glob(os.path.join(self.img_folder, '*.{}'.format(ext)))
            self.img_paths += cur_img_paths

        self.img_paths = sorted(list(set(self.img_paths)))
        self.num_imgs = len(self.img_paths)
        if self.num_imgs < 1:
            messagebox.showinfo(title="Info", message="No images in this folder!")
        else:
            self.str_status.set(self.status_format.format(self.shorten_folder(), self.num_imgs, self.img_idx+1))

            self.boxes_folder = os.path.join(self.img_folder, 'easybox')
            if not os.path.exists(self.boxes_folder):
                os.makedirs(self.boxes_folder)

            self.load_image_to_label()
            self.load_bboxes_from_file()
            self.folder_loaded = True

    def load_image_to_label(self):
        img = PIL_Image.open(self.img_paths[self.img_idx])
        self.img_width, self.img_height = img.size
        self.img_width_ratio = self.img_width / self.canvas.winfo_width()
        self.img_height_ratio = self.img_height / self.canvas.winfo_height()

        img_resized = img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), PIL_Image.ANTIALIAS)
        self.img_photo = ImageTk.PhotoImage(img_resized)
        self.canvas.create_image(0, 0, anchor=NW, image=self.img_photo)
        self.listbox.delete(0, len(self.bboxes)-1)
        self.color_id = -1
        self.bboxes = []
        self.vis_rect_list = []
        self.enhance_vis_rect = None

    def save_bboxes_to_file(self, event=None):
        boxes_save_path = os.path.join(self.boxes_folder, os.path.basename(self.img_paths[self.img_idx]) + '.txt')
        with open(boxes_save_path, 'w') as f:
            for bbox in self.bboxes:
                f.write('%d %d %d %d %d\n' % (bbox[0], bbox[1], bbox[2], bbox[3], bbox[4]))

    def load_bboxes_from_file(self):
        boxes_save_path = os.path.join(self.boxes_folder, os.path.basename(self.img_paths[self.img_idx]) + '.txt')
        if os.path.exists(boxes_save_path):
            with open(boxes_save_path, 'r') as f:
                for line in f:
                    top, left, bottom, right, color_id = [int(e) for e in line.strip().split(' ')]
                    vis_top, vis_bottom = top / self.img_height_ratio, bottom / self.img_height_ratio
                    vis_left, vis_right = left / self.img_width_ratio, right / self.img_width_ratio
                    self.bboxes.append([top, left, bottom, right, color_id])
                    self.vis_rect = self.canvas.create_rectangle(vis_left, vis_top, vis_right, vis_bottom, width=self.cfg.box_width, outline=self.cfg.box_colors[color_id])
                    self.vis_rect_list.append(self.vis_rect)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' % (top, left, bottom, right))
                    self.listbox.itemconfig(len(self.bboxes) - 1, fg=self.cfg.box_colors[color_id])
                    self.color_id = max(self.color_id, color_id)
        # Use next color
        self.color_id += 1

    def load_previous_image(self, event=None):
        if not self.folder_loaded:
            return
        if self.img_idx > 0:
            self.save_bboxes_to_file()
            self.img_idx -= 1
            self.load_image_to_label()
            self.load_bboxes_from_file()
            self.str_status.set(self.status_format.format(self.shorten_folder(), self.num_imgs, self.img_idx+1))
        else:
            messagebox.showinfo(title="Info", message="This is the first image!")

    def load_next_image(self, event=None):
        if not self.folder_loaded:
            return
        if self.img_idx < self.num_imgs - 1:
            self.save_bboxes_to_file()
            self.img_idx += 1
            self.load_image_to_label()
            self.load_bboxes_from_file()
            self.str_status.set(self.status_format.format(self.shorten_folder(), self.num_imgs, self.img_idx+1))
        else:
            messagebox.showinfo(title="Info", message="This is the last image!")

    def left_mouse_click(self, event=None):
        if not self.folder_loaded:
            return
        self.box_top = event.y
        self.box_left = event.x

    def left_mouse_motion(self, event=None):
        if not self.folder_loaded:
            return
        box_top = max(0, min(self.box_top, self.canvas.winfo_height()))
        box_left = max(0, min(self.box_left, self.canvas.winfo_width()))
        box_bottom = max(0, min(event.y, self.canvas.winfo_height()))
        box_right = max(0, min(event.x, self.canvas.winfo_width()))

        if self.hor_line:
            self.canvas.delete(self.hor_line)
        self.hor_line = self.canvas.create_line(0, box_bottom, self.canvas.winfo_height(), box_bottom, width=self.cfg.box_width)

        if self.ver_line:
            self.canvas.delete(self.ver_line)
        self.ver_line = self.canvas.create_line(box_right, 0, box_right, self.canvas.winfo_width(), width=self.cfg.box_width)

        if self.vis_move_rect:
            self.canvas.delete(self.vis_move_rect)
        self.vis_move_rect = self.canvas.create_rectangle(box_left, box_top, box_right, box_bottom, width=self.cfg.box_width, outline=self.cfg.box_colors[self.color_id])

    def left_mouse_release(self, event=None):
        if not self.folder_loaded:
            return
        self.box_bottom = event.y
        self.box_right = event.x
        box_top = max(0, min(self.box_top, self.canvas.winfo_height()))
        box_left = max(0, min(self.box_left, self.canvas.winfo_width()))
        box_bottom = max(0, min(event.y, self.canvas.winfo_height()))
        box_right = max(0, min(event.x, self.canvas.winfo_width()))
        self.vis_rect = self.canvas.create_rectangle(box_left, box_top, box_right, box_bottom, width=self.cfg.box_width, outline=self.cfg.box_colors[self.color_id])
        self.vis_rect_list.append(self.vis_rect)
        real_top = min(box_top, box_bottom) * self.img_height_ratio
        real_bottom = max(box_top, box_bottom) * self.img_height_ratio
        real_left = min(box_left, box_right) * self.img_width_ratio
        real_right = max(box_left, box_right) * self.img_width_ratio

        # Ignore box that is too small
        if (real_right-real_left) > self.cfg.min_box_size and (real_bottom-real_top) > self.cfg.min_box_size:
            self.bboxes.append([real_top, real_left, real_bottom, real_right, self.color_id])
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(real_top, real_left, real_bottom, real_right))
            self.listbox.itemconfig(len(self.bboxes) - 1, fg=self.cfg.box_colors[self.color_id])
            self.color_id = (self.color_id + 1) % len(self.cfg.box_colors)
        else:
            self.canvas.delete(self.vis_rect)
            self.canvas.delete(self.vis_move_rect)

        self.canvas.delete(self.hor_line)
        self.canvas.delete(self.ver_line)

    def delete_box(self, event=None):
        if not self.folder_loaded:
            return
        if len(self.vis_rect_list) > 0:
            self.canvas.delete(self.vis_move_rect)
            self.canvas.delete(self.vis_rect_list[-1])
            self.vis_rect_list.pop()
            self.bboxes.pop()
            self.listbox.delete(len(self.bboxes))
            if self.enhance_vis_rect is not None:
                self.canvas.delete(self.enhance_vis_rect)

    def delete_box_and_bbox(self, event=None):
        if not self.folder_loaded:
            return
        if len(self.vis_rect_list) > 0:
            self.canvas.delete(self.vis_move_rect)
            selected = self.listbox.curselection()
            # Current we only support select one box each time
            if len(selected) != 1:
                return
            selected_idx = int(selected[0])
            self.canvas.delete(self.vis_rect_list[selected_idx])
            self.canvas.delete(self.enhance_vis_rect)
            self.vis_rect_list.pop(selected_idx)
            self.bboxes.pop(selected_idx)
            self.listbox.delete(selected_idx)

    def resize_canvas(self, event=None):
        w, h = event.width * 2 // 3, event.height * 2 // 3
        self.canvas.config(width=w, height=h)
        if len(self.img_paths) > 0:
            img = PIL_Image.open(self.img_paths[self.img_idx])
            self.img_width, self.img_height = img.size
            self.img_width_ratio = self.img_width / self.canvas.winfo_width()
            self.img_height_ratio = self.img_height / self.canvas.winfo_height()

            img_resized = img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), PIL_Image.ANTIALIAS)
            self.img_photo = ImageTk.PhotoImage(img_resized)
            self.canvas.create_image(0, 0, anchor=NW, image=self.img_photo)

            self.vis_rect_list = []
            self.color_id = 0
            for bbox in self.bboxes:
                top = bbox[0] / self.img_height_ratio
                bottom = bbox[2] / self.img_height_ratio
                left = bbox[1] / self.img_width_ratio
                right = bbox[3] / self.img_width_ratio
                self.vis_rect = self.canvas.create_rectangle(left, top, right, bottom, width=self.cfg.box_width, outline=self.cfg.box_colors[self.color_id])
                self.vis_rect_list.append(self.vis_rect)
                self.color_id += 1

            self.str_status.set(self.status_format.format(self.shorten_folder(), self.num_imgs, self.img_idx+1))

    def on_listbox_select(self, event=None):
        if not self.folder_loaded:
            return
        if len(self.vis_rect_list) > 0:
            selected = self.listbox.curselection()
            if len(selected) != 1:
                return
            selected_idx = int(selected[0])
            top, left, bottom, right, color_id = self.bboxes[selected_idx]
            self.canvas.delete(self.enhance_vis_rect)
            self.enhance_vis_rect = self.canvas.create_rectangle(left/self.img_width_ratio, top/self.img_height_ratio, right/self.img_width_ratio, bottom/self.img_height_ratio, width=self.cfg.enhance_box_width, outline=self.cfg.box_colors[color_id])

    def exit_program(self, event=None):
        if self.folder_loaded:
            self.save_bboxes_to_file()
        sys.exit(0)

    def close_toplevel(self, event=None):
        self.toplevel.destroy()

    def open_about_window(self, event=None):
        about_window = Toplevel(self)
        about_text = Text(about_window)
        about_text.tag_configure("center", justify='center')
        about_content = '''
        A simple but powerful bounding box annotation tool by Python.

        Homepage: https://github.com/vra/easybox
        Author: Yunfeng Wang (wyf.brz@gmail.com)
        '''

        about_text.insert(INSERT, about_content)
        about_text.tag_add("center", "1.0", "end")
        about_text.config(state=DISABLED)
        about_text.pack()

        self.toplevel = about_window

    def open_help_window(self, event=None):
        help_window = Toplevel(self)
        help_text = Text(help_window)
        help_content = '''
        1. Ctrl-O: Open a folder with images
        2. Ctrl-Q: Exit this tool
        3. Ctrl-H: Show help information
        4. Ctrl-A: Show about information '''

        help_text.insert(INSERT, help_content)
        help_text.config(state=DISABLED)
        help_text.pack()

        self.toplevel = help_window


def main():
    win = EasyBox()


if __name__ == '__main__':
    main()
