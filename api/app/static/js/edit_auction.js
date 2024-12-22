function validateForm(event) {
    const startTime = document.getElementById('start_time').value;
    const endTime = document.getElementById('end_time').value;

    if (endTime < startTime) {
        event.preventDefault();
        alert('Время окончания не может быть меньше времени начала.');
    }
}