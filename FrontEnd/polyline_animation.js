var inputs_value = [0, 0, 0, 0];
var global_data;

ymaps.ready(['AnimatedLine']).then(init);

function init(ymaps) {
    // Создаем карту.
    var myPlacemark, myMap = new ymaps.Map("map", {

        center: [53.21268092272585, 26.97198642737419],
        zoom: 16, color: "#f652a0",
        type: 'yandex#satellite',
        controls: []
    });

    $(document).ready(function () {
        let arr1 = [
            [53.21268092272585, 26.97198642737419], [53.212536266413544, 26.972278886898152], [53.212399149443236, 26.972546165405287], [53.21206373341792, 26.97316975530047], [53.21185412399693, 26.97355160743415], [53.2114577374993, 26.974238869329014], [53.21150351601854, 26.974302541328694], [53.2115644821588, 26.97442970546365], [53.21163686587346, 26.97460795108988], [53.21166734885956, 26.974716229462217], [53.21169018415648, 26.97481155759733], [53.21167111883866, 26.97491983596967], [53.211598735181866, 26.97507254085026], [53.211533999099515, 26.97514250810415], [53.21149199060771, 26.975250786476487], [53.21143867207804, 26.975307983357556], [53.21137005803414, 26.975333524103192], [53.21135487029528, 26.97540978661128], [53.21138147576335, 26.975524360237827], [53.21144631979042, 26.975734441863896], [53.21154541678503, 26.975957113998376], [53.211606382865675, 26.976090753251945], [53.2116826442013, 26.976186261251463], [53.21173219245396, 26.976211622132695], [53.21178163293592, 26.976192736370074], [53.2118540162837, 26.97618644111587], [53.21193027717856, 26.976135539489007], [53.21204456055357, 26.976135539489007], [53.2121474261017, 26.97606557223512], [53.212208499038034, 26.97600190023544], [53.21226558653648, 26.975950998608575], [53.21233032151344, 26.97590009698171], [53.21242564655105, 26.975887326608895], [53.21268092272585, 26.975791998473778], [53.21334786494614, 26.975582096712117], [53.21345072736508, 26.97553749033946], [53.21350415109988, 26.97549935908541], [53.21353463275743, 26.975448457458548], [53.213549819723596, 26.97521931020546], [53.21353075523329, 26.97511750695173], [53.213542172386695, 26.97496480207114], [53.21351933807686, 26.974793031563525], [53.21349650375483, 26.974665687564162], [53.21345460489646, 26.974417474684053], [53.21337834671488, 26.974258474549252], [53.213363051978504, 26.974182032176753], [53.213321152989614, 26.97403562255037], [53.21327548412216, 26.973895688042596], [53.213199225621736, 26.97338649190955], [53.21310777986812, 26.97308108214837], [53.213069650485615, 26.972941147640594], [53.21303152106918, 26.972832869268252], [53.21299339161882, 26.97262278764219], [53.21295536984497, 26.972520984388463], [53.21291724032683, 26.972431951507556], [53.212875340901945, 26.972323852999622], [53.212860045986005, 26.972202804254465], [53.212860045986005, 26.972164673000414], [53.212783786746115, 26.97176375523971], [53.21268092272585, 26.97198642737419]
        ];
        let arr2 = [
            [53.212734163138784, 26.972068548202515], [53.212708463465205, 26.972090005874634], [53.211513411618384, 26.97418212890625], [53.2118765285956, 26.97489559650421], [53.21206927951451, 26.97590410709381], [53.21224275460009, 26.975737810134888], [53.21186367850352, 26.973801255226135], [53.21201787935427, 26.973522305488586], [53.21239374160283, 26.97567880153656], [53.21258006525574, 26.975598335266113], [53.21216565464877, 26.973291635513306], [53.21231654153294, 26.973023414611816], [53.21277913753046, 26.975523233413696], [53.21306825749246, 26.97542667388916], [53.21252545323452, 26.97266936302185], [53.212657164461284, 26.9723904132843], [53.2132288788505, 26.975351572036743], [53.21343447331009, 26.975297927856445], [53.212734163138784, 26.972068548202515]
        ];
       
        $(".button_main").click(function()  {
            let id = $(this).attr("id");

            // console.log(id);
            // console.log($(this))
            if (id == "button1") {

                let field_name;
                field_name = $('#text_poly').html();
                console.log(field_name);
                $.get("http://dan.itatm.keenetic.pro/fields?field_name=&data=" + field_name, function (data, status) {
                    // $('#text2').text(data.score + '%');
                    var ret = data;
                    console.log(data);
                    // console.log(data);
                }, "json");


                myMap.setCenter([53.212734163138784, 26.972068548202515], 16);
                $("#button_build").click(function()  {
                    first_map(arr1, arr2);
                })
            }
            else if (id == "button2") {
                myMap.setCenter([53.2605025616762, 27.375474125146866], 15);
            }
            else if (id == "button3") {
                myMap.setCenter([59.18315110901265, 37.85521745681763], 15);
            }
            else if (id == "button4") {
                myMap.setCenter([55.837689974599186, 37.55972921848297], 17);
            }
        })
    })



    function first_map(arr1, arr2){
        var firstAnimatedLine = new ymaps.AnimatedLine(arr1, {}, {
            // Задаем цвет.
            strokeColor: "#ED4543",
            // Задаем ширину линии.
            strokeWidth: 5,
            // Задаем длительность анимации.
            animationTime: 4000
        });
        var secondAnimatedLine = new ymaps.AnimatedLine(arr2, {}, {
            strokeColor: "#1E98FF",
            strokeWidth: 5,
            animationTime: 4000
        });
        // Добавляем линии на карту.
        myMap.geoObjects.add(secondAnimatedLine);
        myMap.geoObjects.add(firstAnimatedLine);
        // Создаем метки.
        var firstPoint = new ymaps.Placemark([55.7602953585417, 37.57705113964169], {}, {
            preset: 'islands#redRapidTransitCircleIcon'
        });
        var secondPoint = new ymaps.Placemark([55.76127880650197, 37.57839413202077], {}, {
            preset: 'islands#blueMoneyCircleIcon'
        });
        var thirdPoint = new ymaps.Placemark([55.763105418792314, 37.57724573612205], {}, {
            preset: 'islands#blackZooIcon'
        });
        // Функция анимации пути.
        function playAnimation() {
            // Убираем вторую линию.
            secondAnimatedLine.reset();
            // Добавляем первую метку на карту.
            myMap.geoObjects.add(firstPoint);
            // Анимируем первую линию.
            firstAnimatedLine.animate()
                // После окончания анимации первой линии добавляем вторую метку на карту и анимируем вторую линию.
                .then(function () {
                    myMap.geoObjects.add(secondPoint);
                    return secondAnimatedLine.animate();
                })
                // После окончания анимации второй линии добавляем третью метку на карту.
                .then(function () {
                    myMap.geoObjects.add(thirdPoint);
                    // Добавляем паузу после анимации.
                    return ymaps.vow.delay(null, 2000);
                })
                // После паузы перезапускаем анимацию.
                .then(function () {
                    // Удаляем метки с карты.
                    myMap.geoObjects.remove(firstPoint);
                    myMap.geoObjects.remove(secondPoint);
                    myMap.geoObjects.remove(thirdPoint);
                    // Убираем вторую линию.
                    secondAnimatedLine.reset();
                    // Перезапускаем анимацию.
                    playAnimation();
                });
        }
        // Запускаем анимацию пути.
        playAnimation();
    }
    
    


    // Создадим собственный макет выпадающего списка.
    // ListBoxLayout = ymaps.templateLayoutFactory.createClass(
    //     "<button id='my-listbox-header' class='btn btn-success dropdown-toggle' data-toggle='dropdown'>" +
    //     "{{data.title}} <span class='caret'></span>" +
    //     "</button>" +
    //     // Этот элемент будет служить контейнером для элементов списка.
    //     // В зависимости от того, свернут или развернут список, этот контейнер будет
    //     // скрываться или показываться вместе с дочерними элементами.
    //     "<ul id='my-listbox'" +
    //     " class='dropdown-menu' role='menu' aria-labelledby='dropdownMenu'" +
    //     " style='display: {% if state.expanded %}block{% else %}none{% endif %};'></ul>", {

    //     build: function () {
    //         // Вызываем метод build родительского класса перед выполнением
    //         // дополнительных действий.
    //         ListBoxLayout.superclass.build.call(this);

    //         this.childContainerElement = $('#my-listbox').get(0);
    //         // Генерируем специальное событие, оповещающее элемент управления
    //         // о смене контейнера дочерних элементов.
    //         this.events.fire('childcontainerchange', {
    //             newChildContainerElement: this.childContainerElement,
    //             oldChildContainerElement: null
    //         });
    //     },

    //     // Переопределяем интерфейсный метод, возвращающий ссылку на
    //     // контейнер дочерних элементов.
    //     getChildContainerElement: function () {
    //         return this.childContainerElement;
    //     },

    //     clear: function () {
    //         // Заставим элемент управления перед очисткой макета
    //         // откреплять дочерние элементы от родительского.
    //         // Это защитит нас от неожиданных ошибок,
    //         // связанных с уничтожением dom-элементов в ранних версиях ie.
    //         this.events.fire('childcontainerchange', {
    //             newChildContainerElement: null,
    //             oldChildContainerElement: this.childContainerElement
    //         });
    //         this.childContainerElement = null;
    //         // Вызываем метод clear родительского класса после выполнения
    //         // дополнительных действий.
    //         ListBoxLayout.superclass.clear.call(this);
    //     }
    // }),

    //     // Также создадим макет для отдельного элемента списка.
    //     ListBoxItemLayout = ymaps.templateLayoutFactory.createClass(
    //         "<li><a>{{data.content}}</a></li>"
    //     ),

    //     // Создадим 2 пункта выпадающего списка
    //     listBoxItems = [
    //         new ymaps.control.ListBoxItem({
    //             data: {
    //                 content: 'AGROCODE',
    //                 center: [53.212734163138784, 26.972068548202515],
    //                 zoom: 15
    //             }
    //         }),
    //         new ymaps.control.ListBoxItem({
    //             data: {
    //                 content: 'Cherepovets',
    //                 center: [59.18349737628452, 37.855249643325806],
    //                 zoom: 15
    //             }
    //         })
    //     ],

    //     // Теперь создадим список, содержащий 2 пункта.
    //     listBox = new ymaps.control.ListBox({
    //         items: listBoxItems,
    //         data: {
    //             title: 'Выберите пункт'
    //         },
    //         options: {
    //             // С помощью опций можно задать как макет непосредственно для списка,
    //             layout: ListBoxLayout,
    //             // так и макет для дочерних элементов списка. Для задания опций дочерних
    //             // элементов через родительский элемент необходимо добавлять префикс
    //             // 'item' к названиям опций.
    //             itemLayout: ListBoxItemLayout
    //         }
    //     });

    // listBox.events.add('click', function (e) {
    //     // Получаем ссылку на объект, по которому кликнули.
    //     // События элементов списка пропагируются
    //     // и их можно слушать на родительском элементе.
    //     var item = e.get('target');
    //     // Клик на заголовке выпадающего списка обрабатывать не надо.
    //     if (item != listBox) {
    //         myMap.setCenter(
    //             item.data.get('center'),
    //             item.data.get('zoom')
    //         );
    //     }
    // });

    // myMap.controls.add(listBox, { float: 'left' });






    // let counter = 0;
    // var coords = [[0, 0], [0, 0]];



    //var input2 = document.getElementById("1");
    //alert(input2);

    // Слушаем клик на карте.
    // myMap.events.add('click', function (e) {
    //     coords[counter] = e.get('coords');
    //     counter += 1;



    //     // alert(unputs_value[0])
    //     if (counter == 1) {

    //         for (let i = 0; i < global_data.length; i++) {

    //             animatedLine = new ymaps.AnimatedLine(global_data[i]["path"], {}, {});

    //             animatedLine.reset();
    //         }

    //         var firstPoint = new ymaps.Placemark(coords[0], { iconContent: 'start' }, {
    //             preset: 'islands#blueStretchyIcon'
    //         });
    //         myMap.geoObjects.add(firstPoint);
    //     }


    //     // Если метка уже создана – просто передвигаем ее.
    //     if (myPlacemark) {
    //         myPlacemark.geometry.setCoordinates(coords[counter]);
    //     }
    //     // Если нет – создаем.
    //     else {
    //         myPlacemark = createPlacemark(coords[counter]);
    //         myMap.geoObjects.add(myPlacemark);
    //         // Слушаем событие окончания перетаскивания на метке.
    //         myPlacemark.events.add('dragend', function () {
    //             getAddress(myPlacemark.geometry.getCoordinates());
    //         });
    //     }
    //     getAddress(coords[counter]);


    //     if (counter == 2) {

    //         var secPoint = new ymaps.Placemark(coords[1], { iconContent: 'finish' }, {
    //             preset: 'islands#blueStretchyIcon'
    //         });
    //         myMap.geoObjects.add(secPoint);

    //         fetch("https://itam.misis.ru:9996/get_path", {
    //             method: 'POST', headers: {
    //                 'Content-Type': 'application/json'
    //             },
    //             body: JSON.stringify({
    //                 "start_lat": coords[0][0],
    //                 "start_lon": coords[0][1],
    //                 "end_lat": coords[1][0],
    //                 "end_lon": coords[1][1]
    //             })
    //         }).then((response) => {
    //             return response.json();
    //         }).then((data) => {
    //             global_data = data;
    //             //console.log(data[0]["path"]);
    //             generate_lines(data);

    //             if (inputs_value[1] == 1 && inputs_value[3] == 1) { //[0,1,0,1]
    //                 map_print(data, 0);
    //             }

    //             if (inputs_value[1] == 1 && inputs_value[2] == 1) { //[0,1,1,0]
    //                 map_print(data, 1);
    //             }

    //             if (inputs_value[1] == 0 && inputs_value[3] == 1) { //[0,0,0,1]
    //                 map_print(data, 2);
    //             }

    //             if (inputs_value[1] == 1 && inputs_value[2] == 0) { //[0,1,0,0]
    //                 map_print(data, 3);
    //             }

    //             if (inputs_value[0] == 1 && inputs_value[1] == 0) { //[1,0,0,0]
    //                 map_print(data, 4);
    //             }

    //             if (inputs_value[1] == 0 && inputs_value[2] == 1) { //[0,0,1,0]
    //                 map_print(data, 5);
    //             }

    //             if (inputs_value[0] == 1 && inputs_value[1] == 1) { //[1,1,0,0]
    //                 map_print(data, 6);
    //             }

    //             inputs_value = [0, 0, 0, 0];

    //         });


    //         counter = 0;
    //         coords = [[0, 0], [0, 0]];

    //     }
    // });


    // //alert(coords);

    // function generate_lines(data) {


    //     var colors = ["#3EEAD6", "#88E067", "#EDD35F", "#D99571", "#F881DA", "#8189E3", "#4C4047"];

    //     for (let i = 0; i < data.length; i++) {

    //         animatedLine = new ymaps.AnimatedLine(data[i]["path"], {}, {
    //             // Задаем цвет.
    //             strokeColor: colors[i],
    //             // Задаем ширину линии.
    //             strokeWidth: 5,
    //             // Задаем длительность анимации.
    //             animationTime: 5
    //         });

    //         myMap.geoObjects.add(animatedLine);
    //         animatedLine.animate()
    //     }
    // }



    // function createPlacemark(coords) {
    //     return new ymaps.Placemark(coords, {
    //         iconCaption: 'поиск...'
    //     }, {
    //         preset: 'islands#blueMoneyCircleIcon',

    //     });
    // }

    // function getAddress(coords) {
    //     myPlacemark.properties.set('iconCaption', 'поиск...');
    //     ymaps.geocode(coords).then(function (res) {
    //         var firstGeoObject = res.geoObjects.get(0);

    //         myPlacemark.properties
    //             .set({
    //                 // Формируем строку с данными об объекте.
    //                 iconCaption: [
    //                     // Название населенного пункта или вышестоящее административно-территориальное образование.
    //                     firstGeoObject.getLocalities().length ? firstGeoObject.getLocalities() : firstGeoObject.getAdministrativeAreas(),
    //                     // Получаем путь до топонима, если метод вернул null, запрашиваем наименование здания.
    //                     firstGeoObject.getThoroughfare() || firstGeoObject.getPremise()
    //                 ].filter(Boolean).join(', '),
    //                 // В качестве контента балуна задаем строку с адресом объекта.
    //                 balloonContent: firstGeoObject.getAddressLine()
    //             });
    //     });
    // }

    // Слушаем клик на карте.
    myMap.events.add('click', function (e) {
        var coords = e.get('coords');

        // Если метка уже создана – просто передвигаем ее.
        if (myPlacemark) {
            myPlacemark.geometry.setCoordinates(coords);
        }
        // Если нет – создаем.
        else {
            myPlacemark = createPlacemark(coords);
            myMap.geoObjects.add(myPlacemark);
            // Слушаем событие окончания перетаскивания на метке.
            myPlacemark.events.add('dragend', function () {
                getAddress(myPlacemark.geometry.getCoordinates());
            });
        }
        getAddress(coords);
    });

    // Создание метки.
    function createPlacemark(coords) {
        return new ymaps.Placemark(coords, {
            iconCaption: 'поиск...'
        }, {
            preset: 'islands#violetDotIconWithCaption',
            draggable: true
        });
    }

    // Определяем адрес по координатам (обратное геокодирование).
    function getAddress(coords) {
        myPlacemark.properties.set('iconCaption', 'поиск...');
        ymaps.geocode(coords).then(function (res) {
            var firstGeoObject = res.geoObjects.get(0);
            console.log(coords[0], coords[1]);
            document.getElementById("email").value = coords;
            console.log(firstGeoObject.getAddressLine());

            myPlacemark.properties
                .set({
                    // Формируем строку с данными об объекте.
                    iconCaption: [
                        // Название населенного пункта или вышестоящее административно-территориальное образование.
                        firstGeoObject.getLocalities().length ? firstGeoObject.getLocalities() : firstGeoObject.getAdministrativeAreas(),
                        // Получаем путь до топонима, если метод вернул null, запрашиваем наименование здания.
                        firstGeoObject.getAddressLine()
                    ].filter(Boolean).join(', '),
                    // В качестве контента балуна задаем строку с адресом объекта.
                    balloonContent: firstGeoObject.getAddressLine()
                });
        });
    }



    function map_print(data, map_num) {
        //alert("test button pushed");  
        var colors = ["#3EEAD6", "#88E067", "#EDD35F", "#D99571", "#F881DA", "#8189E3", "#4C4047"];

        //for(let i=0; i<data.length; i++){

        animatedLine = new ymaps.AnimatedLine(data[map_num]["path"], {}, {
            // Задаем цвет.
            strokeColor: colors[map_num],
            // Задаем ширину линии.
            strokeWidth: 10,
            // Задаем длительность анимации.
            animationTime: 5
        });

        myMap.geoObjects.add(animatedLine);
        animatedLine.animate()

    }
}


$(document).ready(function () {
    $(".my").change(function() {
        if ($(this).val() != '') $(this).prev().text('Выбрано файлов: ' + $(this)[0].files.length);
        else $(this).prev().text('Выберите файлы');
    });
});



// ПОЛЗУНКИ
function fun1() {
  var rng1=document.getElementById('r1'); //rng - это Input
  var p1=document.getElementById('one'); // p - абзац
  p1.innerHTML=rng1.value;
}
function fun2() {
    var rng2=document.getElementById('r2'); //rng - это Input
    var p2=document.getElementById('two'); // p - абзац
    p2.innerHTML=rng2.value;
  }
  function fun3() {
    var rng3=document.getElementById('r3'); //rng - это Input
    var p3=document.getElementById('three'); // p - абзац
    p3.innerHTML=rng3.value;
  }
  function fun4() {
    var rng4=document.getElementById('r4'); //rng - это Input
    var p4=document.getElementById('four'); // p - абзац
    p4.innerHTML=rng4.value;
  }


//   УДАЛЕНИЕ НЕНУЖНЫХ ЧАСТЕЙ ЯНДЕКС КАРТЫ
  myMap.controls.remove('fullscreenControl');
  myMap.controls.remove('rulerControl');
  myMap.controls.remove('routeButton');
  myMap.controls.remove('geolocationControl');
  myMap.controls.remove('searchControl');
  myMap.controls.remove('trafficControl');
  myMap.controls.remove('button');
  myMap.controls.remove('listBox');
