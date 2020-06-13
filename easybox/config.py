#!/usr/bin/env python3
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
