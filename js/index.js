/**
 * index.js — Trackit landing page logic
 *
 * Handles:
 *  - Animated counter effect for the stats row
 *    Each [data-count] element counts up from 0 to its target
 *    value on page load, with a suffix appended (e.g. "+", "%")
 */

document.addEventListener('DOMContentLoaded', function () {

    /**
     * Animates a single counter element from 0 to its data-count value.
     * @param {HTMLElement} el      - The span with data-count and data-suffix
     * @param {number}      delay   - Milliseconds to wait before starting
     */
    function animateCounter(el, delay) {
        const target = parseInt(el.dataset.count, 10);
        const suffix = el.dataset.suffix || '';
        const duration = 1600;

        setTimeout(function () {
            const startTime = performance.now();

            function tick(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Ease-out cubic — fast start, gentle finish
                const eased = 1 - Math.pow(1 - progress, 3);
                const current = Math.floor(eased * target);

                el.textContent = current + suffix;

                if (progress < 1) {
                    requestAnimationFrame(tick);
                } else {
                    el.textContent = target + suffix;
                }
            }

            requestAnimationFrame(tick);
        }, delay);
    }

    // Run each counter with a small staggered delay for visual effect
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(function (el, index) {
        animateCounter(el, index * 120);
    });

});