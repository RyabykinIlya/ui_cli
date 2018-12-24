/**
 * Created by Илья on 29.10.2017.
 */

var fdoc = $(document),
    win = window;

function activateMenuItem() {
    var path = win.location.pathname,
        id;
    if (path.toString() == "/") {
        $('#main').toggleClass('active');
    }
    else {
        path = path.split('/'); // разбиваем url на части и берём категорию ( вид /post/cat_name/1 )
        path = path.filter(function (n) {
            return n != ""
        });
        if (path.length != 1) {
            id = path[1];
        } else {
            id = path[0];
        }
        $('#' + id).toggleClass('active');

    }
};

function toggleCategories(siblings) {
    siblings.toggleClass('subcats');
};


fdoc.ready(function () {
    activateMenuItem();     // активация пунктов меню

    $("#categories").click(function () {     // скрываем/открываем категории
        toggleCategories($(this).parent().siblings());
    });

});


