# -*- coding: utf-8 -*-
import csv
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import TextureRegion
from config import TILE_SIZE, TILESET_COLUMNS, TILESET_IMAGE

def load_csv_as_tilemap(path):
    grid=[]
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            grid.append([int(x) for x in row])
    rows=len(grid); cols=len(grid[0]) if rows else 0
    return grid, rows, cols

def load_tileset_regions():
    sheet = CoreImage(TILESET_IMAGE).texture
    tiles=[]; cols=TILESET_COLUMNS; ts=TILE_SIZE
    rows = sheet.height // ts
    for r in range(rows):
        for c in range(cols):
            x = c*ts; y = sheet.height - (r+1)*ts
            tiles.append(TextureRegion(sheet, x, y, ts, ts))
    return tiles
