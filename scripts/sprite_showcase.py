#!/usr/bin/env python3
"""Showcase all the fun sprites in Baba Is You."""

import cv2
import numpy as np

from baba.sprites import create_object_sprite, create_text_sprite


def create_showcase_image():
    """Create an image showcasing all sprites."""
    # Define objects and their colors
    objects = [
        ("baba", (255, 255, 255), "Baba"),
        ("wall", (139, 69, 19), "Wall"),
        ("rock", (169, 169, 169), "Rock"),
        ("flag", (255, 215, 0), "Flag"),
        ("water", (64, 164, 223), "Water"),
        ("key", (255, 215, 0), "Key"),
        ("door", (139, 69, 19), "Door"),
        ("heart", (255, 105, 180), "Heart"),
        ("star", (255, 255, 0), "Star"),
        ("skull", (255, 0, 0), "Skull"),
        ("box", (205, 133, 63), "Box"),
        ("tree", (34, 139, 34), "Tree"),
    ]

    # Define text objects and their colors
    texts = [
        ("BABA", (255, 182, 193)),
        ("IS", (255, 255, 255)),
        ("YOU", (255, 192, 203)),
        ("WIN", (255, 215, 0)),
        ("STOP", (220, 20, 60)),
        ("PUSH", (144, 238, 144)),
        ("WALL", (210, 180, 140)),
        ("ROCK", (192, 192, 192)),
        ("FLAG", (255, 255, 102)),
        ("WATER", (135, 206, 235)),
        ("SINK", (138, 43, 226)),
    ]

    # Settings
    sprite_size = 48
    padding = 10
    label_height = 20

    # Calculate grid dimensions
    items_per_row = 6
    object_rows = (len(objects) + items_per_row - 1) // items_per_row
    text_rows = (len(texts) + items_per_row - 1) // items_per_row

    # Calculate image size
    img_width = items_per_row * (sprite_size + padding) + padding
    img_height = (object_rows + text_rows + 2) * (sprite_size + label_height + padding) + 200

    # Create canvas
    canvas = np.full((img_height, img_width, 3), (40, 40, 40), dtype=np.uint8)

    # Add title
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "Baba Is You - Sprite Showcase", (20, 40), font, 1.2, (255, 255, 255), 2)

    # Draw objects
    cv2.putText(canvas, "Game Objects:", (20, 80), font, 0.8, (200, 200, 200), 1)

    y_offset = 100
    for i, (obj_name, color, label) in enumerate(objects):
        row = i // items_per_row
        col = i % items_per_row

        x = col * (sprite_size + padding) + padding
        y = y_offset + row * (sprite_size + label_height + padding)

        # Create and place sprite
        sprite = create_object_sprite(obj_name, color, (sprite_size, sprite_size))
        canvas[y : y + sprite_size, x : x + sprite_size] = sprite

        # Add label
        text_size = cv2.getTextSize(label, font, 0.4, 1)[0]
        text_x = x + (sprite_size - text_size[0]) // 2
        text_y = y + sprite_size + 15
        cv2.putText(canvas, label, (text_x, text_y), font, 0.4, (200, 200, 200), 1)

    # Draw text objects
    y_offset += (object_rows + 1) * (sprite_size + label_height + padding)
    cv2.putText(canvas, "Text Objects:", (20, y_offset - 20), font, 0.8, (200, 200, 200), 1)

    for i, (text, color) in enumerate(texts):
        row = i // items_per_row
        col = i % items_per_row

        x = col * (sprite_size + padding) + padding
        y = y_offset + row * (sprite_size + label_height + padding)

        # Create and place text sprite
        sprite = create_text_sprite(text, color, (sprite_size, sprite_size))
        canvas[y : y + sprite_size, x : x + sprite_size] = sprite

        # Add label
        text_size = cv2.getTextSize(text, font, 0.4, 1)[0]
        text_x = x + (sprite_size - text_size[0]) // 2
        text_y = y + sprite_size + 15
        cv2.putText(canvas, text, (text_x, text_y), font, 0.4, (200, 200, 200), 1)

    return canvas


def main():
    """Create and display sprite showcase."""
    print("Creating sprite showcase...")

    # Create showcase image
    showcase = create_showcase_image()

    # Convert from RGB to BGR for OpenCV
    showcase_bgr = cv2.cvtColor(showcase, cv2.COLOR_RGB2BGR)

    # Save the image
    output_path = "baba_sprites_showcase.png"
    cv2.imwrite(output_path, showcase_bgr)
    print(f"Sprite showcase saved to: {output_path}")

    # Display the image
    cv2.imshow("Baba Is You - Sprite Showcase", showcase_bgr)
    print("Press any key to close the window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
