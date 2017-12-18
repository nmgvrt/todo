# ToDo アプリ

## 概要

グループで利用することを想定した ToDo アプリです.  
外部の ToDo 管理サービスを利用できない環境におすすめです.  
Python の Web アプリケーションフレームワークである Django をベースに作成しました.  
※ 開発中のため予期せぬ不具合が生じる恐れがございます.

## 依存環境

### Python 実行環境

Python 3 (3.5.2 で動作を確認)

### Python パッケージ

- [Django](https://www.djangoproject.com/) (1.11.4 で動作を確認)
- [django-mptt](https://github.com/django-mptt/django-mptt) (0.8.7 で動作を確認)
- [django-bootstrap3](https://github.com/dyve/django-bootstrap3) (8.2.2 で動作を確認)
- [PyYAML](https://pyyaml.org/) (3.12 で動作を確認)

### Web 系フレームワーク・ライブラリ

- [jQuery](https://jquery.com/) (3.2.1 で動作を確認)
- [Moment.js](https://momentjs.com/) (2.20.0 で動作を確認)
- [Bootstrap 3](https://getbootstrap.com/) (3.3.7 で動作を確認)
- [Bootstrap 3 Datepicker](https://eonasdan.github.io/bootstrap-datetimepicker/) (4.17.47 で動作を確認)

## インストール方法

jQuery, Moment.js, Bootstrap は CDN から読み込むためインストール不要です.

### Ubuntu 16.04 の例

#### Python パッケージのインストール
```
$ sudo apt install -y python3 python3-pip pyyaml git
$ sudo pip3 install Django==1.11.8
$ sudo pip3 install django-mptt==0.8.7
$ sudo pip3 install django-bootstrap3
```

#### 必要ファイルの用意

リポジトリをクローンし, static/ に Bootstrap 3 Datepicker から以下の 2 ファイルをコピーしてください.

- bootstrap-datetimepicker.min.css
- bootstrap-datetimepicker.min.js

```
$ git clone https://github.com/nmgvrt/hoge.git
$ [ Bootstrap 3 Datepicker のダウンロード ]
$ [ bootstrap-datetimepicker.min.css, bootstrap-datetimepicker.min.js の配置 ]
```

#### データベースの初期化と管理者の登録

src/ 以下で作業を行ってください.

```
$ python3 manage.py migrate
$ python3 manage.py loaddata colors
$ python3 manage.py createsuperuser
```

#### 開発用サーバでの起動

簡易的に, 開発用サーバで ToDo アプリを起動する方法を示します.  
Django の本運用については, [公式ドキュメント](https://docs.djangoproject.com/ja/2.0/howto/deployment/)を参照してください.

```
$ python3 manage.py runserver 0.0.0.0:8000
```

Web ブラウザから [http://localhost:8000](http://localhost:8000) にアクセスし, ページが表示されれば成功です.
