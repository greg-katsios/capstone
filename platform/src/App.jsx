import { useState, useRef, useEffect } from "react";
import { Shield, Brain, Flag, UserCircle, Send, Plus, MessageSquare, ChevronDown, ThumbsUp, ThumbsDown, RotateCcw, Copy, Check } from "lucide-react";

const FONT    = "'Allianz Neo W04', 'Helvetica Neue', Arial, sans-serif";
const PURPLE  = "#a020a0";
const DARK_BG = "#1a0d3d";
const CARD_BG = "#2d1b5e";

/* ── Format timestamp like "May 4 - 2:15 PM (PST)" ── */
function formatTimestamp(date) {
  const d      = new Date(date);
  const month  = d.toLocaleString("en-US", { month: "short" });
  const day    = d.getDate();
  const hr24   = d.getHours();
  const hr12   = hr24 % 12 === 0 ? 12 : hr24 % 12;
  const mm     = String(d.getMinutes()).padStart(2, "0");
  const ampm   = hr24 >= 12 ? "PM" : "AM";
  const tzAbbr = d.toLocaleTimeString("en-US", { timeZoneName: "short" }).split(" ").pop();
  return `${month} ${day} - ${hr12}:${mm} ${ampm} (${tzAbbr})`;
}

/* ── Section label used throughout ── */
function Label({ children, light = false }) {
  return (
    <div style={{
      fontFamily: FONT,
      fontWeight: 700,
      fontSize: 13,
      letterSpacing: "0.12em",
      textAlign: "left",
      color: light ? "#fff" : "#111827",
      marginBottom: 14,
    }}>
      {children}
    </div>
  );
}

const ROLES = [
  {
    name: "Defense Analyst",
    description: "Defense systems, threat intelligence, strategic analysis.",
    icon: Shield,
    status: "active",
    systemPrompt: "You are a Defense Analyst AI persona. You specialize in defense systems, threat intelligence, and strategic analysis. Respond with expertise, precision, and a professional military/defense tone. Keep responses concise and structured.",
  },
  {
    name: "Behavior Researcher",
    description: "Human behavior analysis, stress testing, controlled experiments.",
    icon: Brain,
    status: "inactive",
    systemPrompt: "You are a Behavior Researcher AI persona. You specialize in human behavior analysis, psychological stress testing, and controlled experiments. Respond analytically and with academic rigor. Keep responses concise.",
  },
  {
    name: "Crisis Strategist",
    description: "Media training, adversarial interviews, reputation management.",
    icon: Flag,
    status: "inactive",
    systemPrompt: "You are a Crisis Strategist AI persona. You specialize in media training, adversarial interviews, and reputation management. Respond with sharp, strategic communication advice. Keep responses concise.",
  },
  {
    name: "Therapy Trainer",
    description: "De-escalation practice, active listening, emotional conversations.",
    icon: UserCircle,
    status: "inactive",
    systemPrompt: "You are a Therapy Trainer AI persona. You specialize in de-escalation practice, active listening, and emotional conversations. Respond with warmth, empathy, and therapeutic insight. Keep responses concise.",
  },
];

/* ── Slider ── */
function Slider({ label, value, onChange }) {
  return (
    <div style={{ marginTop: 28 }}>
      <Label light>{label}</Label>
      <div style={{ position: "relative", marginBottom: 6 }}>
        <div style={{
          position: "absolute", top: -34,
          left: `calc(${value * 100}% - 22px)`,
          backgroundColor: "#fff", color: DARK_BG,
          fontWeight: 700, fontSize: 12, padding: "3px 8px",
          borderRadius: 6, pointerEvents: "none", fontFamily: FONT, whiteSpace: "nowrap",
        }}>
          {value.toFixed(2)}
          <div style={{ position: "absolute", bottom: -5, left: "50%", transform: "translateX(-50%)", width: 0, height: 0, borderLeft: "5px solid transparent", borderRight: "5px solid transparent", borderTop: "5px solid #fff" }} />
        </div>
        <input
          type="range" min={0} max={1} step={0.01} value={value}
          onChange={e => onChange(parseFloat(e.target.value))}
          style={{ width: "100%", accentColor: PURPLE, cursor: "pointer", height: 4 }}
        />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", color: "rgba(255,255,255,0.35)", fontSize: 11, fontFamily: FONT }}>
        <span>0</span><span>1</span>
      </div>
    </div>
  );
}

/* ── Stepper (Temp) ── */
function Stepper({ label, value, onChange }) {
  const step = 0.1;
  const dec = () => onChange(Math.max(0, parseFloat((value - step).toFixed(1))));
  const inc = () => onChange(Math.min(1, parseFloat((value + step).toFixed(1))));

  return (
    <div style={{ marginTop: 28 }}>
      <Label light>{label}</Label>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <button onClick={dec} style={{ width: 36, height: 36, borderRadius: "50%", backgroundColor: "rgba(255,255,255,0.15)", border: "none", color: "#fff", fontSize: 20, cursor: value <= 0 ? "not-allowed" : "pointer", opacity: value <= 0 ? 0.4 : 1, fontFamily: FONT, display: "flex", alignItems: "center", justifyContent: "center" }}>
          −
        </button>
        <div style={{ flex: 1, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 999, padding: "10px 0", textAlign: "center", color: "#fff", fontWeight: 700, fontSize: 16, fontFamily: FONT, letterSpacing: "0.05em" }}>
          {value.toFixed(1)}
        </div>
        <button onClick={inc} style={{ width: 36, height: 36, borderRadius: "50%", backgroundColor: "rgba(255,255,255,0.15)", border: "none", color: "#fff", fontSize: 20, cursor: value >= 1 ? "not-allowed" : "pointer", opacity: value >= 1 ? 0.4 : 1, fontFamily: FONT, display: "flex", alignItems: "center", justifyContent: "center" }}>
          +
        </button>
      </div>
    </div>
  );
}

/* ── Chat bubble with action row for assistant messages ── */
function Bubble({ msg, RoleIcon, onRetry, onFeedback }) {
  const isUser     = msg.role === "user";
  const [copied,   setCopied]   = useState(false);
  const [feedback, setFeedback] = useState(msg.feedback || null); // 'up' | 'down' | null

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(msg.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch { /* ignore */ }
  };

  const handleFeedback = (kind) => {
    const next = feedback === kind ? null : kind;
    setFeedback(next);
    onFeedback?.(next);
  };

  const isPlaceholder = msg.content === "…";

  const ActionBtn = ({ children, onClick, active, title }) => (
    <button
      onClick={onClick}
      title={title}
      style={{
        background: "transparent",
        border: "none",
        padding: 5,
        borderRadius: 6,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: active ? PURPLE : "#9ca3af",
        transition: "color 0.15s, background 0.15s",
      }}
      onMouseEnter={e => { if (!active) e.currentTarget.style.color = "#374151"; e.currentTarget.style.background = "#f3f4f6"; }}
      onMouseLeave={e => { if (!active) e.currentTarget.style.color = "#9ca3af"; e.currentTarget.style.background = "transparent"; }}
    >
      {children}
    </button>
  );

  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", alignItems: "flex-end", gap: 10, marginBottom: 18 }}>
      {!isUser && (
        <div style={{ width: 34, height: 34, borderRadius: "50%", backgroundColor: DARK_BG, border: `2px solid ${PURPLE}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <RoleIcon size={16} color="#fff" strokeWidth={1.8} />
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", alignItems: isUser ? "flex-end" : "flex-start", maxWidth: "58%" }}>
        <div style={{
          padding: "12px 16px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          backgroundColor: isUser ? DARK_BG : "#f3f4f6",
          color: isUser ? "#fff" : "#111827",
          fontSize: 14, lineHeight: 1.6, fontFamily: FONT,
        }}>
          {msg.content}
        </div>

        {/* Action row — only on assistant messages, hidden while streaming/loading */}
        {!isUser && !isPlaceholder && (
          <div style={{ display: "flex", gap: 2, marginTop: 6, marginLeft: 4 }}>
            <ActionBtn onClick={() => handleFeedback("up")}   active={feedback === "up"}   title="Good response">
              <ThumbsUp size={15} strokeWidth={1.8} />
            </ActionBtn>
            <ActionBtn onClick={() => handleFeedback("down")} active={feedback === "down"} title="Bad response">
              <ThumbsDown size={15} strokeWidth={1.8} />
            </ActionBtn>
            <ActionBtn onClick={handleCopy} active={copied} title={copied ? "Copied!" : "Copy"}>
              {copied ? <Check size={15} strokeWidth={2} /> : <Copy size={15} strokeWidth={1.8} />}
            </ActionBtn>
            {onRetry && (
              <ActionBtn onClick={onRetry} title="Retry">
                <RotateCcw size={15} strokeWidth={1.8} />
              </ActionBtn>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function PersonaWeave() {
  const [activeTab,     setActiveTab]     = useState("Settings");
  const [activeRole,    setActiveRole]    = useState(ROLES[0]);
  const [activePersona, setActivePersona] = useState("Defense Analyst");
  const [temperature,   setTemperature]   = useState(0.5);
  const [topP,          setTopP]          = useState(0.9);
  const [conversations, setConversations] = useState([]);
  const [activeChatId,  setActiveChatId]  = useState(null);
  const [inputMsg,      setInputMsg]      = useState("");
  const [loading,       setLoading]       = useState(false);
  const bottomRef = useRef(null);

  const activeChat = conversations.find(c => c.id === activeChatId) || null;
  const chatRole   = ROLES.find(r => r.name === (activeChat?.role || activePersona)) || ROLES[0];
  const RoleIcon   = chatRole.icon;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages?.length]);

  async function retryMessage(assistantIndex) {
    if (loading || !activeChat) return;

    // Find the user message that produced this assistant message (the one right before it)
    const userIndex = assistantIndex - 1;
    if (userIndex < 0) return;
    const userMsg = activeChat.messages[userIndex];
    if (!userMsg || userMsg.role !== "user") return;

    // Truncate history up through that user message, then re-call the API
    const truncated = activeChat.messages.slice(0, userIndex + 1);
    const chatId    = activeChatId;

    setConversations(c => c.map(x => x.id === chatId
      ? { ...x, messages: [...truncated, { role: "assistant", content: "…" }] }
      : x
    ));
    setLoading(true);

    const role = ROLES.find(r => r.name === activeChat.role) || ROLES[0];

    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: role.systemPrompt,
          temperature,
          top_p: topP,
          messages: truncated.map(m => ({ role: m.role, content: m.content })),
        }),
      });
      const data  = await res.json();
      const reply = data.content?.find(b => b.type === "text")?.text || "No response received.";
      setConversations(c => c.map(x => x.id === chatId
        ? { ...x, messages: [...truncated, { role: "assistant", content: reply }] }
        : x
      ));
    } catch {
      setConversations(c => c.map(x => x.id === chatId
        ? { ...x, messages: [...truncated, { role: "assistant", content: "Connection error — please try again." }] }
        : x
      ));
    } finally {
      setLoading(false);
    }
  }

  function setMessageFeedback(messageIndex, value) {
    if (!activeChat) return;
    const chatId = activeChatId;
    setConversations(c => c.map(x => x.id === chatId
      ? { ...x, messages: x.messages.map((m, i) => i === messageIndex ? { ...m, feedback: value } : m) }
      : x
    ));
  }

  async function sendMessage() {
    const text = inputMsg.trim();
    if (!text || loading) return;
    setInputMsg("");

    let chatId     = activeChatId;
    let baseConvos = conversations;

    if (!chatId) {
      const now     = Date.now();
      const newChat = { id: now, title: text.slice(0, 42), role: activePersona, messages: [], createdAt: now };
      baseConvos = [newChat, ...conversations];
      setConversations(baseConvos);
      chatId = newChat.id;
      setActiveChatId(chatId);
    }

    const prev     = baseConvos.find(c => c.id === chatId)?.messages || [];
    const withUser = [...prev, { role: "user", content: text }];

    setConversations(c => c.map(x => x.id === chatId
      ? { ...x, messages: [...withUser, { role: "assistant", content: "…" }] }
      : x
    ));
    setLoading(true);

    const role = ROLES.find(r => r.name === (baseConvos.find(c => c.id === chatId)?.role || activePersona)) || ROLES[0];

    try {
      const res  = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: role.systemPrompt,
          temperature,
          top_p: topP,
          messages: withUser.map(m => ({ role: m.role, content: m.content })),
        }),
      });
      const data  = await res.json();
      const reply = data.content?.find(b => b.type === "text")?.text || "No response received.";
      setConversations(c => c.map(x => x.id === chatId
        ? { ...x, messages: [...withUser, { role: "assistant", content: reply }] }
        : x
      ));
    } catch {
      setConversations(c => c.map(x => x.id === chatId
        ? { ...x, messages: [...withUser, { role: "assistant", content: "Connection error — please try again." }] }
        : x
      ));
    } finally {
      setLoading(false);
    }
  }

  /* ── Shared input panel ── */
  function InputPanel() {
    return (
      <div style={{ padding: "14px 24px 20px", flexShrink: 0 }}>
        <div style={{ backgroundColor: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 14, padding: "16px 18px" }}>
          <Label>PERSONA SELECTION</Label>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            {ROLES.map(r => {
              const sel = activePersona === r.name;
              return (
                <button key={r.name}
                  onClick={() => { setActivePersona(r.name); setActiveRole(ROLES.find(x => x.name === r.name)); }}
                  style={{ padding: "7px 14px", borderRadius: 999, border: `1px solid ${sel ? PURPLE : "#e5e7eb"}`, backgroundColor: sel ? PURPLE : "#fff", color: sel ? "#fff" : "#1f2937", fontWeight: 600, fontSize: 13, cursor: "pointer", fontFamily: FONT, transition: "all 0.15s" }}>
                  {r.name}
                </button>
              );
            })}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: 999, padding: "9px 14px" }}>
            <input
              value={inputMsg} onChange={e => setInputMsg(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()}
              placeholder="How may we help you today?"
              style={{ flex: 1, border: "none", outline: "none", fontSize: 14, color: "#374151", backgroundColor: "transparent", fontFamily: FONT }}
            />
            <button onClick={sendMessage} disabled={loading}
              style={{ backgroundColor: loading ? "#d1d5db" : PURPLE, border: "none", borderRadius: "50%", width: 32, height: 32, display: "flex", alignItems: "center", justifyContent: "center", cursor: loading ? "not-allowed" : "pointer", flexShrink: 0, transition: "background 0.2s" }}>
              <Send size={14} color="#fff" />
            </button>
          </div>
        </div>

        {/* Model label — outside the box */}
        <div style={{
          textAlign: "center",
          marginTop: 10,
          fontFamily: FONT,
          fontWeight: 300,
          fontSize: 13,
          color: "#6b7280",
          letterSpacing: "0.02em",
        }}>
          Uses Qwen 3-1.7B Model
        </div>
      </div>
    );
  }

  /* ══════════════ RENDER ══════════════ */
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", fontFamily: FONT, backgroundColor: "#fff", overflow: "hidden" }}>

      {/* ── Top bar ── */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "13px 26px", borderBottom: "1px solid #e5e7eb", backgroundColor: "#fff", flexShrink: 0 }}>
        {/* Real Leidos logo */}
        <img
          src="/leidos_logo.png"
          alt="Leidos"
          style={{ height: 38, width: "auto", marginLeft: "auto" }}
        />
      </div>

      {/* ── Body ── */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>

        {/* ══ SIDEBAR ══ */}
        <aside style={{
          width: 440,
          flexShrink: 0,
          backgroundColor: DARK_BG,
          backgroundImage: "url('/landing_page_background.png')",
          backgroundSize: "auto 55%",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "left bottom",
          display: "flex",
          flexDirection: "column",
          padding: "20px 16px 0",
          overflowY: "auto",
          position: "relative",
        }}>

          {/* Tab toggle */}
          <div style={{ display: "flex", backgroundColor: "#fff", borderRadius: 999, padding: 4, marginBottom: 24, flexShrink: 0 }}>
            {["History", "Settings"].map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                style={{ flex: 1, padding: "10px 0", borderRadius: 999, border: "none", fontWeight: 700, fontSize: 14, cursor: "pointer", fontFamily: FONT, backgroundColor: activeTab === tab ? PURPLE : "transparent", color: activeTab === tab ? "#fff" : "#374151", transition: "all 0.2s" }}>
                {tab}
              </button>
            ))}
          </div>

          {/* ── HISTORY TAB ── */}
          {activeTab === "History" && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", paddingBottom: 20 }}>
              <Label light>CHAT HISTORY</Label>
              <button
                onClick={() => setActiveChatId(null)}
                style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 16px", borderRadius: 12, backgroundColor: PURPLE, border: "none", color: "#fff", fontWeight: 700, fontSize: 13, cursor: "pointer", marginBottom: 14, fontFamily: FONT }}>
                <Plus size={17} /> New Conversation
              </button>

              {conversations.length === 0 ? (
                <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12, paddingBottom: 60 }}>
                  <MessageSquare size={50} color="rgba(255,255,255,0.2)" strokeWidth={1.2} />
                  <div style={{ textAlign: "center" }}>
                    <div style={{ color: "#fff", fontWeight: 600, fontSize: 14, marginBottom: 4, fontFamily: FONT }}>No conversations yet.</div>
                    <div style={{ color: "rgba(255,255,255,0.45)", fontSize: 12, fontFamily: FONT }}>Start a new chat to get going.</div>
                  </div>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
                  {conversations.map(c => {
                    const isActive = activeChatId === c.id;
                    return (
                      <button key={c.id} onClick={() => setActiveChatId(c.id)}
                        style={{
                          padding: "13px 16px",
                          borderRadius: 14,
                          backgroundColor: isActive ? PURPLE : "rgba(255,255,255,0.07)",
                          border: isActive ? "2px solid #4ea3ff" : "2px solid transparent",
                          color: "#fff",
                          textAlign: "left",
                          cursor: "pointer",
                          fontFamily: FONT,
                          transition: "all 0.15s",
                          display: "flex",
                          flexDirection: "column",
                          gap: 4,
                        }}>
                        <div style={{ fontWeight: 700, fontSize: 15, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                          {c.title}
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                          <span style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                            {c.role}
                          </span>
                          {c.createdAt && (
                            <span style={{ fontSize: 11, color: "rgba(255,255,255,0.55)", whiteSpace: "nowrap", flexShrink: 0 }}>
                              {formatTimestamp(c.createdAt)}
                            </span>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* ── SETTINGS TAB ── */}
          {activeTab === "Settings" && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", paddingBottom: 28 }}>
              <Label light>PERSONA SELECTION</Label>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {ROLES.map(role => {
                  const Icon     = role.icon;
                  const isActive = activeRole.name === role.name;
                  return (
                    <button key={role.name}
                      onClick={() => { setActiveRole(role); setActivePersona(role.name); }}
                      style={{ display: "flex", alignItems: "center", gap: 13, padding: "13px 14px", borderRadius: 15, border: isActive ? `2px solid rgba(200,100,200,0.6)` : "2px solid transparent", backgroundColor: isActive ? PURPLE : "rgba(45,27,94,0.85)", cursor: "pointer", textAlign: "left", position: "relative", transition: "all 0.15s" }}>
                      <div style={{ position: "absolute", top: 10, right: 10, width: 8, height: 8, borderRadius: "50%", backgroundColor: isActive ? "#22c55e" : "#ef4444" }} />
                      <div style={{ width: 46, height: 46, borderRadius: "50%", backgroundColor: "#fff", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                        <Icon size={21} color={DARK_BG} strokeWidth={2} />
                      </div>
                      <div>
                        <div style={{ color: "#fff", fontWeight: 700, fontSize: 15, marginBottom: 3, fontFamily: FONT }}>{role.name}</div>
                        <div style={{ color: "rgba(255,255,255,0.65)", fontSize: 12, lineHeight: 1.4, fontFamily: FONT }}>{role.description}</div>
                      </div>
                    </button>
                  );
                })}
              </div>

              <Stepper label="TEMPERATURE" value={temperature} onChange={setTemperature} />
              <Slider label="TOP P"        value={topP}         onChange={setTopP} />
            </div>
          )}
        </aside>

        {/* ══ MAIN ══ */}
        <main style={{ flex: 1, display: "flex", flexDirection: "column", backgroundColor: "#fff", overflow: "hidden" }}>

          {activeChat ? (
            /* ── ACTIVE CHAT ── */
            <>
              <div style={{ padding: "18px 28px 14px", borderBottom: "1px solid #f0f0f0", flexShrink: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <img
                    src="/airplane.png"
                    alt="Persona Weave"
                    style={{ width: 50, height: 50, objectFit: "contain", flexShrink: 0 }}
                  />
                  <div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#111827", fontFamily: FONT }}>Hello, User!</div>
                    <div style={{ fontSize: 13, color: "#6b7280", display: "flex", alignItems: "center", gap: 6, marginTop: 2, fontFamily: FONT }}>
                      You are chatting with:
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 5, backgroundColor: "#f3f4f6", borderRadius: 999, padding: "2px 10px 2px 5px" }}>
                        <div style={{ width: 18, height: 18, borderRadius: "50%", backgroundColor: PURPLE, display: "flex", alignItems: "center", justifyContent: "center" }}>
                          <RoleIcon size={10} color="#fff" strokeWidth={2.2} />
                        </div>
                        <span style={{ fontWeight: 600, color: "#111827", fontSize: 13 }}>{activeChat.role}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ flex: 1, overflowY: "auto", padding: "22px 28px" }}>
                  {activeChat.messages.map((msg, i) => (
                    <Bubble
                      key={i}
                      msg={msg}
                      RoleIcon={RoleIcon}
                      onRetry={msg.role === "assistant" ? () => retryMessage(i) : undefined}
                      onFeedback={msg.role === "assistant" ? (val) => setMessageFeedback(i, val) : undefined}
                    />
                  ))}
                <div ref={bottomRef} />
              </div>

              <InputPanel />
            </>
          ) : (
            /* ── LANDING ── */
            <>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                <img
                  src="/airplane.png"
                  alt="Persona Weave"
                  style={{ width: 111, height: 111, marginBottom: 22, objectFit: "contain" }}
                />
                <h1 style={{ fontSize: 40, fontWeight: 700, color: "#111827", margin: "0 0 8px", fontFamily: FONT }}>Hello, User!</h1>
                <p style={{ fontSize: 17, color: "#6b7280", margin: 0, fontFamily: FONT }}>Welcome to Persona Weave.</p>
              </div>

              <InputPanel />
            </>
          )}
        </main>
      </div>
    </div>
  );
}