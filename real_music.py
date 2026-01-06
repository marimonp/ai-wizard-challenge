import os
import json
import scipy.io.wavfile
import numpy as np
from datetime import datetime
from transformers import pipeline

# TECHNICAL NOTE: 
# This script executes REAL AI inference using Meta's MusicGen Small model.
# On CPU-only environments, generation takes approximately 2-3 minutes per track.

class CloudWalkMusicWizard:
    def __init__(self):
        self.company_name = "Nimbus Music Gen (Real AI Mode)"
        self.ledger_file = "billing_ledger.json"
        self.playlist_file = "cloudwalk_playlist.m3u"
        
        print("⏳ Initializing AI Model (MusicGen)...")
        # Loads the model pipeline into memory
        self.synthesizer = pipeline("text-to-audio", "facebook/musicgen-small")

    def music_agent(self, mood_prompt):
        print(f"\n🎵 [Music Agent]: Composing track for prompt: '{mood_prompt}'...")
        print("   (Processing on CPU... please wait ~2 mins)...")
        
        try:
            # 1. INFERENCE
            # Uses forward_params to encapsulate generation arguments safely
            # max_new_tokens=256 generates approx. 5 seconds of audio to prevent timeouts
            music = self.synthesizer(mood_prompt, forward_params={"max_new_tokens": 256})
            
            # 2. AUDIO PROCESSING
            # Extract audio array from the output dictionary
            audio_data = music["audio"]
            
            # Ensure data is a Numpy array (converts if it's a PyTorch Tensor)
            if hasattr(audio_data, 'numpy'):
                audio_data = audio_data.numpy()
            
            # Flatten to 1D array if necessary to avoid shape errors
            if len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            sampling_rate = music["sampling_rate"]
            
            # Normalize audio volume to avoid clipping
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # 3. SAVE FILE
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"track_{timestamp}.wav"
            
            scipy.io.wavfile.write(filename, sampling_rate, audio_data)
                
            print(f"✅ SUCCESS! Real audio generated: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Generation Error: {e}")
            return "error_track.wav"

    def billing_agent(self, user):
        print(f"💳 [Billing Agent]: Processing subscription for {user}...")
        bill_data = {
            "user": user, 
            "amount": "1.00", 
            "currency": "USD", 
            "status": "paid", 
            "date": str(datetime.now())
        }
        with open(self.ledger_file, "a") as f:
            f.write(json.dumps(bill_data) + "\n")

    def marketing_agent(self, track_name, mood):
        if "error" in track_name:
            print("📱 [Marketing Agent]: Waiting for valid audio file...")
        else:
            post = f"✨ New AI Drop! Generated '{mood}'. Listen now: {track_name} #CloudWalk #AIWizard"
            print(f"📱 [Marketing Agent]: Generated Post: {post}")

    def playlist_builder(self):
        print("\n🎧 [Bonus Feature]: Building Playlist...")
        
        # IMPROVEMENT: Filter checks not just extension, but if file actually has content size
        tracks = []
        for f in os.listdir('.'):
            if f.endswith('.wav') and 'error' not in f:
                # Check file size to ensure it's a real audio file (> 1KB)
                if os.path.getsize(f) > 1024:
                    tracks.append(f)
        
        tracks.sort()
        
        with open(self.playlist_file, "w") as f:
            f.write("#EXTM3U\n")
            for track in tracks:
                # Calculates duration (simulated metadata) or sets default
                f.write(f"#EXTINF:-1,CloudWalk AI - {track}\n{track}\n")
                
        print(f"✅ Playlist '{self.playlist_file}' updated with {len(tracks)} verified audio tracks.")

# --- EXECUTION ---
if __name__ == "__main__":
    wizard = CloudWalkMusicWizard()

    print(f"--- Starting {wizard.company_name} ---\n")

    # Single execution scenario to demonstrate functionality without overloading CPU
    user = "user_001"
    prompt = "lo-fi hip hop beat with piano"

    wizard.billing_agent(user) 
    track = wizard.music_agent(prompt)
    wizard.marketing_agent(track, prompt)

    wizard.playlist_builder()