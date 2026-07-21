import { Brick } from './brick.js';
import { Ball } from './ball.js';
import { Paddle } from './paddle.js';
import { Particle } from './particle.js';

const LEVEL_DATA = [
    {
        layout: [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ],
        ballSpeed: 4,
    },
    {
        layout: [
            [1, 0, 1, 0, 1, 0, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 1, 0, 1, 0],
        ],
        ballSpeed: 5,
    },
    {
        layout: [
            [1, 1, 0, 1, 1, 0, 1, 1],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 0, 1, 1, 1, 1, 0, 1],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 0, 1, 1, 0, 1, 1],
        ],
        ballSpeed: 6,
    },
];

export class Game {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;

        this.score = 0;
        this.highScore = parseInt(localStorage.getItem('brickBreakerHighScore')) || 0;
        this.lives = 3;
        this.level = 1;
        this.gameOver = false;
        this.gameWon = false;

        this.paddle = new Paddle(this.width / 2 - 50, this.height - 30, 100, 15, '#00ffcc');
        this.ball = new Ball(this.width / 2, this.height - 50, 8, 4);
        this.bricks = [];
        this.particles = [];
        this.initBricks();

        this.scoreElement = document.getElementById('score');
        this.highScoreElement = document.getElementById('highScore');
        this.livesElement = document.getElementById('lives');
    }

    initBricks() {
        const level = LEVEL_DATA[this.level - 1];
        const layout = level.layout;
        const rows = layout.length;
        const cols = layout[0].length;
        const padding = 10;
        const offsetTop = 50;
        const offsetLeft = 30;
        const brickWidth = (this.width - (offsetLeft * 2)) / cols - padding;
        const brickHeight = 20;
        const colors = ['#ff4d4d', '#ff944d', '#ffdb4d', '#94ff4d', '#4dffdb'];

        this.bricks = [];
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (layout[r][c] === 1) {
                    const bx = c * (brickWidth + padding) + offsetLeft;
                    const by = r * (brickHeight + padding) + offsetTop;
                    this.bricks.push(new Brick(bx, by, brickWidth, brickHeight, colors[r % colors.length]));
                }
            }
        }
    }

    spawnParticles(x, y, color) {
        for (let i = 0; i < 15; i++) {
            this.particles.push(new Particle(x, y, color));
        }
    }

    saveHighScore() {
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('brickBreakerHighScore', this.highScore);
            console.log(`New High Score saved: ${this.highScore}!`);
            this.updateUI();
        }
    }

    update(mouseX, dt) {
        if (this.gameOver || this.gameWon) return;

        this.paddle.update(mouseX, this.width);
        this.ball.update(this.width, this.height, this.paddle, dt);

        // Update particles
        this.particles.forEach(p => p.update(dt));
        this.particles = this.particles.filter(p => p.life > 0);

        // Ball’s bottom collision (Life loss)
        if (this.ball.y + this.ball.radius > this.height) {
            this.lives--;
            this.updateUI();
            if (this.lives <= 0) {
                this.gameOver = true;
                this.saveHighScore();
            } else {
                this.ball.reset(this.width / 2, this.height - 50);
                this.paddle.x = this.width / 2 - 50;
            }
        }

        // Brick collisions
        let bricksRemaining = 0;
        for (let brick of this.bricks) {
            if (brick.active) {
                bricksRemaining++;
                const collision = brick.collide(this.ball);
                if (collision.collided) {
                    this.spawnParticles(brick.x + brick.width / 2, brick.y + brick.height / 2, brick.color);
                    this.score += 10;
                    this.updateUI();
                    if (collision.axis === 'x') {
                        this.ball.dx = -this.ball.dx;
                    } else {
                        this.ball.dy = -this.ball.dy;
                    }
                }
            }
        }

        if (bricksRemaining === 0) {
            if (this.level < LEVEL_DATA.length) {
                this.level++;
                const levelConfig = LEVEL_DATA[this.level - 1];
                this.ball.speed = levelConfig.ballSpeed;
                this.ball.dx = levelConfig.ballSpeed;
                this.ball.dy = -levelConfig.ballSpeed;
                this.ball.reset(this.width / 2, this.height - 50);
                this.paddle.x = this.width / 2 - 50;
                this.initBricks();
            } else {
                this.gameWon = true;
                this.saveHighScore();
            }
        }
    }

    updateUI() {
        this.scoreElement.innerText = this.score;
        this.highScoreElement.innerText = this.highScore;
        this.livesElement.innerText = this.lives;
    }

    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        this.paddle.draw(this.ctx);
        this.ball.draw(this.ctx);
        for (let brick of this.bricks) {
            brick.draw(this.ctx);
        }

        // Draw particles
        this.particles.forEach(p => p.draw(this.ctx));

        if (this.gameOver) {
            this.drawText('GAME OVER', 'red');
        } else if (this.gameWon) {
            this.drawText('YOU WIN!', '#00ffcc');
        }
    }

    drawText(text, color) {
        this.ctx.fillStyle = color;
        this.ctx.font = '40px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(text, this.width / 2, this.height / 2);
    }
}
