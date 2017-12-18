var ajaxData = {};

function show(key) {
    var dom = $("#" + key + "-body");
    var parent = dom.closest(".json-multiple-sub-frame");
    parent.find(".hidden-container").hide();
    dom.show();
}

function setDom(key) {
    var body = $("#" + key + "-body");

    var data = ajaxData[key];
    if(data.length) {
        var html = "";
        for(var i = 0; i < data.length; i++) {
            var info = data[i];
            if("color" in info) {
                html += '<div class="col-xs-6 col-sm-4 col-md-3 color"><input type="button" class="btn btn-default btn-block btn-sm" data-toggle="button tooltip" data-placement="top" aria-pressed="false" autocomplete="off" style="background: ' + info.color + ';" value="' + info.display +  '" name="' + info.pk + '" title="' + info.display + '"></div>';
            } else {
                html += '<div class="col-xs-6 col-sm-4 col-md-3"><input type="button" class="btn btn-default btn-block btn-sm" data-toggle="button tooltip" data-placement="top" aria-pressed="false" autocomplete="off" value="' + info.display +  '" name="' + info.pk + '" title="' + info.display + '"></div>';
            }
        }
    } else {
        var html = '<p class="text-center">選択可能なものがありません.</p>';
    }

    body.html(html);
}

function getValue(key) {
    var root = $("#" + key);
    var info = jsonMultipleInfo[key];

    if(info.mode == 'selected') {
        var selectedTab = root.find(".switcher .active input").attr("id");
        var searchRoot = $("#" + selectedTab + "-body");
        var selected = $("#" + selectedTab + "-body").find("input.active");
    } else if(info.mode == 'all') {
        var selected = root.find(".json-multiple-sub-frame input.active");
    } else {
        var selected = [];
    }

    var values = [];
    for(var i = 0; i < selected.length; i++) values.push(Number($(selected[i]).attr('name')));

    return values;
}

function loadData(root, key) {
    $.ajax({
        type: "GET",
        url: jsonMultipleInfo[root]['children'][key],
        dataType: "json"
    }).done(function(data) {
        ajaxData[key] = data;
    });
}


$(document).ready(function() {
    var ready = false;

    // .json-multiple の対象となるカスタムフォームを取得
    var multiples = [];
    var domMultiples = $(".json-multiple");
    for(var i = 0; i < domMultiples.length; i++) {
        var key = domMultiples[i].id;
        if(key in jsonMultipleInfo) multiples.push(key);
    }

    var count = 0;
    for(var i = 0; i < multiples.length; i++) {
        // データ (json) を取得
        var id = multiples[i];
        var children = jsonMultipleInfo[id]['children'];
        for(var key in children) {
            loadData(id, key);
            count++;
        }

        // タブが切り替えられたら,
        // データの読み込みが終わっていれば切り替えるように登録
        var root = $("#" + id);
        root.on("click", ".switcher label", function(e) {
            if(!ready) return;

            var target = $(e.target).find("input").first().attr("id");
            show(target);
        });

        // Django のフォームを非表示
        $("#" + id.replace('set-', 'id_')).parent().hide();
    }

    setTimeout(function() {
        if(Object.keys(ajaxData).length == count) {
            for(var key in ajaxData) {
                // 読み込んだデータをボタンとしてカスタムフォームに追加
                setDom(key);

                // Django のフォームを取得
                var djangoFormName = $("#" + key + "-body").closest(".json-multiple").attr("id").replace("set-", "id_");
                var djangoForm = $("#" + djangoFormName).parent();

                // .help-block (メッセージ) とラベルをカスタムフォームに移動
                var helpText = djangoForm.find(".help-block");
                var label = djangoForm.find("label");
                var root = $("#" + key).closest(".json-multiple");
                var body = root.find(".json-multiple-frame").first();
                root.append(helpText);
                label.insertBefore(body);

                // Django のフォームで状態が設定されていたらカスタムフォームに反映
                if(djangoForm.hasClass("has-error")) {
                    root.addClass("has-error");
                } else if(djangoForm.hasClass("has-success")) {
                    root.addClass("has-success");
                }

                // Django フォームに値が設定されていればカスタムフォームに反映
                var djangoValues = $("#" + djangoFormName).val();
                for(var i = 0; i < djangoValues.length; i++) {
                    var button = $("#" + key + "-body").find('input[name="' + djangoValues[i] + '"]');
                    if(button) {
                        button.addClass("active");
                    }
                }
            }

            // カスタムフォームのタブを初期設定に変更
            for(var i = 0; i < multiples.length; i++) {
                var target = jsonMultipleInfo[multiples[i]]['initial'];
                show(target);
            }

            // ツールチップを有効化
            $('[data-toggle="button tooltip"]').tooltip();

            ready = true;
        } else {
            setTimeout(arguments.callee, 50);
        }
    });

    $('button[type="submit"]').on("click", function(e) {
        e.preventDefault();

        for(var i = 0; i < multiples.length; i++) {
            var key = multiples[i];
            var formValues = getValue(key);

            var djangoFormName = key.replace('set-', 'id_');
            $("#" + djangoFormName).val(formValues);
        }

        $(e.target).closest("form").submit();
    });
});
