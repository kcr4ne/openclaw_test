import React from 'react';

const CRTOverlay = () => {
    return (
        <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden h-full w-full">
            {/* Scanlines */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,6px_100%] animate-scanline" />

            {/* Vignette */}
            <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(0,0,0,0)_60%,rgba(0,0,0,0.4)_100%)]" />

            {/* Screen Flicker (Subtle) */}
            <div className="absolute inset-0 bg-white opacity-[0.02] animate-flicker pointer-events-none mix-blend-overlay" />
        </div>
    );
};

export default CRTOverlay;
