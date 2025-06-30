// static/js/modes/starUtils.js - Utility functions for star handling
import { gameState, gameSettings, sounds, updateScore } from '../gameState.js';
import { assets } from '../assets.js';

/**
 * Checks if a star overlaps with any existing pipes.
 * Used in pipes-and-stars mode to avoid uncollectible stars.
 * @param {number} starX - Proposed X position of the star.
 * @param {number} starY - Proposed Y position of the star.
 * @param {number} starWidth - Width of the star.
 * @param {number} starHeight - Height of the star.
 * @param {HTMLCanvasElement} canvas - The game canvas.
 * @returns {boolean} True if the star overlaps with a pipe, false otherwise.
 */
function isStarOverlappingPipe(starX, starY, starWidth, starHeight, canvas) {
    const starLeft = starX;
    const starRight = starX + starWidth;
    const starTop = starY;
    const starBottom = starY + starHeight;

    for (const pipe of gameState.pipes) {
        const pipeLeft = pipe.x;
        const pipeRight = pipe.x + pipe.width;
        const pipeTopOpening = pipe.topHeight; // Top of the gap
        const pipeBottomOpening = pipe.bottomY; // Bottom of the gap (top of the lower pipe visually)

        // Check for horizontal overlap
        if (starRight > pipeLeft && starLeft < pipeRight) {
            // Check if star is within the solid part of the top pipe
            if (starBottom > 0 && starTop < pipeTopOpening) {
                return true; // Overlaps with top pipe solid part
            }
            // Check if star is within the solid part of the bottom pipe
            if (starTop < canvas.height - gameState.ground.height && starBottom > pipeBottomOpening) {
                return true; // Overlaps with bottom pipe solid part
            }
        }
    }
    return false;
}

/**
 * Creates a star object.
 * @param {HTMLCanvasElement} canvas - The game canvas.
 * @param {boolean} checkPipeOverlap - Whether to check for overlap with pipes.
 * @returns {object|null} The star object or null if overlap check fails.
 */
function createStar(canvas, checkPipeOverlap) {
    const bird = gameState.bird;
    const minY = Math.max(50, bird.height * 2); // Ensure star is not too high
    const maxY = canvas.height - gameState.ground.height - 50 - bird.height; // Ensure star is not too low or in ground
    let x = canvas.width + Math.random() * 100; // Start off-screen to the right
    let y = minY + Math.random() * (maxY - minY);

    const isBigStar = Math.random() < gameState.bigStarChance;
    const starWidth = isBigStar ? 40 : 25; // Adjusted sizes
    const starHeight = isBigStar ? 40 : 25;

    if (checkPipeOverlap) {
        let attempts = 0;
        const maxAttempts = 15;
        while (attempts < maxAttempts) {
            if (!isStarOverlappingPipe(x, y, starWidth, starHeight, canvas)) {
                break; // Found a good position
            }
            // Try a new position further to the right if overlapping
            x += 50 + Math.random() * 50;
            y = minY + Math.random() * (maxY - minY); // Also new Y
            attempts++;
            if (attempts >= maxAttempts) {
                console.warn("Could not place star without overlapping pipe after multiple attempts.");
                return null; // Failed to place star without overlap
            }
        }
    }

    return {
        x: x,
        y: y,
        width: starWidth,
        height: starHeight,
        collected: false,
        speed: gameState.pipeSpeed, // Stars move slightly slower than pipes or at their own speed
        isBigStar: isBigStar,
        points: isBigStar ? 3 : 1 // Points for big and regular stars
    };
}

/**
 * Draws all active stars onto the canvas.
 * @param {CanvasRenderingContext2D} ctx - The canvas rendering context.
 */
function drawStars(ctx) {
    gameState.stars = gameState.stars.filter(star => star.x + star.width > 0 && !star.collected);

    for (const star of gameState.stars) {
        star.x -= star.speed; // Move star based on its own speed or game speed

        if (!star.collected) {
            ctx.save();
            const pulse = 1 + 0.08 * Math.sin(Date.now() / 180); // Slower, subtler pulse
            ctx.translate(star.x + star.width / 2, star.y + star.height / 2);
            // Removed rotation for simplicity, can be added back if desired
            // ctx.rotate(Date.now() / 1000);
            ctx.scale(pulse, pulse);

            const starAsset = star.isBigStar ? assets.bigStar : assets.star; // Use different assets if available
            if (starAsset && starAsset.complete) {
                ctx.drawImage(starAsset, -star.width / 2, -star.height / 2, star.width, star.height);

                if (star.isBigStar) { // Optional glow for big stars
                    const gradient = ctx.createRadialGradient(0, 0, star.width / 5, 0, 0, star.width * 0.7);
                    gradient.addColorStop(0, 'rgba(255, 255, 100, 0.25)');
                    gradient.addColorStop(1, 'rgba(255, 255, 100, 0)');
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(0, 0, star.width * 0.7, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            ctx.restore();
        }
    }
}

/**
 * Checks for collisions between the bird and stars.
 * Handles scoring and sound effects for star collection.
 */
function checkStarCollisions() {
    const bird = gameState.bird;
    let starCollectedThisFrame = false;

    for (const star of gameState.stars) {
        if (!star.collected &&
            bird.x < star.x + star.width &&
            bird.x + bird.width > star.x &&
            bird.y < star.y + star.height &&
            bird.y + bird.height > star.y) {

            star.collected = true;
            gameState.score += star.points;
            updateScore(gameState.score); // Update main score display
            starCollectedThisFrame = true;

            const soundToPlay = star.isBigStar ? sounds.bigStar : sounds.score;
            if (soundToPlay) {
                soundToPlay.currentTime = 0;
                soundToPlay.play().catch(e => console.warn("Star sound play failed:", e));
            }

            // Arcade mode progression for star collection
            if (gameSettings.difficulty === 'arcade' && (gameSettings.mode === 'stars' || gameSettings.mode === 'pipes-and-stars')) {
                 if (gameState.score > 0 && gameState.score % gameState.arcadeMode.scoreThreshold === 0) {
                    if (gameSettings.mode === 'stars') {
                        gameState.pipeSpeed = Math.min(gameState.pipeSpeed + gameState.arcadeMode.speedIncrease, 5); // Max speed 5
                        gameState.starSpawnInterval = Math.max(gameState.starSpawnInterval - gameState.arcadeMode.spawnRateDecrease, 800); // Min interval 800ms
                    } else if (gameSettings.mode === 'pipes-and-stars') {
                        // In combined mode, arcade for pipes is handled by pipe scoring.
                        // This part can make stars appear faster if desired, or add other effects.
                        gameState.starSpawnInterval = Math.max(gameState.starSpawnInterval - gameState.arcadeMode.spawnRateDecreasePipes, 1000);
                    }
                }
            }
        }
    }
    return starCollectedThisFrame;
}


export {
    createStar,
    drawStars,
    checkStarCollisions,
    isStarOverlappingPipe
};