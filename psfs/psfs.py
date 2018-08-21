import sys, os, re, json
from matplotlib import pyplot as plt
from collections import OrderedDict as od

class Prop:

    def __init__ (self, path, encoding):

        # ファイルの読み込み
        self.readFile(path, encoding)

        # y 軸の最大値
        self.basis = None

        # サブタイトル
        self.bstitle = None
        self.pltitle = None

        # setOptions の実行
        self.setOptions()

    def readFile (self, path, encoding):
        '''
        initial ファイルの読み込み
        '''

        with open(path, "r", encoding=encoding) as rf:
            self.initial = json.load(rf, object_pairs_hook=od)

        # keys の格納
        self.keys = self.initial.keys()


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

        # 余白の設定
        plt.rcParams["axes.xmargin"] = 0
        plt.rcParams["axes.ymargin"] = 0
            
        # y 軸の表示の有無
        if opt and "noylab" in opt.keys():
            self.noylab = True
        else:
            self.noylab = False

        # BS タイトル (タイトル無しの場合は None とする)
        if self.bstitle:
            pass
        elif opt and "bstitle" in opt.keys():
            self.bstitle = opt["bstitle"]
        else:
            self.bstitle = None

        # PL タイトル (タイトル無しの場合は None とする)
        if self.pltitle:
            pass
        elif opt and "pltitle" in opt.keys():
            self.pltitle = opt["pltitle"]
        else:
            self.pltitle = None

    def getBasis (self):
        '''
        BS の総資産の額と、PL の売上高 (もしくは収益合計)
        を比較し、どちらが大きいか (bs or pl)、 および、
        値を返す
        '''

        # keys に bs, pl の両方ともが含まれていない場合は
        # None を返す
        if any(x not in self.keys for x in ("bs", "pl")):
            self.basis = None

        # bs の assets 合計を取得
        assets = sum(self.initial["bs"]["assets"].values())

        # pl の income 合計を取得
        income = sum(self.initial["pl"]["income"].values())

        # より大きな値の出力
        self.basis = max(assets, income)


    def prepare (self):
        '''
        作図の準備
        '''

        # bs および pl の両方が含まれている場合
        if all(x in self.keys for x in ("bs", "pl")):

            self.getBasis()
            self.fig, (self.bs, self.pl) = plt.subplots(ncols=2)
            self.mkpsbs(self.bs, self.initial["bs"])
            self.mkpspl(self.pl, self.initial["pl"])

            # x 軸の表示
            if not self.noylab:
                self.pl.tick_params(labelleft="off")
                
        # bs のみ含まれている場合
        elif "bs" in self.keys:

            self.fig, self.bs = plt.subplots()
            self.mkpsbs(self.bs, self.initial["bs"])

        # pl のみ含まれている場合
        elif "pl" in self.keys:

            self.fig, self.pl = plt.subplots()
            self.mkpspl(self.pl, self.initial["pl"])
            
    def show (self):
        self.fig.show()

    def savefig (self, path):
        self.fig.savefig(path, bbox_inches = "tight")

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

            # 利益
            bottom = self._displayItems(
                pltrg, statement["earnings"],
                2, 0, "#DCEDC8"
            )

            # 収益
            self._displayItems(
                pltrg, statement["income"],
                2, bottom, "#FFE0B2"
            )


        # title
        if self.pltitle:
            pltrg.set_title(self.pltitle)

        # x軸
        pltrg.tick_params(labelbottom="off", bottom="off")

        # y 軸
        if self.noylab:
            pltrg.tick_params(labelleft="off", left="off")

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


        # 赤字企業の場合
        else:

            # 純資産
            bottom = self._displayItems(
                pltrg, statement["equity"],
                1, 0, "#C8E6C9"
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

        # title
        if self.bstitle:
            pltrg.set_title(self.bstitle)

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
            tmplt.text(
                left,
                bottom + item[entry] / 2.0,
                entry, ha="center", va="center"
            )

            # bottom のカウンタを進める
            bottom = bottom + item[entry]


        # bottom を返す
        return bottom
