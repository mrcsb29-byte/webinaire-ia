export class Brick {
    constructor(x, y, width, height, color) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.active = true;
    }

    draw(ctx) {
        if (!this.active) return;
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);

        // Simple highlight effect
        ctx.strokeStyle = 'rgba(255,255,255,0.3)';
        ctx.strokeRect(this.x, this.y, this.width, this.height);
    }

    collide(ball) {
        if (!this.active) return { collided: false };

        const ballLeft = ball.x - ball.radius;
        const ballRight = ball.x + ball.radius;
        const ballTop = ball.y - ball.radius;
        const ballBottom = ball.y + ball.radius;

        if (ballRight > this.x && ballLeft < this.x + this.width &&
            ballBottom > this.y && ballTop < this.y + this.height) {

            this.active = false;

            // Find which side was hit
            const overlapLeft = ballRight - this.x;
            const overlapRight = (this.x + this.width) - ballLeft;
            const overlapTop = ballBottom - this.y;
            const overlapBottom = (this.y + this.height) - ballTop;

            const minOverlap = Math.min(overlapLeft, overlapRight, overlapTop, overlapBottom);

            if (minOverlap === overlapLeft || minOverlap === overlapRight) {
                return { collided: true, axis: 'x' };
            } else {
                return { collided: true, axis: 'y' };
            }
        }
        return { collided: false };
    }
}
