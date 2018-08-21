# proportional scale

比例縮尺財務諸表の作成

## Features:

- python 3.5; matplotlib 2.0.0
- 財務諸表データをもとに、比例縮尺財務諸表を作成
- シェルコマンドとして利用可能

## Installation

- `# python3 setup.py install` OR
- `$ python3 setup.py install --user`

## Usage:

```
usage: psfs [-h] [--output OUTPUT] [--encoding ENCODING]
            [--extention EXTENTION] [--threshold THRESHOLD] [--title]
            [--noylab] [--spines]
            input [input ...]

positional arguments:
  input                 JSON file

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        image file
  --encoding ENCODING, -e ENCODING
                        encoding (DEFAULT: utf-8)
  --extention EXTENTION, -x EXTENTION
                        extention of image files
  --threshold THRESHOLD, -t THRESHOLD
                        minimum ratio that can display text (DEFAULT: 0.02)
  --title               make default titles (B/S and P/L)
  --noylab, -y          hide ylabs
  --spines, -s          hide spines
```

- 基本的な使い方
    - `$ psfs fs.json` 
        - 同一ディレクトリ上の fs.json に格納されている財務データをもとに描画を表示する
    - `$ psfs fs.json -o fs.png`
        - 描画を `fs.png` という名の画像データとして保存する
    - `$ psfs data/* -o fig/`
        - 財務データとして、複数のファイルを指定できる。その場合、保存先はディレクトリを指定する。

## Preparation:

- 読み込み用データの作成
    - json ファイルの例は以下のとおり
    ```
    {
        "bs" : {
            "assets" : {
                "現金預金" : 1000,
                "売上債権" : 2000,
                "棚卸資産" : 300,
                "その他流動資産" : 1500,
                "有形固定資産" : 7000,
                "投資その他の資産" : 1500
            },
            "liabilities" : {
                "流動負債" : 5000,
                "固定負債" : 3300
            },
            "equity" : {
                "純資産" : 5000
            }
        },
        "pl" : {
            "income" : {
                "売上高" : 14000
            },
            "expenses" : {
                "売上原価" : 7000,
                "販売費及び一般管理費" : 5000
            }
        }
    }
    ```
    - bs もしくは pl のうち少なくともひとつを指定する
    - bs 項目は以下の要素から構成される
        - assets
        - liabilities
        - equity (省略可能)
    - pl 項目は以下の要素から構成される
        - income
        - expenses
        - earnings (省略可能)
        - assets
        - liabilities
