import sys, os, re, json
from matplotlib import pyplot as plt
from collections import OrderedDict as od

class Prop:

    def __init__ (self, path, encoding):

        # ファイルの読み込み
        self.readFile(path, encoding)

        # y 軸のメモリ
        self.noylab = None

        # グラフの枠線
        self.spines = None

        # 図ごとのタイトルの設定
        self.title = None

        # テキスト表示閾値
        self.threshold = None

        # setOptions の実行
        self.setOptions()


    def readFile (self, path, encoding):
        '''
        initial ファイルの読み込み
        '''

        with open(path, "r", encoding=encoding) as rf:
            self.initial = json.load(rf, object_pairs_hook=od)

        # keys の取得
        self.keys = self.initial.keys()

        # key とタイプの対応表の作成
        self.setTable()

        # basis の初期化
        self.basis = None


    def setTable (self):

        self.table = od()

        for key in self.keys:

            # BS データの場合
            if key == "bs" or self.initial[key]["type"] == "bs":
                self.table[key] = "bs"

            # PL データの場合
            elif key == "pl" or self.initial[key]["type"] == "pl":
                self.table[key] = "pl"


    def setOptions (self):
        '''
        self.initial["options"] から設定を取得
        '''

        if "options" in self.keys:
            opt = self.initial["options"]
        else:
            opt = None

        # 日本語フォントの設定
        if opt and "fonts" in opt.keys():
            plt.rcParams['font.family'] = opt["fonts"]
        else:
            plt.rcParams['font.family'] = 'IPAexGothic' 

        # 枠線の有無
        if self.spines:
            pass
        elif opt and "spines" in opt.keys():
            self.spines = True
        else:
            self.spines = None

        # 余白の設定
        plt.rcParams["axes.ymargin"] = 0
        plt.rcParams["axes.xmargin"] = 0
            
        # y 軸の表示の有無
        if self.noylab:
            pass
        elif opt and "noylab" in opt.keys():
            self.noylab = True
        else:
            self.noylab = False

        # テキスト表示閾値
        if self.threshold:
            pass
        elif opt and "threshold" in opt.keys():
            self.threshold = opt["threshold"]
        else:
            self.threshold = 0

        # 図ごとのタイトルの設定
        if self.title:
            pass
        elif opt and "title" in opt.keys():
            self.title = opt["title"]
        else:
            self.title = None

    def getBasis (self):
        '''
        BS の総資産の額と、PL の売上高 (もしくは収益合計)
        を比較し、どちらが大きいか (bs or pl)、 および、
        値を返す
        '''

        # 初期化
        self.basis = 0
        
        # ループ処理
        for key in self.table.keys():

            # BS の場合
            if self.table[key] == "bs":
                self.basis = max(
                    self.basis,
                    sum(self.initial[key]["assets"].values()),
                    sum(self.initial[key]["liabilities"].values())
                )

            # PL の場合
            if self.table[key] == "pl":
                self.basis = max(
                    self.basis,
                    sum(self.initial[key]["income"].values()),
                    sum(self.initial[key]["expenses"].values())
                )


    def prepare (self):
        '''
        作図の準備
        '''

        # basis の取得
        self.getBasis()

        # subplots の設定
        self.subplots = plt.subplots(ncols = len(self.table))

        # 作図
        for i, key in enumerate(self.table.keys()):

            tmplt = self.subplots[1][i] if len(self.table) > 1 else self.subplots[1]

            # bs の処理
            if self.table[key] == "bs":
                self.mkpsbs(tmplt, self.initial[key])

            # pl の処理
            elif self.table[key] == "pl":
                self.mkpspl(tmplt, self.initial[key])

            # タイトルの設定
            if self.title:
                tmplt.set_title(key)

            # x 軸の表示
            if i > 0 and not self.noylab:
                tmplt.tick_params(labelleft = "off")
            
    def show (self):
        self.subplots[0].show()

    def savefig (self, path):
        self.subplots[0].savefig(path, bbox_inches = "tight")

    def mkpspl (self, pltrg, statement):
        '''
        PL データをもとに比例縮尺損益計算書を作成
        '''

        # 利益の計算
        if "earnings" not in statement.keys():
            statement["earnings"] = od(
                [(
                    "営業利益",
                    sum(statement["income"].values()) -
                    sum(statement["expenses"].values())
                )]
            )
            
        # PL の図示

        # 黒字企業の場合
        if sum(statement["earnings"].values()) > 0:

            # 利益
            bottom = self._displayItems(
                pltrg, statement["earnings"],
                1, 0, "#DCEDC8"
            )

            # 費用
            self._displayItems(
                pltrg, statement["expenses"],
                1, bottom, "#FFF9C4"
            )

            # 収益
            self._displayItems(
                pltrg, statement["income"],
                2, 0, "#FFE0B2"
            )

        # 赤字企業の場合
        else:

            # 費用
            self._displayItems(
                pltrg, statement["expenses"],
                1, 0, "#FFF9C4"
            )

            # 損失
            bottom = self._displayItems(
                pltrg, statement["earnings"],
                2, 0, "red"
            )

            # 収益
            self._displayItems(
                pltrg, statement["income"],
                2, bottom, "#FFE0B2"
            )


        # x 軸
        pltrg.tick_params(labelbottom="off", bottom="off")

        # y 軸
        if self.noylab:
            pltrg.tick_params(labelleft="off", left="off")

        # 枠線
        if self.spines:
            pltrg.spines["right"].set_visible(False)
            pltrg.spines["top"].set_visible(False)
            pltrg.spines["left"].set_visible(False)

        # ylim
        if self.basis:
            pltrg.set_ylim((0, self.basis))

    def mkpsbs (self, pltrg, statement):
        '''
        BS データをもとに比例縮尺損益計算書を作成
        '''

        # 純資産合計の計算
        if "equity" not in statement.keys():
            statement["equity"] = od(
                [(
                    "純資産",
                    sum(statement["assets"].values()) -
                    sum(statement["liabilities"].values())
                )]
            )
            
        # BS の図示

        # equity > 0 の場合
        if sum(statement["equity"].values()) > 0:

            # 資産
            self._displayItems(
                pltrg, statement["assets"],
                1, 0, "#C5CAE9"
            )

            # 純資産
            bottom = self._displayItems(
                pltrg, statement["equity"],
                2, 0, "#C8E6C9"
            )

            # 負債
            self._displayItems(
                pltrg, statement["liabilities"],
                2, bottom, "#ffcdd2"
            )


        # 欠損企業の場合
        else:

            # 純資産
            bottom = self._displayItems(
                pltrg, statement["equity"],
                1, 0, "red"
            )

            # 資産
            self._displayItems(
                pltrg, statement["assets"],
                1, bottom, "#C5CAE9"
            )

            # 負債
            self._displayItems(
                pltrg, statement["liabilities"],
                2, 0, "#ffcdd2"
            )

        # x 軸
        pltrg.tick_params(labelbottom="off", bottom="off")

        # y 軸
        if self.noylab:
            pltrg.tick_params(labelleft="off", left="off")

        # 枠線
        if self.spines:
            pltrg.spines["right"].set_visible(False)
            pltrg.spines["top"].set_visible(False)
            pltrg.spines["left"].set_visible(False)

        # ylim
        if self.basis:
            pltrg.set_ylim((0, self.basis))

    # 内部関数
    def _displayItems (self, tmplt, item, left, bottom, color):
        '''
        項目を逆順に表示
        bottom を返す
        '''

        for entry in reversed(item.keys()):

            # plt への格納
            tmplt.bar(
                left, item[entry],
                color=color, edgecolor="black",
                bottom=bottom, width=1.0
            )

            # テキストの挿入
            if self.basis and (item[entry] / self.basis) < self.threshold:
                pass
            else:
                tmplt.text(
                    left,
                    bottom + item[entry] / 2.0,
                    entry, ha="center", va="center"
                )

            # bottom のカウンタを進める
            bottom = bottom + item[entry]


        # bottom を返す
        return bottom
