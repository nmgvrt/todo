$(document).ready(function() {
    for(var key in targets) {
        // Django のオリジナルフォームを取得
        var djangoForm = $("#" + key);
        if(!djangoForm[0]) continue;
        var djangoFormContainer = djangoForm.parent();

        // Django のフォームを非表示
        djangoForm.closest(".form-group").hide();

        // カスタムフォームを取得
        var myForm = $("#bm_" + key);
        var myFormContainer = myForm.closest(".form-group");

        // Django のフォームの状態を取得し, カスタムフォームに反映
        if(djangoFormContainer.hasClass("has-error")) {
            myFormContainer.addClass("has-error");
        } else if(djangoFormContainer.hasClass("has-success")) {
            myFormContainer.addClass("has-success");
        }
        console.log(djangoFormContainer)
        if(djangoFormContainer.hasClass("required")) {
            myFormContainer.addClass("required");
        }

        // ラベルとメッセージをカスタムフォームに移動
        djangoFormContainer.find("label").insertBefore(myForm);
        myFormContainer.append(djangoFormContainer.find(".help-block"));

        // ボタンを追加
        var buttonContainer = myForm.find(".button-container");
        buttonContainer.addClass("inline-buttons");
        var isColor = buttonContainer.hasClass("color");

        var html = "";
        djangoForm.find("option").each(function(idx, opt) {
            var val = $(opt).attr("value");
            var display = $(opt).text();
            if(val.length) {
                if(isColor) {
                    html += '<div class="col-xs-6 col-sm-4 col-md-3"><input type="button" class="btn btn-default btn-sm btn-block btn-toggle" data-toggle="tooltip" data-placement="top" value="　" name="' + val + '" style="background: ' + display + ';" title="' + display + '"></div>';
                } else {
                    html += '<div class="col-xs-6 col-sm-4 col-md-3"><input type="button" class="btn btn-default btn-sm btn-block btn-toggle" data-toggle="tooltip" data-placement="top" value="' + display +  '" name="' + val + '" title="' + display + '"></div>';
                }
            }
        });
        buttonContainer.append(html);

        // 初期値があれば反映
        var selected = djangoForm.val();
        console.log(selected)
        var buttons = buttonContainer.find(".btn");
        buttons.each(function(idx, btn) {
            if($.inArray($(btn).attr("name"), selected) >= 0) $(btn).addClass("active");
        });
    }
    $('[data-toggle="tooltip"]').tooltip();

    $('*[type="submit"]').on("click", function(e) {
        e.preventDefault();

        for(var key in targets) {
            var buttons = $("#bm_" + key + " .btn");
            var selected = [];
            buttons.each(function(idx, btn) {
                if($(btn).hasClass("active")) selected.push($(btn).attr("name"));
            });

            var djangoForm = $("#" + key);
            djangoForm.val(selected);
        }

        $("form").submit();
    });

    $(".btn-toggle").on("click", function(e) {
        var key = $(this).closest(".well").attr("id").replace("bm_", "");
        var max = targets[key];
        if(max == 1) {
            $(this).closest(".row").find(".active").each(function() {
                $(this).removeClass("active");
            });
        }

        if ($(this).hasClass("active")) {
            $(this).removeClass("active");
        } else {
            var selected = $(this).closest(".row").find(".active");
            if(Number(max) && selected.length >= max) return;
            $(this).addClass("active");
        }
    });

    $("button.select-all").on("click", function(e) {
        var buttons = $(this).closest(".well").find(".button-container .btn");
        buttons.each(function(e) {
            if(!$(this).hasClass("active")) $(this).addClass("active");
        });
    });
});
