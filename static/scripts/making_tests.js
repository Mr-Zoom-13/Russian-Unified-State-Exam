$(document).ready(function () {
    vowels = "аеёиоуыэюя"
    open_your_tests()

    function open_your_tests() {
        parent = $('#parent')
        parent.append(`
            <div class="create-thing">
                <h1 class="h1_title">Создать тему</h1>
                <div class="tests_themes d-inline-block">
                    <h3 class="d-inline-block">Название: </h3>
                    <input id="input_theme_title" type="text" class="d-inline-block m-left">
                    <br />
                    <input onclick="create_theme()" class="form-control btn btn-success btn_next d-inline-block m-left" type="submit" value="Создать">
                </div>
                
            </div>
            <div class="create-thing">
                <h1 class="h1_title">Создать подтему</h1>
                <div class="tests_themes d-inline-block">
                    <h3 class="d-inline-block">Название: </h3>
                    <input id="input_subtheme_title" type="text" class="d-inline-block m-left">
                    <br />
                    <h3 class="d-inline-block">Описание: </h3>
                    <input id="input_subtheme_description" type="text" class="d-inline-block m-left">
                    <br />
                    <h3 class="d-inline-block">Тема: </h3>
                    <select class="js-select2 m-left" id="select_themes">
                    </select>
                    <br />
                    <input onclick="create_subtheme()" class="form-control btn btn-success btn_next d-inline-block m-left" type="submit" value="Создать">
                </div>
            </div>
            <div class="create-thing">
                <h1 class="h1_title">Создать задачу</h1>
                <div class="tests_themes d-inline-block">
                    <h3 class="d-inline-block">Тема: </h3>
                    <select class="js-select21 m-left" id="select_themes2">
                    </select>
                    <br />
                    <h3 class="d-inline-block">Подтема: </h3>
                    <select class="js-select22 m-left" id="select_subthemes">
                        <option selected disabled></option>
                    </select>
                    <br /a>
                    <h3 class="d-inline-block">Тип задачи: </h3>
                    <select class="js-select2-type-task m-left">
                        <option selected disabled></option>
                        <option value="0">Выбор буквы</option>
                        <option value="1">Выбор вариантов ответа</option>
                    </select>
                    <div id="create_new_task">
                        
                    </div>
                    <br />
                    <input onclick="make_task()" class="form-control btn btn-success btn_next d-inline-block m-left" type="submit" value="Создать">
                </div>
            </div>
`)
        fetch('/api/get-test/0')
            .then((response) => {
                return response.json();
            })
            .then((myjson) => {
                select_themes = $('#select_themes')
                select_themes2 = $('#select_themes2')
                select_themes.append(`<option selected disabled></option>`)
                select_themes2.append(`<option selected disabled></option>`)
                for (var i = 0; i < myjson.tests.length; i++) {
                    select_themes.append(`<option data-test-id="${myjson.tests[i].id}">${myjson.tests[i].title}</option>`)
                    select_themes2.append(`<option data-test-id="${myjson.tests[i].id}">${myjson.tests[i].title}</option>`)
                }
            });
    }

    function set_type_task(type_task) {
        right = -1
        selected = $(type_task).val()
        create_new_task = $("#create_new_task")
        create_new_task.empty()
        if (selected == "0") {
            create_new_task.append(`
                <h3 class="d-inline-block">Слово: </h3>
                <input id="input_new_task" type="text" class="d-inline-block m-left" onkeyup="view_task()">
                <br />
                <h3 class="d-inline-block">Выберите букву(верную): </h3><div id="choose_right_letter"></div>
            `)
        } else {
            create_new_task.append("Иначе")
        }
    }

    function view_task() {
        new_task = document.getElementById('input_new_task').value;
        parent_div = $('#choose_right_letter')
        parent_div.empty()
        for (var i = 0; i < new_task.length; i++) {
            if (vowels.includes(new_task[i])) {
                parent_div.append(`<h2 id="letter${i}" class="task can_choose_task" data-symbol='${i}' onclick="set_right_answer(this)">${new_task[i]}</h2>`)
            } else {
                parent_div.append(`<h2 class="task">${new_task[i]}</h2>`)
            }
        }
    }

    function set_right_answer(this_) {
        right = Number($(this_).attr('data-symbol'))
        view_task()
        letter = document.getElementById('letter' + String(right))
        letter.classList.add('can_choose_task_hover')
    }


    function set_subthemes(this_) {
        test_id = String($(this_).attr('data-test-id'))
        select_subthemes = $('#select_subthemes')
        select_subthemes.empty()
        select_subthemes.append(`<option selected disabled></option>`)
        fetch('/api/get-subthemes/' + test_id)
            .then((response) => {
                return response.json();
            })
            .then((myjson) => {
                for (var i = 0; i < myjson.subthemes.length; i++) {
                    select_subthemes.append(`<option data-subtheme-id="${myjson.subthemes[i].id}" >${myjson.subthemes[i].title}</option>`)
                }
            });
    }

    function create_theme() {
        title = $('#input_theme_title').val()
        fetch('/api/create-theme/' + title)
            .then((response) => {
                return response.json();
            })
            .then((myjson) => {
                if (myjson.status == 200) {
                    $("#select_themes").append(`<option data-test-id="${myjson.Id}" >${title}</option>`)
                    $("#select_themes2").append(`<option data-test-id="${myjson.Id}" >${title}</option>`)
                }
            });
    }

    function create_subtheme() {
        test_id = $('#select_themes').find('option:selected').attr('data-test-id')
        title = $('#input_subtheme_title').val()
        description = $('#input_subtheme_description').val()
        fetch(`/api/create-subtheme/${test_id}/${title}/${description}`)
            .then((response) => {
                return response.json();
            })
            .then((myjson) => {
                if (myjson.status == 200 && test_id == $('#select_themes2').find('option:selected').attr('data-test-id')) {
                    $("#select_subthemes").append(`<option>${title}</option>`)
                }
            });
    }

    function make_task() {
        if (right != -1) {
            test_id = $('#select_themes').find('option:selected').attr('data-test-id')
            task = $('#input_new_task').val()
            subtheme_id = $('#select_subthemes').find('option:selected').attr('data-subtheme-id')
            type_task = $('.js-select2-type-task').val()
            fetch(`/api/create-task/${subtheme_id}/${task}/${type_task}/${right}`)
                .then((response) => {
                    return response.json();
                })
                .then((myjson) => {
                });
        }
    }


    $(".js-select2").select2({})
    $(".js-select21").select2({})
    $(".js-select22").select2({})
    $(".js-select2-type-task").select2({})
    $('.js-select2').data('select2').$container.addClass('custom-select')
    $('.js-select21').data('select2').$container.addClass('custom-select')
    $('.js-select22').data('select2').$container.addClass('custom-select')
    $('.js-select2-type-task').data('select2').$container.addClass('custom-select')
    $('.js-select2-type-task').on("select2:select", function (e) {

        set_type_task($(this).find('option:selected'))
    });

    $('.js-select21').on("select2:select", function (e) {

        set_subthemes($(this).find('option:selected'))
    });

    window.view_task = view_task
    window.set_right_answer = set_right_answer
    window.make_task = make_task
    window.set_subthemes = set_subthemes
    window.create_theme = create_theme
    window.create_subtheme = create_subtheme
})