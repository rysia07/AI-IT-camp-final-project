from audio_adapter import AudioAdapter
import pygame
import time

# Initialize
adapter = AudioAdapter()

# Load your WAV file - replace with your actual file path
try:
    adapter.load("path/to/your/file.wav")  # ← Change this to your WAV file
    print("✓ Audio loaded successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    exit()

# Test basic playback
print("Playing audio...")
adapter.play()

# Keep it running for the duration
time.sleep(5)  # Play for 5 seconds

# Test pause/unpause
print("Pausing...")
adapter.pause()
time.sleep(2)

print("Resuming...")
adapter.unpause()
time.sleep(3)

# Test fade out
print("Fading out...")
adapter.fade_out(2000)  # Fade out over 2 seconds

# Update fade effect
for _ in range(100):
    adapter.update()
    time.sleep(0.02)

adapter.quit()
print("✓ Done!")