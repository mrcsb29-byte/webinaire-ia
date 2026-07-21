export class Ball {
    constructor(x, y, radius, speed) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.speed = speed;
        this.dx = speed;
        this.dy = -speed;
    }

    update(canvasWidth, canvasHeight, paddle, dt) {
        this.x += this.dx * dt * 60;
        this.y += this.dy * dt * 60;

        // Wall collisions (Left/Right)
        if (this.x + this.radius > canvasWidth || this.x - this.radius < 0) {
            this.dx = -this.dx;
        }

        // Top collision
        if (this.y - this.radius < 0) {
            this.dy = -this.dy;
        }

        // Paddle collision
        if (this.y + this.radius > paddle.y &&
            this.y - this.radius < paddle.y + paddle.height &&
            this.x + this.radius > paddle.x && this.x - this.radius < paddle.x + paddle.width) {

            // Calculate hit position on paddle to change bounce angle
            const hitPos = (this.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2);
            this.dx = hitPos * this.speed;
            this.dy = -this.dy;

            // Normalize velocity to maintain constant speed
            const currentSpeed = Math.sqrt(this.dx * this.dx + this.dy * this.dy);
            this.dx = (this.dx / currentSpeed) * this.speed;
            this.dy = (this.dy / currentSpeed) * this.speed;
        }
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        ctx.closePath();
    }

    reset(x, y) {
        this.x = x;
        this.y = y;
        this.dx = this.speed;
        this.dy = -this.speed;
    }
}
