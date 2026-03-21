# field/map_loader_kivy.py
# CSVマップの読み込みとタイル画像の分割を行います。

import csv
from kivy.core.image import Image as CoreImage
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

def load_csv_as_tilemap(path):
    """
    CSVファイルを読み込んで、数値の2次元リストを返します。
    """
    grid = []
    full_path = BASE_DIR / path

    with open(full_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            grid.append([int(tile_id) for tile_id in row])
    
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    # Kivyの座標系に合わせて上下反転させる必要がある場合があります
    grid.reverse() 
    return grid, rows, cols

def load_tileset_regions():
    """
    タイルセット画像を読み込み、各タイルをテクスチャとして切り出します。
    """
    # 実際のリソースパスに合わせて変更してください
    tileset_path = BASE_DIR / "assets" / "maps" / "rustic_tileset.png"
    texture = CoreImage(str(tileset_path)).texture
    ts = 32  # タイルサイズ（configからインポートしても良いです）
    
    # 1枚の画像から各タイルを切り出して辞書に保存します
    tiles = {}
    # 例：0=草地, 1=壁, 2=看板 ...
    # 本来はタイルセットの枚数に合わせてループを回します
    for i in range(10): 
        # get_region(x, y, width, height)
        tiles[i] = texture.get_region(i * ts, 0, ts, ts)
    
    return tiles