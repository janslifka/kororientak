(function () {
    var inputs = document.querySelectorAll('#id_category input')
    var labels = document.querySelectorAll('#id_category label')
    Array.prototype.map.call(inputs, function ($el) {
        $el.addEventListener('change', function (ev) {
            Array.prototype.map.call(labels, function ($el1) {
                $el1.classList.remove('selected')
            })
            $el.parentElement.classList.add('selected')
        })
    })
})()
