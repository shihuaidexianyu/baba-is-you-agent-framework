#!/usr/bin/env python3
"""
Record Claude Code agent playing Baba Is You levels.

This script records the Claude Code agent playing various environments,
creating GIF recordings for documentation and showcasing.
"""

import sys

import pygame

from agents.claude_code_agent import ClaudeCodeAgent
from baba import create_environment


def record_claude_gameplay(env_name="push_puzzle", output_path=None, verbose=True):
    """Record Claude Code agent playing a specific environment."""

    # Create environment
    env = create_environment(env_name)
    if not env:
        print(f"Unknown environment: {env_name}")
        return

    # Create Claude Code agent (verbose for seeing reasoning)
    agent = ClaudeCodeAgent(verbose=True)

    # Set output path
    if output_path is None:
        output_path = f"docs/gameplay_claude_code_{env_name}.gif"

    print(f"Recording Claude Code agent playing {env_name}...")
    print(f"Output will be saved to: {output_path}")
    print("Note: This requires Claude Code to be installed and configured")
    print()

    # For push_puzzle, use higher step limit
    max_steps = 100 if env_name in ["push_puzzle", "rock_is_push", "rock_push"] else 200

    # Use standard play_episode with appropriate step limit
    stats = agent.play_episode(
        env,
        render=True,
        record=True,
        record_path=output_path,
        cell_size=48,
        fps=4,
        verbose=True,
        max_steps=max_steps,
    )

    if stats["won"]:
        print(f"\n✨ Claude won in {stats['steps']} steps!")
    elif stats["timeout"]:
        print(f"\n⏱️ Timeout after {stats['steps']} steps")
    else:
        print(f"\n❌ Claude lost after {stats['steps']} steps")

    print(f"\nRecording saved to: {output_path}")
    return

    # OLD MANUAL CODE BELOW (keeping for reference but not using)
    if False:  # Disabled
        print("Using manual episode control for complex puzzle...")

        # Initialize pygame for recording
        pygame.init()

        # Reset environment and agent
        obs = env.reset()
        agent.reset()

        # Set up recording
        frames = []
        cell_size = 48
        fps = 4

        # Create window
        window = pygame.display.set_mode((obs.width * cell_size, obs.height * cell_size))
        pygame.display.set_caption(f"Claude Code playing {env_name}")

        clock = pygame.time.Clock()
        done = False
        steps = 0
        max_steps = 100  # Allow up to 100 steps for complex puzzles

        while not done and steps < max_steps:
            # Get action from agent
            action = agent.get_action(obs)

            # Step environment
            obs, reward, done, info = env.step(action)
            steps += 1

            # Debug info
            if verbose and steps % 10 == 0:
                print(
                    f"Step {steps}: Still playing... (YOU objects: {obs.rule_manager.get_you_objects()})"
                )

            # Render and capture frame
            frame = env.render(cell_size=cell_size)
            frames.append(frame)

            # Update display
            surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            window.blit(surf, (0, 0))
            pygame.display.flip()

            # Control frame rate
            clock.tick(fps)

            # Check for pygame quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

        pygame.quit()

        # Save recording
        if frames:
            from baba.rendering import save_gif

            save_gif(frames, output_path, fps=fps)

        # Print results
        if info.get("won"):
            print(f"\n✨ Claude won in {steps} steps!")
        elif info.get("lost"):
            print(f"\n❌ Claude lost after {steps} steps")
        else:
            print(f"\n⏱️ Stopped after {steps} steps (max: {max_steps})")
    else:
        # Use standard play_episode for simpler environments
        stats = agent.play_episode(
            env,
            render=True,
            record=True,
            record_path=output_path,
            cell_size=48,
            fps=4,
            verbose=True,
        )

        if stats["won"]:
            print(f"\n✨ Claude won in {stats['steps']} steps!")
        else:
            print(f"\n❌ Claude didn't win this time (steps: {stats['steps']})")

    print(f"\nRecording saved to: {output_path}")


if __name__ == "__main__":
    # Get environment name from command line or use default
    env_name = sys.argv[1] if len(sys.argv) > 1 else "push_puzzle"

    # Optional: specify output path as second argument
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    record_claude_gameplay(env_name, output_path)
