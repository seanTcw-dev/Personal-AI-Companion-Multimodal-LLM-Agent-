/**
 * Lip Sync Service
 * Uses Web Audio API AnalyserNode to extract volume from audio playback
 * and dispatch events for VRM character mouth animation.
 */

class LipSyncService {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.animationFrameId = null;
        this.isAnalysing = false;
        this.smoothedVolume = 0;

        // Track which audio elements have already been connected
        // (calling createMediaElementSource twice on the same element throws an error)
        this._connectedElements = new WeakSet();
    }

    /**
     * Lazily initialise the AudioContext and AnalyserNode.
     * Must be called from a user-gesture context the first time (browser policy).
     */
    _ensureContext() {
        if (this.audioContext) return;

        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256; // 128 frequency bins — enough for speech
        this.analyser.smoothingTimeConstant = 0.6; // hardware-level smoothing

        // Connect analyser → destination so we still hear the audio
        this.analyser.connect(this.audioContext.destination);

        this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

        console.log('🎤 LipSync: AudioContext + AnalyserNode initialised');
    }

    /**
     * Connect an HTMLAudioElement to the analyser graph.
     * Call this BEFORE audio.play().
     *
     * @param {HTMLAudioElement} audioElement
     */
    connectAudio(audioElement) {
        this._ensureContext();

        // Resume context if suspended (autoplay policy)
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        // Only create source once per element
        if (!this._connectedElements.has(audioElement)) {
            const source = this.audioContext.createMediaElementSource(audioElement);
            source.connect(this.analyser);
            // NOTE: we do NOT connect source → destination directly because
            // the chain is source → analyser → destination (set up in _ensureContext)
            this._connectedElements.add(audioElement);
            console.log('🎤 LipSync: Audio element connected to analyser');
        }

        // Start the analysis loop
        this._startAnalysis();

        // Stop analysis when audio ends or pauses
        const stopHandler = () => {
            this._stopAnalysis();
            audioElement.removeEventListener('ended', stopHandler);
            audioElement.removeEventListener('pause', stopHandler);
        };
        audioElement.addEventListener('ended', stopHandler);
        audioElement.addEventListener('pause', stopHandler);
    }

    /**
     * Start the requestAnimationFrame loop that reads frequency data
     * and dispatches volume events.
     */
    _startAnalysis() {
        if (this.isAnalysing) return;
        this.isAnalysing = true;

        const analyse = () => {
            if (!this.isAnalysing) return;

            this.analyser.getByteFrequencyData(this.dataArray);

            // Focus on speech frequencies (~85 – 4000 Hz)
            // With sampleRate=48000 and fftSize=256, each bin ≈ 187.5 Hz
            // Bins 0–21 cover roughly 0–4000 Hz
            const speechBins = this.dataArray.slice(0, 22);
            const sum = speechBins.reduce((a, b) => a + b, 0);
            const avg = sum / speechBins.length; // 0-255 range
            const rawVolume = Math.min(avg / 128, 1.0); // normalise to 0-1

            // Smooth with lerp to prevent jitter
            const lerpFactor = rawVolume > this.smoothedVolume ? 0.4 : 0.15; // open fast, close slow
            this.smoothedVolume += (rawVolume - this.smoothedVolume) * lerpFactor;

            // Dispatch event
            window.dispatchEvent(new CustomEvent('lipsync:volume', {
                detail: { volume: this.smoothedVolume }
            }));

            this.animationFrameId = requestAnimationFrame(analyse);
        };

        this.animationFrameId = requestAnimationFrame(analyse);
    }

    /**
     * Stop the analysis loop and dispatch a final volume=0 to close the mouth.
     */
    _stopAnalysis() {
        this.isAnalysing = false;

        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }

        // Smoothly close mouth by dispatching 0
        this.smoothedVolume = 0;
        window.dispatchEvent(new CustomEvent('lipsync:volume', {
            detail: { volume: 0 }
        }));

        console.log('🎤 LipSync: Analysis stopped, mouth closed');
    }
}

// Singleton
export const lipSyncService = new LipSyncService();
