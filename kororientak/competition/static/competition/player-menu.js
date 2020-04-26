(function () {
    var visible = false
    var taskStatus = document.querySelector('.task-status')
    var taskStatusIcon = document.querySelector('.task-status .fas')
    var taskList = document.querySelector('.task-list')

    taskStatus.addEventListener('click', function () {
        if (visible) {
            taskList.classList.remove('visible')
            taskStatusIcon.classList.remove('fa-chevron-up')
            taskStatusIcon.classList.add('fa-chevron-down')
            visible = false
        } else {
            taskList.classList.add('visible')
            taskStatusIcon.classList.add('fa-chevron-up')
            taskStatusIcon.classList.remove('fa-chevron-down')
            visible = true
        }
    })
})()
