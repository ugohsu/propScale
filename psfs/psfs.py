import sys, os, re, json
from matplotlib import pyplot as plt
from collections import OrderedDict as od

class Prop:

    def __init__ (self):

        # y 軸のメモリ
        self.noylab = None

        # グラフの枠線
        self.spines = None

        # タイトルの設定
        self.main = None
        self.sub = None

        # y 軸に対する x 軸の比率
        self.xratio = None

        # テキスト表示閾値
        self.threshold = None

        # sharey の初期化
        self.sharey = True

        # basis の初期化
        self.basis = None


    def readFile (self, path, encoding):
        '''
        initial ファイルの読み込み
        '''

        with open(path, "r", encoding=encoding) as rf:
            self.initial = json.load(rf, object_pairs_hook=od)


    def setTable (self):

        self.table = od()

        for key in self.keys:

            # BS データの場合
            if key == "bs" or (
                    "type" in self.initial[key].keys() and 
                    self.initial[key]["type"] == "bs"
            ):
                self.table[key] = "bs"

            # PL データの場合
            elif key == "pl" or (
                    "type" in self.initial[key].keys() and 
                    self.initial[key]["type"] == "pl"
            ):
                self.table[key] = "pl"


    def getYaxis (self):
        '''
        BS の総資産の額と、PL の売上高 (もしくは収益合計)
        を比較し、どちらが大きいか (bs or pl)、 および、
        値を返す
        '''
        # 初期化
        self.yaxis = 0
        # 固定 yaxis が指定されている場合
        if self.basis:
            self.yaxis = self.basis
        else:
            
            # ループ処理
            for key in self.table.keys():
                # BS の場合
                if self.table[key] == "bs":
                    self.yaxis = max(
                        self.yaxis,
                        sum(self.initial[key]["assets"].values()),
                        sum(self.initial[key]["liabilities"].values())
                    )
                    # PL の場合
                if self.table[key] == "pl":
                    self.yaxis = max(
                        self.yaxis,
                        sum(self.initial[key]["income"].values()),
                        sum(self.initial[key]["expenses"].values())
                    )



    def setOptions (self):
        '''
        self.initial["options"] から設定を取得
        '''

        # keys の取得
        self.keys = self.initial.keys()

        # key とタイプの対応表の作成
        self.setTable()

        # options の調査
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

        # 固定 basis
        if self.basis:
            pass
        elif opt and "basis" in opt.keys():
            self.basis = opt["basis"]
        else:
            self.basis = None


        # y 軸に対する x 軸の比率
        if self.xratio:
            pass
        elif opt and "threshold" in opt.keys():
            if opt["threshold"] == "golden":
                self.xratio = 2 / (1 + 5 ** (1/2))
            else:
                self.xratio = float(opt["threshold"])
        else:
            self.xratio = None
        
        # テキスト表示閾値
        if self.threshold:
            pass
        elif opt and "threshold" in opt.keys():
            self.threshold = opt["threshold"]
        else:
            self.threshold = 0

        # メインタイトルの設定
        if self.main:
            pass
        elif opt and "main" in opt.keys():
            self.main = opt["main"]
        else:
            self.main = None

        # 図ごとのタイトルの設定
        if self.sub:
            pass
        elif opt and "sub" in opt.keys():
            self.sub = True
        else:
            self.sub = None

    def prepare (self):
        '''
        作図の準備
        '''

        # subplots の設定
        self.subplots = plt.subplots(
            ncols = len(self.table),
            sharey = self.sharey,
            figsize = self._getFigsize()
        )

        # yaxis の取得
        self.getYaxis()

        # メインタイトルの設定
        if self.main:
            self.subplots[0].suptitle(self.main)

        # 作図
        for i, key in enumerate(self.table.keys()):

            tmplt = self.subplots[1][i] if len(self.table) > 1 else self.subplots[1]

            # bs の処理
            if self.table[key] == "bs":
                self.mkpsbs(tmplt, self.initial[key])

            # pl の処理
            elif self.table[key] == "pl":
                self.mkpspl(tmplt, self.initial[key])

            # サブタイトルの設定
            if self.sub:
                tmplt.set_title(key)

            # x 軸の表示
            if i > 0 and not self.noylab and self.sharey not in ("none", "col"):
                tmplt.tick_params(labelleft = "off")
            
    def show (self):
        self.subplots[0].show()

    def savefig (self, path):
        self.subplots[0].savefig(
            path, bbox_inches = "tight", transparent = True
        )

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
                left, abs(item[entry]),
                color=color, edgecolor="black",
                bottom=bottom, width=1.0
            )

            # テキストの挿入
            if (abs(item[entry]) / self.yaxis) < self.threshold:
                pass
            else:
                tmplt.text(
                    left,
                    bottom + abs(item[entry]) / 2.0,
                    entry, ha="center", va="center"
                )

            # bottom のカウンタを進める
            bottom = bottom + abs(item[entry])


        # bottom を返す
        return bottom

    def _getFigsize (self):

        if self.xratio:
            ysize = plt.rcParams["figure.figsize"][1]
            xsize = ysize * self.xratio
            return xsize, ysize
        else:
            return None
