"use client";

import { useState, useEffect, useRef } from "react";
import { Play, Pause, Square, Activity, Cpu, HardDrive, Wifi, MessageSquare, ShieldAlert, X } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer, Tooltip, YAxis } from "recharts";
import CRTOverlay from "./components/CRTOverlay";
import BootSequence from "./components/BootSequence";
import clsx from "clsx";

// --- Components ---

const TvScreen = ({ title, children, glowColor = "amber" }: { title: string, children: React.ReactNode, glowColor?: "amber" | "green" | "blue" }) => {
  const glowClass = {
    amber: "shadow-[0_0_15px_rgba(255,107,0,0.3)]",
    green: "shadow-[0_0_15px_rgba(0,255,65,0.3)]",
    blue: "shadow-[0_0_15px_rgba(0,243,255,0.3)]",
  }[glowColor];

  return (
    <div className="flex flex-col gap-2 h-full">
      <div className={clsx("tv-screen flex-1 w-full scanlines screen-gloss relative flex flex-col items-center justify-center bg-black", glowClass)}>
        {children}
      </div>
      <div className="text-center font-bold text-sm text-gray-500 uppercase tracking-widest">{title}</div>
    </div>
  );
};

const InterKnotPost = ({ user, msg, date, isAi = false }: { user: string, msg: string, date: string, isAi?: boolean }) => (
  <div className="flex gap-4 p-5 hover:bg-white/5 transition-colors border-b border-gray-800/50">
    {/* Avatar */}
    <div className={clsx(
      "w-10 h-10 rounded-full flex items-center justify-center font-black text-lg shrink-0 border-2",
      isAi ? "bg-[#f3b400] text-black border-white" : "bg-[#333] text-gray-300 border-gray-500"
    )}>
      {isAi ? "J" : "P"}
    </div>

    {/* Content */}
    <div className="flex-1">
      <div className="flex justify-between items-center mb-1">
        <div className="flex items-center gap-2">
          <span className={clsx("font-bold text-base", isAi ? "text-[#f3b400]" : "text-white")}>
            {user}
          </span>
          {isAi && <span className="bg-[#f3b400] text-black text-[10px] px-1.5 py-0.5 rounded font-bold tracking-wider">ADMIN</span>}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-blue-400 font-bold opacity-60">#LOG</span>
          <span className="text-xs text-gray-600 font-mono">{date}</span>
        </div>
      </div>

      <p className="text-gray-300 text-sm leading-relaxed mb-3">{msg}</p>

      {/* Thread Footer UI */}
      <div className="flex gap-4 text-[10px] font-bold text-gray-500 uppercase tracking-wider">
        <span className="cursor-pointer hover:text-[#f3b400] transition-colors">Reply</span>
        <span className="cursor-pointer hover:text-[#f3b400] transition-colors">Like</span>
      </div>
    </div>
  </div>
);

export default function Home() {
  // --- Mock Data ---
  const [data, setData] = useState(Array.from({ length: 20 }, (_, i) => ({ cpu: 40, ram: 50 })));
  const [netSpeed, setNetSpeed] = useState({ up: 0, down: 0 }); // Bytes/sec
  const [threatLevel, setThreatLevel] = useState<"safe" | "critical">("safe");

  const [logs, setLogs] = useState([
    { user: "System", msg: "Core Services initialized successfully.\nConnected to Daemon v1.0.2", date: "Now", isAi: true },
    { user: "Proxy_User", msg: "Run system diagnostics.", date: "1m ago", isAi: false },
  ]);
  const [input, setInput] = useState("");
  const logEndRef = useRef<HTMLDivElement>(null);
  const [booted, setBooted] = useState(false);

  // WebSocket Ref to send messages outside hooks
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // WebSocket Connection
    const ws = new WebSocket("ws://localhost:8888/ws");
    wsRef.current = ws;

    ws.onopen = () => {
      setLogs(prev => [...prev, { user: "System", msg: "Link established with Neural Cloud (WebSocket Connected).", date: "Now", isAi: true }]);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "stats") {
          setData(prev => {
            const next = [...prev, {
              cpu: Math.floor(msg.data.cpu),
              ram: Math.floor(msg.data.ram)
            }];
            if (next.length > 20) next.shift();
            return next;
          });
          setNetSpeed({ up: msg.data.net_sent_speed, down: msg.data.net_recv_speed });
        } else if (msg.type === "log") {
          setLogs(prev => [...prev, { user: msg.user, msg: msg.msg, date: "Now", isAi: msg.isAi }]);
        } else if (msg.type === "threat_alert") {
          setThreatLevel(msg.level);
          // Auto add log
          setLogs(prev => [...prev, { user: "System", msg: `ALERT: ${msg.msg}`, date: "Now", isAi: true }]);
        }
      } catch (e) {
        console.error("Parse Error", e);
      }
    };

    ws.onclose = () => {
      setLogs(prev => [...prev, { user: "System", msg: "Link Lost. Reconnecting...", date: "Now", isAi: true }]);
    };

    return () => ws.close();
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleSend = () => {
    if (!input.trim()) return;

    // UI Update Immediate
    setLogs(prev => [...prev, { user: "Proxy_User", msg: input, date: "Now", isAi: false }]);

    // Send to Backend
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "chat", msg: input }));
    }

    setInput("");
  }

  const sendControl = (mode: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "control", mode: mode }));
      setLogs(prev => [...prev, { user: "System", msg: `Mode Switch: ${mode.toUpperCase()}`, date: "Now", isAi: true }]);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#151515] relative overflow-hidden">
      {!booted && <BootSequence onComplete={() => setBooted(true)} />}
      <CRTOverlay />

      {/* 1. Header (Random Play Storefront Style) */}
      <header className="flex flex-col z-20 shrink-0">
        {/* Yellow Bar */}
        <div className="h-14 bg-[#F3B400] flex items-center justify-between px-6 shadow-md relative z-10">
          <div className="flex items-center gap-3">
            {/* Logo Icon */}
            <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center border-2 border-black">
              <span className="text-[#F3B400] text-lg font-black italic pr-0.5">R</span>
            </div>
            {/* Logo Text */}
            <div className="flex items-baseline -space-x-1">
              <h1 className="text-3xl font-black italic text-black tracking-tighter glitch-text" data-text="JARVIS">JARVIS</h1>
              <span className="text-sm font-bold italic text-black opacity-60 ml-2 pt-1">SYSTEM</span>
            </div>
          </div>

          {/* VCR Controls (Black Container) */}
          <div className="flex bg-[#1a1a1a] p-1 rounded-md gap-1 border border-[#333] shadow-lg">
            <button onClick={() => sendControl("start")} className="w-8 h-6 flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] hover:text-[#00ff41] transition-colors rounded text-gray-500"><Play size={10} fill="currentColor" /></button>
            <button onClick={() => sendControl("pause")} className="w-8 h-6 flex items-center justify-center bg-[#F3B400] text-black hover:bg-white transition-colors rounded shadow-sm"><Pause size={10} fill="currentColor" /></button>
            <button onClick={() => sendControl("stop")} className="w-8 h-6 flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] hover:text-[#ff2a6d] transition-colors rounded text-gray-500"><Square size={8} fill="currentColor" /></button>
          </div>
        </div>

        {/* Sub Bar (Diagonal Stripes) */}
        <div className="h-2 w-full bg-[#111] bg-[linear-gradient(45deg,#111_25%,#1a1a1a_25%,#1a1a1a_50%,#111_50%,#111_75%,#1a1a1a_75%,#1a1a1a_100%)] bg-[length:10px_10px]"></div>
      </header>

      {/* 2. Main Content Area */}
      <div className="flex-1 flex overflow-hidden bg-[#0a0a0a]">

        {/* LEFT: TV Wall (Monitoring) */}
        <div className="flex-1 p-6 flex flex-col gap-6 overflow-y-auto">

          {/* Shelf Title */}
          <div className="flex items-center justify-between border-b-2 border-[#222] pb-1">
            <span className="font-black text-xl text-gray-700 italic tracking-tighter">MONITORING_WALL</span>
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-[#F3B400] rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-[#222] rounded-full"></div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-6">

            {/* TV 1: CPU */}
            <div className="h-48">
              <TvScreen title="CPU_CORE" glowColor="amber">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data}>
                    <defs>
                      <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#ff6b00" /><stop offset="100%" stopColor="transparent" /></linearGradient>
                    </defs>
                    <YAxis domain={[0, 100]} hide />
                    <Area type="step" dataKey="cpu" stroke="#ff6b00" strokeWidth={3} fill="url(#cpuGrad)" isAnimationActive={false} />
                  </AreaChart>
                </ResponsiveContainer>
                <div className="absolute top-2 left-2 font-mono text-xs text-[#ff6b00] font-bold">LOAD: {data[data.length - 1].cpu}%</div>
              </TvScreen>
            </div>

            {/* TV 2: RAM */}
            <div className="h-48">
              <TvScreen title="MEMORY_MOD" glowColor="green">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data}>
                    <defs>
                      <linearGradient id="ramGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#00ff41" /><stop offset="100%" stopColor="transparent" /></linearGradient>
                    </defs>
                    <YAxis domain={[0, 100]} hide />
                    <Area type="monotone" dataKey="ram" stroke="#00ff41" strokeWidth={3} fill="url(#ramGrad)" isAnimationActive={false} />
                  </AreaChart>
                </ResponsiveContainer>
                <div className="absolute top-2 right-2 font-mono text-xs text-[#00ff41] font-bold">USE: {data[data.length - 1].ram}%</div>
              </TvScreen>
            </div>

            {/* TV 3: Threats */}
            <div className="h-48">
              <TvScreen title="THREAT_SCOPE">
                <div className="flex flex-col items-center gap-2 text-center">
                  {threatLevel === "safe" ? (
                    <>
                      <ShieldAlert size={48} className="text-gray-600 opacity-50" />
                      <span className="font-mono text-gray-500 font-bold bg-gray-900/30 px-2 py-1 rounded text-xs">NO THREATS DETECTED</span>
                    </>
                  ) : (
                    <>
                      <ShieldAlert size={48} className="text-red-500 animate-ping" />
                      <span className="font-mono text-red-500 font-black bg-red-900/50 px-2 py-1 rounded animate-pulse border border-red-500">WARNING: INTRUSION</span>
                    </>
                  )}
                </div>
              </TvScreen>
            </div>

            {/* TV 4: Network */}
            <div className="h-48">
              <TvScreen title="NET_LINK" glowColor="blue">
                <div className="w-full h-full flex items-center justify-center gap-4 relative">
                  <Wifi size={40} className="text-blue-400" />
                  <div className="flex flex-col font-mono text-blue-300 text-xs">
                    {/* Convert Bytes to KB/MB */}
                    <span>UP: {(netSpeed.up / 1024).toFixed(1)} KB/s</span>
                    <span>DN: {(netSpeed.down / 1024 / 1024).toFixed(2)} MB/s</span>
                    <span>Status: ONLINE</span>
                  </div>
                  <div className="absolute bottom-0 w-full h-1 bg-blue-500 animate-[pulse_0.5s_infinite]"></div>
                </div>
              </TvScreen>
            </div>

          </div>
        </div>
        {/* RIGHT: Inter-knot Chat (Sliding Panel Style) */}

        <div className="w-[400px] bg-[#0F0F0F] border-l border-[#222] flex flex-col shadow-2xl relative">

          {/* Panel Header */}
          <div className="p-4 flex items-center justify-between border-b border-[#222] bg-[linear-gradient(45deg,#0F0F0F_25%,#111_25%,#111_50%,#0F0F0F_50%,#0F0F0F_75%,#111_75%,#111_100%)] bg-[length:4px_4px]">
            <div>
              <h2 className="text-white font-black text-lg tracking-tight">INTER-KNOT</h2>
              <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">Secure_Channel: #SYS_ADMIN</div>
            </div>
            <X className="text-gray-600 cursor-pointer hover:text-white w-5 h-5" />
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto bg-[#0a0a0a] scrollbar-thin scrollbar-thumb-[#333] scrollbar-track-transparent">
            {logs.map((log, i) => (
              <InterKnotPost key={i} {...log} />
            ))}
            <div ref={logEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 bg-[#0F0F0F] border-t border-[#222]">
            <div className="relative group">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                className="w-full bg-black border border-[#333] text-gray-200 p-3 pr-10 rounded text-sm focus:border-[#F3B400] focus:outline-none transition-colors placeholder:text-gray-700"
                placeholder="Write a command..."
              />
              <button
                onClick={handleSend}
                className="absolute right-2 top-1.5 p-1.5 bg-[#F3B400] rounded-sm text-black hover:bg-white transition-colors"
              >
                <MessageSquare size={14} fill="currentColor" strokeWidth={2.5} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
