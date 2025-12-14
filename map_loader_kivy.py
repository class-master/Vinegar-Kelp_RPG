# -*- coding: utf-8 -*-
"""
map_loader_kivy.py（共通ユーティリティ）

────────────────────────────────────────────────────────────────────
■ 目的
  1) CSVマップ（例: assets/maps/steel_map01.csv）を読み込み、
     2次元グリッド（タイルIDの表）として返す。
  2) タイルセット画像（PNGなど）を読み込み、
     「タイル1枚ずつの“切り出し領域（Texture Region）”」を辞書で返す。

────────────────────────────────────────────────────────────────────
■ 今回の改修の狙い（超重要）
  「相対パスが、実行時のカレントディレクトリに依存して壊れる」問題を防ぎます。

  たとえば main_day1.py を VSCode から実行した場合と、
  どこか別フォルダから `python main_day1.py` した場合で、
  相対パス "assets/..." の意味（参照先）が変わってしまうことがあります。

  そこで本ファイルでは、相対パスを必ず
    「この map_loader_kivy.py が置いてあるフォルダ」
  を基準に解決してからファイルを開きます。

  → これにより、起動方法が変わっても assets が安定して見つかります。
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Kivy の「画像 → Texture化」ユーティリティ
# ここで import してOK（使うのは load_tileset_regions の中）
from kivy.core.image import Image as CoreImage


# =============================================================================
# ✅ 基準ディレクトリ（超重要）
# =============================================================================
# Path(__file__) : この Python ファイル（map_loader_kivy.py）の場所
# resolve()      : .. 等を解決して絶対パス化
# parent         : ファイルの1つ上（= このファイルが入っているフォルダ）
#
# つまり _BASE_DIR は：
#   D:\...\RPG_Steel_MasterD
# のような「プロジェクト直下（想定）」になります。
_BASE_DIR = Path(__file__).resolve().parent


def _resolve_path(path: str | Path) -> Path:
    """
    パス解決ヘルパー（共通化）

    何をする関数？
      - 引数 path が絶対パスなら、そのまま使う
      - 引数 path が相対パスなら、_BASE_DIR を基準に絶対パスへ解決する

    なぜ共通化？
      - CSV でも PNG でも「相対パス地獄」は同じ原因で起こります
      - ここを共通にしておくと、“直す場所が一箇所” になり事故が減ります
    """
    p = Path(path)
    if not p.is_absolute():
        # _BASE_DIR / p で結合し、resolve() で確定した絶対パスへ
        p = (_BASE_DIR / p).resolve()
    return p


# =============================================================================
# 1) CSVマップ読み込み
# =============================================================================
def load_csv_as_tilemap(path: str) -> Tuple[List[List[int]], int, int]:
    """
    CSVマップを読み込み、（grid, rows, cols）を返します。

    引数:
      path : str
        例) "assets/maps/steel_map01.csv"
        - 絶対パスでもOK
        - 相対パスでもOK（この場合、_BASE_DIR 基準に変換してから探します）

    戻り値:
      grid : List[List[int]]
        grid[y][x] に「タイルID（整数）」が入る2次元配列です。
        例）0 は “空” / 1以上は “タイル” として扱うことが多いです。
        ※ 0/1 の意味はプロジェクトの設計に合わせて運用します。

      rows : int
        行数（y方向のサイズ）

      cols : int
        列数（x方向のサイズ）

    失敗時（例外）:
      FileNotFoundError
        ファイルが存在しないとき。
        “解決後の絶対パス” もメッセージに出すので、原因がすぐ分かります。

      ValueError
        CSV内に整数に変換できない値が混ざっていたとき。
        どの行/列が壊れているかが分かるようにメッセージを整えます。
    """

    # -------------------------------------------------------------------------
    # 0) パスを「このファイル基準」で絶対パス化する
    # -------------------------------------------------------------------------
    p = _resolve_path(path)

    # -------------------------------------------------------------------------
    # 1) ファイル存在チェック（見つからない場合は “探した場所” を明示）
    # -------------------------------------------------------------------------
    if not p.exists():
        raise FileNotFoundError(
            f"[map_loader_kivy] Map CSV not found.\n"
            f"  requested: {path}\n"
            f"  resolved : {p}\n"
            f"  hint     : assets/maps 配下にCSVがあるか、ファイル名が一致するか確認してください。"
        )

    # -------------------------------------------------------------------------
    # 2) CSVを読み込む（UTF-8固定で文字化け事故を防ぐ）
    # -------------------------------------------------------------------------
    # CSVの形式は多くの場合：
    #   1,1,1,1,1
    #   1,0,0,0,1
    #   1,0,2,0,1
    #   1,1,1,1,1
    # のように「カンマ区切り整数」です。
    #
    # ★ポイント
    #   - 空行は無視（末尾に改行が多いファイルにも強くなる）
    #   - 行ごとに strip() して余計な空白を除去
    #   - 変換エラー時に “行番号/列番号” を出す
    text = p.read_text(encoding="utf-8")

    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            # 空行はスキップ（CSVの末尾に空行があっても壊れない）
            continue
        lines.append(s)

    # -------------------------------------------------------------------------
    # 3) 行が1つも無い場合は、それはそれで “異常” として扱う
    # -------------------------------------------------------------------------
    if not lines:
        raise ValueError(
            f"[map_loader_kivy] Map CSV is empty.\n"
            f"  resolved : {p}\n"
            f"  hint     : CSVにタイルIDの行が1行以上あるか確認してください。"
        )

    # -------------------------------------------------------------------------
    # 4) 行 → 列へ分解して int に変換して grid を作る
    # -------------------------------------------------------------------------
    grid: List[List[int]] = []
    max_cols = 0

    for row_index, line in enumerate(lines):
        # カンマ区切りで分割し、各要素の前後空白を除去
        parts = [c.strip() for c in line.split(",")]

        row: List[int] = []
        for col_index, cell in enumerate(parts):
            # よくある事故：末尾に「,」があり、最後のセルが空になる
            #   "1,2,3,"  → 最後の cell が "" になる
            # こういうときは 0 扱いにすると運用が安定することが多いです。
            if cell == "":
                row.append(0)
                continue

            try:
                row.append(int(cell))
            except ValueError as e:
                # どこで壊れたかを “具体的に” 出す（生徒さん対応で神）
                raise ValueError(
                    f"[map_loader_kivy] Invalid integer in CSV.\n"
                    f"  resolved : {p}\n"
                    f"  row      : {row_index + 1}\n"
                    f"  col      : {col_index + 1}\n"
                    f"  value    : {cell!r}\n"
                    f"  hint     : CSVは整数（例: 0,1,2...）のみで構成してください。"
                ) from e

        max_cols = max(max_cols, len(row))
        grid.append(row)

    # -------------------------------------------------------------------------
    # 5) 行ごとに列数がバラバラなとき、短い行を 0 で埋めて矩形にする
    # -------------------------------------------------------------------------
    # Kivyで描画ループを書く場合、
    #   for y in range(rows):
    #     for x in range(cols):
    #       tile_id = grid[y][x]
    # のように “必ず矩形” になっている方がコードが簡単で安全です。
    for y in range(len(grid)):
        if len(grid[y]) < max_cols:
            grid[y].extend([0] * (max_cols - len(grid[y])))

    rows = len(grid)
    cols = max_cols
    return grid, rows, cols


# =============================================================================
# 2) タイルセット画像 → タイル領域（Texture Region）切り出し
# =============================================================================
def load_tileset_regions(
    tileset_path: Optional[str] = None,
    tile_size: Optional[int] = None,
    first_gid: int = 1,
) -> Dict[int, object]:
    """
    タイルセット画像（PNGなど）を読み込み、「タイル1枚ずつの領域」を辞書で返します。

    なぜ必要？
      main_day1.py は次の import を前提にしています：
        from map_loader_kivy import load_csv_as_tilemap, load_tileset_regions

      よって、この関数名が存在しないと ImportError で起動不能になります。

    引数:
      tileset_path : str | None
        タイルセット画像のパス。
        None の場合は config.py から “それっぽい変数名” を探して自動取得します。

      tile_size : int | None
        タイル1枚のピクセルサイズ（例: 32）。
        None の場合は config.py の TILE_SIZE を使います。

      first_gid : int
        辞書キーの開始IDです。
        - CSVが 1 を最初のタイルとして使うなら first_gid=1（デフォルト）
        - CSVが 0 を最初のタイルとして使う設計なら first_gid=0
        ※ 多くの教材では 0=空、1〜=タイル なので first_gid=1 が扱いやすいです。

    戻り値:
      regions : dict[int, Texture]
        key   : タイルID（CSVの値と対応させる）
        value : Kivy Texture（get_regionで切り出した“部分Texture”）

        例）tile_id = 5 のとき regions[5] を描画に使える、という設計にします。

    失敗時:
      FileNotFoundError / ValueError
        - tileset画像が見つからない
        - TILE_SIZE が取得できない
      の場合に “何をどう直すか” が分かるメッセージを出します。
    """

    # -------------------------------------------------------------------------
    # 0) config を “遅延 import” する
    # -------------------------------------------------------------------------
    # 理由：
    #   import 時点で循環参照や初期化順序問題を起こしにくくするためです。
    #   （main_day1.py → map_loader_kivy.py → config.py の順序はよく揺れます）
    try:
        import config  # type: ignore
    except Exception as e:
        raise ImportError(
            "[map_loader_kivy] config.py を import できませんでした。\n"
            "  hint: map_loader_kivy.py と同じフォルダに config.py があるか確認してください。"
        ) from e

    # -------------------------------------------------------------------------
    # 1) tile_size を決める（引数が優先、なければ config.TILE_SIZE）
    # -------------------------------------------------------------------------
    if tile_size is None:
        tile_size = getattr(config, "TILE_SIZE", None)

    if not isinstance(tile_size, int) or tile_size <= 0:
        raise ValueError(
            "[map_loader_kivy] tile_size が決まりませんでした。\n"
            "  hint: config.py に TILE_SIZE = 32 のように整数で定義してください。"
        )

    # -------------------------------------------------------------------------
    # 2) tileset_path を決める（引数が優先、なければ config から推測）
    # -------------------------------------------------------------------------
    if tileset_path is None:
        # プロジェクトによって変数名が微妙に違うことがあるので、
        # よくある候補を上から順に探します。
        candidates = [
            "TILESET_PNG",
            "TILESET_PATH",
            "TILESET_IMAGE",
            "TILESET_IMG",
            "TILESET_FILE",
            "TILESET",
        ]
        for name in candidates:
            if hasattr(config, name):
                tileset_path = getattr(config, name)
                break

    if not isinstance(tileset_path, str) or not tileset_path.strip():
        raise ValueError(
            "[map_loader_kivy] タイルセット画像のパスが決まりませんでした。\n"
            "  hint: config.py に次のいずれかを定義してください（例）:\n"
            "    TILESET_PNG = 'assets/tiles/steel_tileset.png'\n"
            "  もしくは load_tileset_regions(tileset_path='...') の引数で渡してください。"
        )

    # -------------------------------------------------------------------------
    # 3) 画像パスを “このファイル基準” で解決して存在確認
    # -------------------------------------------------------------------------
    img_path = _resolve_path(tileset_path)

    if not img_path.exists():
        raise FileNotFoundError(
            f"[map_loader_kivy] Tileset image not found.\n"
            f"  requested: {tileset_path}\n"
            f"  resolved : {img_path}\n"
            f"  hint     : assets/tiles 配下などにPNGがあるか、ファイル名が一致するか確認してください。"
        )

    # -------------------------------------------------------------------------
    # 4) 画像を Texture 化する
    # -------------------------------------------------------------------------
    # CoreImage は “ファイルからTextureを作る” のが得意です。
    # ここで得た texture は「画像全体」なので、get_region で部分切り出しします。
    texture = CoreImage(str(img_path)).texture

    # 画像サイズがタイルサイズの倍数になっているかを軽くチェックします。
    # もちろん “倍数じゃない” 画像も存在し得ますが、教材では倍数が一般的です。
    if texture.width < tile_size or texture.height < tile_size:
        raise ValueError(
            "[map_loader_kivy] tileset画像が tile_size より小さいです。\n"
            f"  image     : {img_path}\n"
            f"  size(px)  : {texture.width} x {texture.height}\n"
            f"  tile_size : {tile_size}\n"
        )

    cols = texture.width // tile_size
    rows = texture.height // tile_size

    if cols <= 0 or rows <= 0:
        raise ValueError(
            "[map_loader_kivy] tileset の列数/行数が計算できませんでした。\n"
            f"  image     : {img_path}\n"
            f"  size(px)  : {texture.width} x {texture.height}\n"
            f"  tile_size : {tile_size}\n"
        )

    # -------------------------------------------------------------------------
    # 5) タイルごとの “部分Texture” を切り出して辞書に詰める
    # -------------------------------------------------------------------------
    # Kivyの Texture 座標系は “左下が原点” です。
    # しかし多くの画像は “左上起点” の感覚で作られがち。
    # ここでは y を反転して、上から下へ順にタイルIDが増える形に揃えます。
    #
    # 例：
    #   画像の左上タイル → first_gid
    #   その右隣         → first_gid+1
    #   ...
    #   次の段（1行下）  → 続きのID
    regions: Dict[int, object] = {}

    tile_id = first_gid
    for ty in range(rows):
        for tx in range(cols):
            x = tx * tile_size

            # y は “上から下” へ進めたいので、Kivy原点（下）に合わせて反転します。
            # 上段(ty=0) → 画像の最上段の y を計算
            y_from_top = ty * tile_size
            y = texture.height - y_from_top - tile_size

            # get_region(x, y, w, h) で部分Textureを作ります
            region = texture.get_region(x, y, tile_size, tile_size)

            regions[tile_id] = region
            tile_id += 1

    # ※必要なら「空タイル(0)」の扱いを揃えるために None を入れる手もありますが、
    #   ここでは “1以上だけ返す” にして、描画側で tile_id==0 をスキップする形が安全です。
    return regions
