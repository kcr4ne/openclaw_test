import React, { useEffect, useState } from 'react';
import clsx from 'clsx';

const BootSequence = ({ onComplete }: { onComplete: () => void }) => {
    const [logs, setLogs] = useState<string[]>([]);
    const [showLogo, setShowLogo] = useState(false);
    const [fadeOut, setFadeOut] = useState(false);

    useEffect(() => {
        const bootLogs = [
            "INITIALIZING NEURAL LINK...",
            "LOADING KERNEL MODULES (v5.15.0-91-generic)...",
            "MOUNTING FILESYSTEMS... [OK]",
            "STARTING DAEMONS... [OK]",
            "ESTABLISHING SECURE CONNECTION...",
            "VERIFYING PERMISSIONS [ROOT]... DETECTED",
            "LOADING INTERFACE DRIVERS...",
        ];

        let delay = 0;
        bootLogs.forEach((log, i) => {
            delay += Math.random() * 300 + 100;
            setTimeout(() => {
                setLogs(prev => [...prev, log]);
            }, delay);
        });

        // Logo Reveal
        setTimeout(() => setShowLogo(true), 2500);

        // Complete
        setTimeout(() => setFadeOut(true), 4000);
        setTimeout(onComplete, 4500);

    }, [onComplete]);

    if (fadeOut) return null; // Or keep it in DOM but transparent for exit transition

    return (
        <div className={clsx(
            "fixed inset-0 z-40 bg-black flex flex-col items-center justify-center font-mono transition-opacity duration-500",
            fadeOut ? "opacity-0" : "opacity-100"
        )}>
            {/* Background Noise/Grid */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(20,20,20,1)_1px,transparent_1px),linear-gradient(90deg,rgba(20,20,20,1)_1px,transparent_1px)] bg-[length:20px_20px] opacity-20 pointer-events-none"></div>

            {/* Center Content */}
            <div className="z-10 flex flex-col items-center gap-8">

                {/* LOGO */}
                <div className={clsx(
                    "transition-all duration-1000 transform",
                    showLogo ? "scale-100 opacity-100 blur-0" : "scale-125 opacity-0 blur-xl"
                )}>
                    <div className="w-24 h-24 bg-[#F3B400] rounded-full flex items-center justify-center border-4 border-white shadow-[0_0_50px_#F3B400]">
                        <span className="text-black font-black text-5xl italic">R</span>
                    </div>
                </div>

                {/* Title */}
                <div className={clsx(
                    "text-center transition-opacity duration-1000 delay-300",
                    showLogo ? "opacity-100" : "opacity-0"
                )}>
                    <h1 className="text-4xl font-black italic tracking-tighter text-white mb-2">JARVIS <span className="text-[#F3B400]">SYSTEM</span></h1>
                    <div className="h-1 w-full bg-[#F3B400] animate-[pulse_0.2s_infinite]"></div>
                </div>

                {/* Logs */}
                <div className="w-96 text-xs text-gray-500 font-bold h-32 overflow-hidden flex flex-col justify-end">
                    {logs.map((log, i) => (
                        <div key={i} className="whitespace-nowrap">&gt; {log}</div>
                    ))}
                    <div className="animate-pulse">&gt; _</div>
                </div>

            </div>
        </div>
    );
};

export default BootSequence;
