// Countdown timer used on the "take skill test" page.
// Reads the time limit from a data attribute and auto-submits the form when it hits zero.

document.addEventListener('DOMContentLoaded', function () {
    const timerDisplay = document.getElementById('test-timer');
    const testForm = document.getElementById('skill-test-form');
    if (!timerDisplay || !testForm) return;

    let secondsLeft = parseInt(timerDisplay.getAttribute('data-seconds'), 10);

    const countdown = setInterval(function () {
        secondsLeft -= 1;
        const minutes = Math.floor(secondsLeft / 60);
        const seconds = secondsLeft % 60;
        timerDisplay.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;

        if (secondsLeft <= 0) {
            clearInterval(countdown);
            testForm.submit();
        }
    }, 1000);
});
