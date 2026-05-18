import React, { useState } from "react";
import { Menu, Search, Shield, Brain, MessageSquare, Heart, Send, ChevronDown } from "lucide-react";

export default function PersonaWeave() {
  const [activeTab, setActiveTab] = useState("Settings");
  const [activePersona, setActivePersona] = useState("Persona 1");
  const [activeRole, setActiveRole] = useState("Defense Analyst");
  const [message, setMessage] = useState("");

  const roles = [
    {
      name: "Defense Analyst",
      description: "Defense systems, threat intelligence, strategic analysis.",
      icon: Shield,
      status: "active",
    },
    {
      name: "Behavior Researcher",
      description: "Human behavior analysis, stress testing, controlled experiments.",
      icon: Brain,
      status: "inactive",
    },
    {
      name: "Crisis Strategist",
      description: "Media training, adversarial interviews, reputation management.",
      icon: MessageSquare,
      status: "inactive",
    },
    {
      name: "Therapy Trainer",
      description: "De-escalation practice, active listening, emotional conversations.",
      icon: Heart,
      status: "inactive",
    },
  ];

  return (
    <div className="min-h-screen bg-white flex flex-col" style={{ fontFamily: "'Helvetica Neue', Arial, sans-serif" }}>
      {/* Top bar */}
      <div className="flex items-center justify-between px-8 py-5 border-b border-gray-200">
        <div className="flex items-center gap-6">
          <button className="text-purple-700 hover:text-purple-900">
            <Menu size={28} strokeWidth={2.5} />
          </button>
          <button className="text-purple-700 hover:text-purple-900">
            <Search size={26} strokeWidth={2.5} />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <svg width="40" height="32" viewBox="0 0 40 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M2 20 L36 4 L20 18 L14 16 L12 28 L18 22 L26 26 L36 4"
              stroke="#a020a0"
              strokeWidth="2.5"
              fill="#a020a0"
              fillOpacity="0.9"
              strokeLinejoin="round"
            />
          </svg>
          <span
            className="text-4xl font-bold"
            style={{ color: "#a020a0", letterSpacing: "-0.02em" }}
          >
            leidos
          </span>
        </div>
      </div>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside
          className="w-[420px] p-6 relative overflow-hidden"
          style={{ backgroundColor: "#1a0d3d" }}
        >
          {/* Tab toggle */}
          <div className="bg-white rounded-full p-1 flex mb-8 relative">
            <button
              onClick={() => setActiveTab("History")}
              className={`flex-1 py-3 px-6 rounded-full font-semibold text-base transition-colors ${
                activeTab === "History"
                  ? "text-white"
                  : "text-gray-800"
              }`}
              style={{
                backgroundColor: activeTab === "History" ? "#a020a0" : "transparent",
              }}
            >
              History
            </button>
            <button
              onClick={() => setActiveTab("Settings")}
              className={`flex-1 py-3 px-6 rounded-full font-semibold text-base transition-colors ${
                activeTab === "Settings"
                  ? "text-white"
                  : "text-gray-800"
              }`}
              style={{
                backgroundColor: activeTab === "Settings" ? "#a020a0" : "transparent",
              }}
            >
              Settings
            </button>
          </div>

          {/* Role cards */}
          <div className="space-y-4 relative z-10">
            {roles.map((role) => {
              const Icon = role.icon;
              const isActive = activeRole === role.name;
              return (
                <button
                  key={role.name}
                  onClick={() => setActiveRole(role.name)}
                  className="w-full text-left rounded-2xl p-5 flex items-center gap-4 relative transition-all hover:scale-[1.01]"
                  style={{
                    backgroundColor: isActive ? "#a020a0" : "#2d1b5e",
                  }}
                >
                  <div className="w-14 h-14 rounded-full bg-white flex items-center justify-center flex-shrink-0">
                    <Icon size={26} color="#1a0d3d" strokeWidth={2} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-white font-bold text-lg mb-1">{role.name}</h3>
                    <p className="text-white/80 text-sm leading-snug">{role.description}</p>
                  </div>
                  <div
                    className="absolute top-3 right-3 w-2.5 h-2.5 rounded-full"
                    style={{
                      backgroundColor: role.status === "active" ? "#22c55e" : "#ef4444",
                    }}
                  />
                </button>
              );
            })}
          </div>

          {/* Decorative paper plane */}
          <svg
            className="absolute bottom-0 left-0 opacity-20"
            width="280"
            height="180"
            viewBox="0 0 280 180"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M10 130 L240 30 L120 110 L80 90 Z" fill="#a020a0" fillOpacity="0.6" />
            <path d="M80 90 L120 110 L100 160 Z" fill="#a020a0" fillOpacity="0.4" />
          </svg>
        </aside>

        {/* Main content */}
        <main className="flex-1 flex flex-col px-12 py-16 relative">
          <div className="flex-1 flex flex-col items-center justify-center">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">Hello, User!</h1>
            <p className="text-2xl text-gray-700">Welcome to Persona Weave.</p>
          </div>

          {/* Bottom section: Model + Persona */}
          <div className="space-y-4">
            {/* Model selector */}
            <div className="flex justify-end">
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 w-80">
                <label className="text-xs font-bold text-gray-900 tracking-wider mb-2 block">
                  MODEL
                </label>
                <button className="w-full bg-white border border-gray-200 rounded-full px-5 py-3 flex items-center justify-between hover:border-gray-300">
                  <span className="text-gray-800 font-medium">Persona Weave Beta</span>
                  <ChevronDown size={18} className="text-gray-600" />
                </button>
              </div>
            </div>

            {/* Persona + chat input */}
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
              <label className="text-xs font-bold text-gray-900 tracking-wider mb-3 block">
                PERSONA
              </label>
              <div className="flex gap-2 mb-4 flex-wrap">
                {["Persona 1", "Persona 2", "Persona 3", "Persona 4"].map((p) => {
                  const isActive = activePersona === p;
                  return (
                    <button
                      key={p}
                      onClick={() => setActivePersona(p)}
                      className="px-6 py-2 rounded-full font-semibold text-sm transition-colors border"
                      style={{
                        backgroundColor: isActive ? "#a020a0" : "white",
                        color: isActive ? "white" : "#1f2937",
                        borderColor: isActive ? "#a020a0" : "#e5e7eb",
                      }}
                    >
                      {p}
                    </button>
                  );
                })}
              </div>

              <div className="bg-white border border-gray-200 rounded-full px-5 py-3 flex items-center gap-3">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="How may we help you today?"
                  className="flex-1 bg-transparent outline-none text-gray-700 placeholder-gray-500"
                />
                <button
                  className="text-gray-700 hover:text-purple-700"
                  onClick={() => setMessage("")}
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
