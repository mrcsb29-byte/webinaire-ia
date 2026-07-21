import { Game } from './game.js';

const canvas = document.getElementById('gameCanvas');
canvas.width = 800;
canvas.height = 600;

const game = new Game(canvas);

let mouseX = canvas.width / 2;

window.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
});

function loop(timestamp) {
    if (!previousTime) previousTime = timestamp;
    const dt = (timestamp - previousTime) / 1000;
    previousTime = timestamp;

    game.update(mouseX, dt);
    game.draw();
    requestAnimationFrame(loop);
}

let previousTime = 0;
requestAnimationFrame(loop);
