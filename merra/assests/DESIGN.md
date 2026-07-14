python?code_reference&code_event_index=6
markdown_content = """# Terminal UI Layout & Styling Design Guide
## Project: TikTok Hook - Merra (Colorcode)

This document contains a comprehensive guide for the layout, typography (font styling), and color scheme implementation for a Terminal User Interface (TUI). This project is designed as a TikTok content hook that blends the vibrant *pixel art* / *ASCII art* visualization of the **"Colorcode"** album cover by **Merra** with real-time lyrics ("Pain That I Buried Inside").

---

## 1. Core Concept & Visual Aesthetics
The main goal of this project is to create a contrasting yet harmonious visual between the **retro aesthetics of a computer terminal (CLI/TUI)** and the **vibrant colors of the album cover**.

The album cover features key elements:
- Bold title text: **"COLORCODE"**
- A swirling red-and-black portal.
- A man in a green checkered shirt and a gray cat facing the portal.
- Complementary elements: Dice, fire, an hourglass, and plants with orange flowers.

These visuals will be converted into colored *ASCII/Pixel Art* using ANSI codes or Rich Text, then combined with the 10 lyric layout variations below.

---

## 2. 10 Layout & Lyric Typography Variations

Here are 10 terminal UI layout designs that can be randomized or selected for TikTok video transition needs:

### Layout 1: Split Screen (Classic Left-Right)
- **Description:** The screen is divided into two balanced main columns.
- **Left Side:** Full *ASCII Art* of the album cover (including the portal and characters).
- **Right Side:** Vertical lyric panel. The currently active lyric uses a Bold font with a *Neon Cyan* color, while the previous/next lyrics are given a *dimmed* effect.
- **Best for:** The *verse* parts of the song with a steady tempo.

### Layout 2: Background Watermark / Transparent Overlay
- **Description:** The album cover is rendered with low saturation/brightness (20-30% opacity/dimmed) as the full terminal background.
- **Center Screen:** Very large lyric text scrolls from bottom to top (*scrolling mode*).
- **Font Styling:** Thick block-style fonts (ANSI Block Characters) in neon white or bright red to contrast with the background.
- **Best for:** The intro or slow transition parts.

### Layout 3: Tiling Border Windows (Floating Grid)
- **Description:** Uses classic terminal *borders* to separate each element.
- **Components:**
  - Box 1 (Top Left): Focuses on the album title "COLORCODE".
  - Box 2 (Bottom Left): Focuses on the swirling portal and the cat.
  - Box 3 (Right): Main lyric box with a *progress bar* indicator below it.
- **Best for:** A highly structured retro terminal aesthetic.

### Layout 4: Audio Reactive Circular Portal
- **Description:** A layout centered around the red swirling portal. The portal's *ASCII Art* element is in the center.
- **Lyric Typography:** Lyrics are not displayed straight; instead, they curve or follow the edges of the circular portal. The font size of the lyrics dynamically scales up and down following the *bass* hits (*audio reactive*).
- **Best for:** The *Drop* or *Climax* parts of the song as the *main hook* for TikTok.

### Layout 5: Focus Mode (Character & Pet Detailing)
- **Description:** The *ASCII* visual is *zoomed in*, focusing only on rendering the details of the man in the green checkered shirt and the gray cat in the bottom left corner of the screen.
- **Right/Top Side:** Song lyrics are displayed line-by-line with a fast *typewriter effect*.
- **Best for:** Emotional or *storytelling* lyric sections.

### Layout 6: Matrix Waterfall Lyrics
- **Description:** Draws inspiration from the falling code rain effect in *The Matrix* movies.
- **Visuals:** Song lyrics flow falling from top to bottom on the right side of the terminal with a green-to-white color gradient. On the left side, the *ASCII Art* of the blazing fire and dice is rendered in contrasting bright orange.
- **Best for:** Fast song tempos or intense transition parts.

### Layout 7: Minimalist Command Line Interface (CLI)
- **Description:** A very clean interface simulating a real computer command line.
- **Visuals:** In the top right corner, there is a small hourglass icon in ASCII. At the bottom of the screen, song lyrics appear after a terminal *prompt* (e.g., `user@colorcode:~ $ current_lyrics --play`).
- **Font Styling:** Pure monospaced fonts (like Courier or JetBrains Mono) without heavy decoration.

### Layout 8: Cinematic Subtitle Block
- **Description:** A horizontal layout similar to a cinematic movie player.
- **Visuals:** The top 75% of the screen is filled by a widened *Pixel Art* album cover (landscape mode). The bottom 25% area is a solid black block specifically for displaying lyrics with an extra-large and bold font size (like *Impact ASCII* or *Double-stroke font*).
- **Best for:** Landscape format TikTok videos rotated 90 degrees or center-cropped.

### Layout 9: Creative Code Syntax Highlighting
- **Description:** Lyrics are formatted to look like lines of programming code (e.g., Python or Rust).
- **Example:**
python
if pain_inside == True:
print("[Bold Neon-Red] Pain That I Buried Inside")

- **Visuals:** The album cover is embedded inside a multi-line comment block with highly aesthetic *syntax highlighting*.

### Layout 10: Kinetic Typography Explosion
- **Description:** Full focus on the dynamic words of the lyrics appearing randomly.
- **Visuals:** Every sung word of the lyric will instantly appear at random terminal coordinates using different giant ASCII fonts. Album cover elements (like the dice or fire) will flash briefly as particle effects when a new word appears.
- **Best for:** Grabbing the TikTok audience's attention in the first 3 seconds (*ultimate hook*).

---

## 3. Font Styling & Color Palette Guide

To ensure the terminal display looks modern and sharp on TikTok videos, use the following combinations:

### A. Terminal Font Recommendations (Monospaced)
1. **Fira Code / JetBrains Mono:** Very clean, excellent *ligatures*, perfect for sharp text displays.
2. **Comic Mono:** Gives a slightly casual and retro-comic vibe, matching the original cover illustration style perfectly.
3. **ANSI Shadow / ANSI 3D (Figlet Fonts):** For rendering main lyric keywords into large ASCII text.

### B. ANSI/TrueColor Palette (Hex Codes)
Match the terminal coloring with the original image colors using 24-bit color codes (TrueColor):
- 🟥 **Swirling Portal & Fire:** `#E63946` (Bright Red) & `#F4A261` (Fire Orange)
- 🟩 **Man's Shirt & Leaves:** `#2A9D8F` (Dark Teal / Checkered)
- 🟨 **Floor & Wall Background:** `#E9C46A` (Muted Pastel Yellow)
- 🟪 **Dice Borders & Hourglass:** `#8187B5` (Muted / Desaturated Purple)
- ⬛ **Shadows & Contrast:** `#1D3557` (Dark Blue / Terminal Black)

---

## 4. Recommended Tech Stack for Implementation

If you want to realize this *layouting* into an actual program, here are highly recommended *libraries*:

- **Python:** Use the **`rich`** library (extremely easy for text coloring, panel layouting, and live display) or **`Textual`** (if you want to build a full interactive TUI app). For image-to-color-ASCII conversion, use **`ascii-magic`**.
- **JavaScript/Node.js:** Use **`Ink`** (to build TUIs using React-based components) or **`blessed`**.
- **Lyric Synchronization:** Use the `.lrc` file format (contains minutes:seconds:milliseconds timestamps) and pair it with a *timer* in your program so the lyric text changes automatically and accurately in sync with the Merra - Colorcode audio.
"""

with open("DESIGN.md", "w", encoding="utf-8") as f:
  f.write(markdown_content)

print("File DESIGN.md successfully created in English. [file-tag: code-generated-file-DESIGN.md]")