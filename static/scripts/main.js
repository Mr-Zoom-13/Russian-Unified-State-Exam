$(document).ready(function () {
    open_tests()
    vowels = "аеёиоуыэюя"

    // get the real id of user
    fetch('/api/get-user-id')
        .then((response) => {
            return response.json();
        })
        .then((myjson) => {
            user_id = myjson.user_id;
        });

    function open_test(this_) {
        test_id = $(this_).attr('data-test-id')
        fetch('/api/get-test/' + test_id)
            .then((response) => {
                return response.json();
            })
            .then((myjson) => {
                subthemes = myjson.subthemes
                console.log(subthemes)
                parent = $('#parent')
                parent.empty()
                parent.append(`<h1 class="h1_title">Подтемы тестов</h1><div class="tests_themes"></div>`)
                parent_div = $('.tests_themes')
                for (var i = 0; i < subthemes.length; i++) {
                    parent_div.append(`<h1 class="test_theme_and_subtheme" data-test-id="${myjson.id}" data-subtheme-id="${subthemes[i].id}" onclick="start_testing(this)">${i + 1}. ${subthemes[i].title}</h1>`)
                }
            });
    }

    function start_testing(this_) {
        test_id = $(this_).attr('data-test-id')
        subtheme_id = $(this_).attr('data-subtheme-id')
        fetch('/api/start-test/' + user_id + '/' + test_id + '/' + subtheme_id)
            .then((response) => {
                return response.json();
            })
            .then((myjson) => {
                task_description = myjson.description
                create_task(myjson)
            });
    }

    function check_right_answer(this_) {
        answer = $(this_).attr('data-symbol')
        if (right_answer == answer) {
            fetch(`/api/next-task/${user_id}/${task_id}/1`)
                .then((response) => {
                    return response.json();
                })
                .then((myjson) => {
                    create_task(myjson)
                });
        } else {
            fetch(`/api/next-task/${user_id}/${task_id}/2`)
                .then((response) => {
                    return response.json();
                })
                .then((myjson) => {
                    trup = myjson
                    parent = $('#parent')
                    first = task.slice(0, right_answer)
                    second = task.slice(right_answer, right_answer + 2).slice(1)
                    right_letter = task[right_answer].toUpperCase()
                    parent.append(`<h2 class="task_description"><span class="wrong_answer">Неверно!</span> Правильный ответ: ${first}<span class="right_answer">${right_letter}</span>${second}</h2><div class="text-center"><input onclick="create_task(trup)" class="form-control btn btn-success btn_next" type="submit" value="Далее"></div>`)
                });
        }
    }


    function create_task(myjson) {
        parent = $('#parent')
        parent.empty()
        if (Object.keys(myjson).includes('success')) {
            parent.append(`
                <h2 class="task_description">Вы успешно завершили тест! Ваша эффективность равна: ${myjson.success}/${myjson.resolved} или же ${Math.round(myjson.success / myjson.resolved * 100)}%!</h2>
                <div class="text-center">
                    <input data-test-id="${test_id}" data-subtheme-id="${subtheme_id}" onclick="start_testing(this)" class="form-control btn btn-success btn_next task_again" type="submit" value="Заново ↺">
                    <br />
                    <input data-test-id="${test_id}" onclick="open_tests()" class="form-control btn btn-success btn_next" type="submit" value="Вернуться к темам">
                    <br />
                    <input data-test-id="${test_id}" onclick="open_test(this)" class="form-control btn btn-success btn_next" type="submit" value="Вернуться к подтемам">
                </div>
            `)
        } else {
            task_id = Number(myjson.task_id)
            task_json = myjson.task.split('/')
            task = task_json[0]
            right_answer = task_json[1]
            parent.append(`<h3 class="task_description">${task_description}</h3><div class="task_div"></div>`)
            parent_div = $('.task_div')
            for (var i = 0; i < task.length; i++) {
                if (vowels.includes(task[i])) {
                    parent_div.append(`<h2 class="task can_choose_task" data-symbol='${i}' onclick="check_right_answer(this)">${task[i]}</h2>`)
                } else {
                    parent_div.append(`<h2 class="task">${task[i]}</h2>`)
                }
            }
        }

    }

    function open_tests() {
        fetch('/api/get-test/0')
            .then((response) => {
                return response.json();
            })
            .then((myjson) => {
                console.log(myjson)
                parent = $('#parent')
                parent.empty()
                parent.append(`<h1 class="h1_title">Темы тестов</h1><div class="tests_themes"></div>`)
                parent_div = $('.tests_themes')
                for (var i = 0; i < myjson.tests.length; i++) {
                    parent_div.append(`<h1 class="test_theme_and_subtheme" data-test-id="${myjson.tests[i].id}" onclick="open_test(this)">${i + 1}. ${myjson.tests[i].title}</h1>`)
                }
            });
    }

    window.open_test = open_test
    window.start_testing = start_testing
    window.check_right_answer = check_right_answer
    window.create_task = create_task
    window.open_tests = open_tests
})

