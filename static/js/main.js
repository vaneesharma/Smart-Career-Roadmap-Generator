// Smart Career Roadmap Generator - main.js
// Plain vanilla JavaScript, no libraries. Handles small UI interactions
// that don't need a full page reload.

document.addEventListener('DOMContentLoaded', function () {

    // ---------------- Dark / Light theme toggle ----------------
    // We save the choice in a cookie instead of localStorage so it works the
    // same way across all pages and survives a browser restart.
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            document.body.classList.toggle('dark-theme');
            const isDark = document.body.classList.contains('dark-theme');
            document.cookie = "theme=" + (isDark ? "dark" : "light") + ";path=/;max-age=" + (60 * 60 * 24 * 30);
            themeToggleBtn.textContent = isDark ? '☀️' : '🌙';
        });
    }

    // ---------------- FAQ accordion on home page ----------------
    document.querySelectorAll('.faq-item').forEach(function (item) {
        item.addEventListener('click', function () {
            item.classList.toggle('open');
        });
    });

    // ---------------- Mobile sidebar toggle ----------------
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show-mobile');
        });
    }

    // ---------------- Auto-hide success/info messages after 4 seconds ----------------
    document.querySelectorAll('.messages li').forEach(function (msg) {
        setTimeout(function () {
            msg.style.opacity = '0';
            setTimeout(function () { msg.remove(); }, 400);
        }, 4000);
    });

    // ---------------- Animate progress bars on page load ----------------
    document.querySelectorAll('.progress-bar-fill').forEach(function (bar) {
        const targetWidth = bar.getAttribute('data-percent') + '%';
        bar.style.width = '0%';
        setTimeout(function () { bar.style.width = targetWidth; }, 200);
    });

});
