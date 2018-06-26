# -*- coding: utf-8 -*-
import json
import os
from collections import OrderedDict
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

FILE_LIST = OrderedDict([
    ('ad', 'プリティーリズムオーロラドリーム'),
    ('dmf', 'プリティーリズムディアマイフューチャー'),
    ('rl', 'プリティーリズムレインボーライブ'),
    ('ass', 'プリティーリズムオールスターセレクション'),
    ('pp', 'プリパラ'),
    ('idpp', 'アイドルタイムプリパラ'),
    ('kpch', 'キラっとプリチャン'),
])

KEY_MAP = OrderedDict([
    ('subtitle', 'サブタイトル'),
    ('scenario', '脚本'),
    ('conte', '絵コンテ'),
    ('storyboard', 'ストーリーボード'),
    ('direction', '演出'),
    ('animation_direction', 'アニメーション演出'),
    ('supervision', '作画監修'),
    ('onair_date', '放送日 (TXN)'),
])


def prepare_date():
    data = dict()
    for key, name in FILE_LIST.items():
        with open('kakuwa/各話リスト_{}.json'.format(name)) as f:
            d = json.load(f)
            data[key] = d
    return data

DATA = prepare_date()


def get(data_, story_id_):
    res = dict()
    for key, item in data_.items():
        res[key] = item[str(story_id_)]
    return res


def search(data_, cond=None):
    print(cond)
    result_index_list = list()
    for key, val in cond.items():
        if key == 'number':
            story_num = int(val)
            if story_num <= 0:
                return '話数は1以上の値を指定してください'
            return get(data_, story_num - 1)
        try:
            mapped_key = KEY_MAP[key]
            koho_dic = data_[mapped_key]
        except KeyError:
            return None
        koho_list = koho_dic.values()
        index_list = list()
        for ind, value in enumerate(koho_list):
            if val in value:
                index_list.append(ind)
        result_index_list.extend(index_list)
    result = list()
    for ind in list(set(result_index_list)):
        result.append(get(data_, ind))
    return result


@app.route('/')
def index():
    return render_template('index.html', series=FILE_LIST, possible_params=KEY_MAP)


@app.route('/story/<series>')
def search_story(series):
    """
    各話リストから条件にあうものをサーチ

    :return:
    """
    params = request.args
    if not params:
        return '検索条件を追加してください'
    possible_param_keys = [
        # 'series',
        'number',
        'subtitle',
        'scenario',
        'conte',
        'storyboard',
        'direction',
        'animation_direction',
        'supervision',
        'onair_date',
    ]


    search_condition = dict()
    for key in possible_param_keys:
        try:
            search_condition[key] = params[key]
        except KeyError:
            pass
    result = search(DATA.get(series, {}), search_condition)
    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    app.debug = False
    app.run()
