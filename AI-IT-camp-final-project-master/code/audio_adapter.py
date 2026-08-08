import pygame
import os
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class AudioState(Enum):
    """Enumeration for audio playback states."""
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2

@dataclass
class FadeConfig:
    """Configuration for fade effects."""
    duration: int  # Duration in milliseconds
    target_volume: float  # Target volume (0.0 to 1.0)
    start_volume: float = None  # Starting volume (auto-calculated if None)


class AudioAdapter:
    """
    A pygame-based audio adapter supporting FLAC, MP3, and WAV files.
    Provides volume control, fade effects, and full playback management.
    """

    SUPPORTED_FORMATS = {'.flac', '.mp3', '.wav', '.ogg'}

    def __init__(self, frequency: int = 44100, size: int = -16, channels: int = 2, 
                 buffer: int = 512):
        """
        Initialize the audio adapter.

        Args:
            frequency: Sample rate in Hz (default 44100)
            size: Sample width (-16 for 16-bit signed, default)
            channels: Number of audio channels (default 2 for stereo)
            buffer: Buffer size in samples (default 512)
        """
        pygame.mixer.init(frequency=frequency, size=size, channels=channels, 
                         buffer=buffer)
        self.current_sound: Optional[pygame.mixer.Sound] = None
        self.current_channel: Optional[pygame.mixer.Channel] = None
        self.state = AudioState.STOPPED
        self.current_file = None
        self.current_volume = 1.0
        self.fade_config: Optional[FadeConfig] = None
        self.fade_start_time = 0
        self.on_end_callback: Optional[Callable] = None

    def load(self, file_path: str) -> bool:
        """
        Load an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {ext}. Supported: {self.SUPPORTED_FORMATS}")

        try:
            self.current_sound = pygame.mixer.Sound(file_path)
            self.current_file = file_path
            self.state = AudioState.STOPPED
            self.current_volume = 1.0
            self.fade_config = None
            return True
        except pygame.error as e:
            raise RuntimeError(f"Failed to load audio file: {e}")

    def play(self, loops: int = 0) -> None:
        """
        Play the loaded audio file.

        Args:
            loops: Number of loops (-1 for infinite)
        """
        if not self.current_sound:
            raise RuntimeError("No audio file loaded. Call load() first.")

        if self.state == AudioState.PAUSED:
            self.current_channel.unpause()
        else:
            self.current_channel = self.current_sound.play(loops=loops)
            self.current_channel.set_volume(self.current_volume)

        self.state = AudioState.PLAYING
        self.fade_config = None

    def pause(self) -> None:
        """Pause the current audio playback."""
        if self.state == AudioState.PLAYING and self.current_channel:
            self.current_channel.pause()
            self.state = AudioState.PAUSED

    def unpause(self) -> None:
        """Resume paused audio playback."""
        if self.state == AudioState.PAUSED and self.current_channel:
            self.current_channel.unpause()
            self.state = AudioState.PLAYING

    def stop(self) -> None:
        """Stop the current audio playback."""
        if self.current_channel:
            self.current_channel.stop()
        self.state = AudioState.STOPPED
        self.fade_config = None

    def set_volume(self, volume: float) -> None:
        """
        Set the playback volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        self.current_volume = volume
        if self.current_channel:
            self.current_channel.set_volume(volume)

    def get_volume(self) -> float:
        """Get the current volume level."""
        return self.current_volume

    def fade_in(self, duration: int) -> None:
        """
        Fade in the audio from silent to current volume.

        Args:
            duration: Duration of fade in milliseconds
        """
        if not self.current_sound:
            raise RuntimeError("No audio file loaded.")

        self.current_channel = self.current_sound.play(loops=-1)
        self.fade_config = FadeConfig(
            duration=duration,
            target_volume=self.current_volume,
            start_volume=0.0
        )
        self.current_channel.set_volume(0.0)
        self.state = AudioState.PLAYING
        self.fade_start_time = pygame.time.get_ticks()

    def fade_out(self, duration: int) -> None:
        """
        Fade out the audio to silence.

        Args:
            duration: Duration of fade out in milliseconds
        """
        if self.state != AudioState.PLAYING or not self.current_channel:
            raise RuntimeError("No audio currently playing.")

        self.fade_config = FadeConfig(
            duration=duration,
            target_volume=0.0,
            start_volume=self.current_volume
        )
        self.fade_start_time = pygame.time.get_ticks()

    def update(self) -> None:
        """
        Update fade effects. Call this in your game loop.
        Must be called regularly for fade effects to work.
        """
        if not self.fade_config or not self.current_channel:
            if self.state == AudioState.PLAYING and self.current_channel:
                if not self.current_channel.get_busy():
                    self.state = AudioState.STOPPED
                    if self.on_end_callback:
                        self.on_end_callback()
            return

        elapsed = pygame.time.get_ticks() - self.fade_start_time
        progress = min(elapsed / self.fade_config.duration, 1.0)

        if self.fade_config.start_volume is not None:
            volume_range = self.fade_config.target_volume - self.fade_config.start_volume
            current_volume = self.fade_config.start_volume + (volume_range * progress)
        else:
            current_volume = self.fade_config.target_volume

        self.current_channel.set_volume(max(0.0, min(1.0, current_volume)))

        if progress >= 1.0:
            target_vol = self.fade_config.target_volume
            self.current_volume = target_vol
            self.fade_config = None

            if target_vol == 0.0:
                self.stop()

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self.state == AudioState.PLAYING

    def is_paused(self) -> bool:
        """Check if audio is currently paused."""
        return self.state == AudioState.PAUSED

    def get_state(self) -> AudioState:
        """Get the current playback state."""
        return self.state

    def get_loaded_file(self) -> Optional[str]:
        """Get the path of the currently loaded file."""
        return self.current_file

    def set_on_end_callback(self, callback: Callable) -> None:
        """
        Set a callback function to be called when audio playback ends.

        Args:
            callback: Function to call when playback ends
        """
        self.on_end_callback = callback

    def get_busy(self) -> bool:
        """Check if a channel is actively playing sound."""
        return self.current_channel is not None and self.current_channel.get_busy()

    def quit(self) -> None:
        """Clean up and stop the mixer."""
        if self.current_channel:
            self.current_channel.stop()
        pygame.mixer.quit()


class AudioManager:
    """
    Manages multiple audio channels for playing different sounds simultaneously.
    """

    def __init__(self, max_channels: int = 8):
        """
        Initialize the audio manager.

        Args:
            max_channels: Maximum number of simultaneous audio channels
        """
        pygame.mixer.init()
        pygame.mixer.set_num_channels(max_channels)
        self.adapters = {}
        self.max_channels = max_channels

    def create_adapter(self, adapter_id: str) -> AudioAdapter:
        """
        Create a new audio adapter.

        Args:
            adapter_id: Unique identifier for the adapter

        Returns:
            The created AudioAdapter instance
        """
        if adapter_id in self.adapters:
            raise ValueError(f"Adapter '{adapter_id}' already exists.")

        adapter = AudioAdapter()
        self.adapters[adapter_id] = adapter
        return adapter

    def get_adapter(self, adapter_id: str) -> Optional[AudioAdapter]:
        """Get an adapter by ID."""
        return self.adapters.get(adapter_id)

    def remove_adapter(self, adapter_id: str) -> None:
        """Remove and stop an adapter."""
        if adapter_id in self.adapters:
            adapter = self.adapters[adapter_id]
            adapter.stop()
            del self.adapters[adapter_id]

    def update_all(self) -> None:
        """Update all adapters (call in game loop for fade effects)."""
        for adapter in self.adapters.values():
            adapter.update()

    def stop_all(self) -> None:
        """Stop all adapters."""
        for adapter in self.adapters.values():
            adapter.stop()

    def pause_all(self) -> None:
        """Pause all adapters."""
        for adapter in self.adapters.values():
            if adapter.is_playing():
                adapter.pause()

    def unpause_all(self) -> None:
        """Resume all adapters."""
        for adapter in self.adapters.values():
            if adapter.is_paused():
                adapter.unpause()

    def quit(self) -> None:
        """Clean up all adapters."""
        self.stop_all()
        for adapter in self.adapters.values():
            adapter.quit()
        pygame.mixer.quit()
