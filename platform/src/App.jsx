import { useState, useRef, useEffect } from "react";
import { Eye, Brain, Flag, UserCircle, Send, Plus, MessageSquare, ThumbsUp, ThumbsDown, RotateCcw, Copy, Check, ChevronDown } from "lucide-react";

const FONT    = "'Allianz Neo W04', 'Helvetica Neue', Arial, sans-serif";
const PURPLE  = "#a020a0";
const DARK_BG = "#1a0d3d";

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
    name: "Case Witness",
    description: "A simulated deponent or courtroom witness trained to challenge examination technique under pressure.",
    icon: Eye,
    tone: "Guarded",
    extendedDescription: "A simulated deponent or courtroom witness with a defined role, backstory, and agenda. Designed to train law students, attorneys, and paralegals in examination technique, cross-examination strategy, and deposition practice. Self-interested and evasive under pressure — only reveals protected information when questioned with precision.",
    tags: ["Deposition simulation", "Cross-examination", "Legal training"],
    systemPrompt: `You are a simulated witness in a legal proceeding — either a deposition or courtroom examination. You have a defined role in the case (plaintiff, defendant, bystander, or expert), a backstory, and details you are motivated to protect or conceal.

- Answer only what is directly asked. Do not volunteer information.
- Stay fully consistent with your established story across the entire session.
- Become evasive or defensive when questions approach a vulnerability in your account.
- Only reveal protected information if the user constructs a precise, well-reasoned line of questioning.
- If questioned sloppily or broadly, give minimal answers that technically satisfy the question.
- As an expert witness variant, be confident and credentialed — resist being led, challenge imprecise framing, and don't concede points without pressure.

Begin with: "I've been advised by my counsel to answer your questions. Go ahead."`,
  },
  {
    name: "Behavior Researcher",
    description: "Safe simulations of human reactions under stress and uncertainty.",
    icon: Brain,
    tone: "Analytical",
    extendedDescription: "Designed for psychologists, behavioral scientists, and academic researchers who study how people react under stress or uncertainty. Replaces risky real-world experiments with controlled, repeatable simulations that surface genuine behavioral patterns safely.",
    tags: ["Stress response", "Controlled simulation", "Academic research"],
    systemPrompt: "You are a Behavior Researcher AI persona. You specialize in human behavior analysis, psychological stress testing, and controlled experiments. Respond analytically and with academic rigor. Keep responses concise.",
  },
  {
    name: "Crisis Strategist",
    description: "Adversarial press briefings, hostile interviews, and reputation-crisis scenarios.",
    icon: Flag,
    tone: "Direct",
    extendedDescription: "Built for journalists and PR strategists who need to practice under fire. Simulates hostile press briefings, adversarial interviews, and reputation-crisis scenarios at scale. Presents a believable spokesperson persona so practitioners can sharpen their message control before it counts.",
    tags: ["Press briefings", "Reputation crisis", "Media training"],
    systemPrompt: "You are a Crisis Strategist AI persona. You specialize in media training, adversarial interviews, and reputation management. Respond with sharp, strategic communication advice. Keep responses concise.",
  },
  {
    name: "Therapy Trainer",
    description: "Safe simulation of emotionally complex conversations for mental health training.",
    icon: UserCircle,
    tone: "Empathetic",
    extendedDescription: "Designed for mental health counselors and therapists in training. Simulates supportive, non-judgmental conversations to practice de-escalation, active listening, and boundary-setting. Use case without involving real clients or exposing trainees to uncontrolled emotional risk.",
    tags: ["De-escalation", "Active listening", "Boundary-setting"],
    systemPrompt: "You are a Therapy Trainer AI persona. You specialize in de-escalation practice, active listening, and emotional conversations. Respond with warmth, empathy, and therapeutic insight. Keep responses concise.",
  },
];

function Slider({ label, value, onChange, a11y }) {
  const percent = value * 100;
  const clampedLeft = `clamp(0px, calc(${percent}% - 22px), calc(100% - 44px))`;
  return (
    <div style={{ marginTop: 28 }}>
      <Label light>{label}</Label>
      <div style={{ position: "relative", marginBottom: 6, marginTop: 36 }}>
        <div style={{
          position: "absolute", top: -38, left: clampedLeft,
          backgroundColor: "#fff", color: DARK_BG,
          fontWeight: 700, fontSize: a11y ? 13 : 12, padding: "3px 8px",
          borderRadius: 6, pointerEvents: "none", fontFamily: FONT, whiteSpace: "nowrap",
        }}>
          {value.toFixed(2)}
          <div style={{ position: "absolute", bottom: -5, left: "50%", transform: "translateX(-50%)", width: 0, height: 0, borderLeft: "5px solid transparent", borderRight: "5px solid transparent", borderTop: "5px solid #fff" }} />
        </div>
        <input type="range" min={0} max={1} step={0.01} value={value}
          onChange={e => onChange(parseFloat(e.target.value))}
          style={{ width: "100%", accentColor: PURPLE, cursor: "pointer", height: a11y ? 6 : 4 }}
        />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", color: "rgba(255,255,255,0.5)", fontSize: a11y ? 13 : 11, fontFamily: FONT }}>
        <span>0</span><span>1</span>
      </div>
    </div>
  );
}

function Stepper({ label, value, onChange, a11y }) {
  const step = 0.1;
  const dec = () => onChange(Math.max(0, parseFloat((value - step).toFixed(1))));
  const inc = () => onChange(Math.min(1, parseFloat((value + step).toFixed(1))));
  return (
    <div style={{ marginTop: 28 }}>
      <Label light>{label}</Label>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <button onClick={dec} style={{ width: a11y ? 42 : 36, height: a11y ? 42 : 36, borderRadius: "50%", backgroundColor: "rgba(255,255,255,0.15)", border: a11y ? "2px solid rgba(255,255,255,0.4)" : "none", color: "#fff", fontSize: 20, cursor: value <= 0 ? "not-allowed" : "pointer", opacity: value <= 0 ? 0.4 : 1, fontFamily: FONT, display: "flex", alignItems: "center", justifyContent: "center" }}>−</button>
        <div style={{ flex: 1, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 999, padding: "10px 0", textAlign: "center", color: "#fff", fontWeight: 700, fontSize: a11y ? 18 : 16, fontFamily: FONT, letterSpacing: "0.05em" }}>{value.toFixed(1)}</div>
        <button onClick={inc} style={{ width: a11y ? 42 : 36, height: a11y ? 42 : 36, borderRadius: "50%", backgroundColor: "rgba(255,255,255,0.15)", border: a11y ? "2px solid rgba(255,255,255,0.4)" : "none", color: "#fff", fontSize: 20, cursor: value >= 1 ? "not-allowed" : "pointer", opacity: value >= 1 ? 0.4 : 1, fontFamily: FONT, display: "flex", alignItems: "center", justifyContent: "center" }}>+</button>
      </div>
    </div>
  );
}

function Bubble({ msg, RoleIcon, onRetry, onFeedback, fontSize }) {
  const isUser = msg.role === "user";
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(msg.feedback || null);

  const handleCopy = async () => {
    try { await navigator.clipboard.writeText(msg.content); setCopied(true); setTimeout(() => setCopied(false), 1500); } catch { }
  };
  const handleFeedback = (kind) => { const next = feedback === kind ? null : kind; setFeedback(next); onFeedback?.(next); };
  const isPlaceholder = msg.content === "…";

  const ActionBtn = ({ children, onClick, active, title }) => (
    <button onClick={onClick} title={title}
      style={{ background: "transparent", border: "none", padding: 5, borderRadius: 6, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: active ? PURPLE : "#9ca3af", transition: "color 0.15s, background 0.15s" }}
      onMouseEnter={e => { if (!active) e.currentTarget.style.color = "#374151"; e.currentTarget.style.background = "#f3f4f6"; }}
      onMouseLeave={e => { if (!active) e.currentTarget.style.color = "#9ca3af"; e.currentTarget.style.background = "transparent"; }}>
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
      <div style={{ display: "flex", flexDirection: "column", alignItems: isUser ? "flex-end" : "flex-start", maxWidth: "70%" }}>
        <div style={{ padding: "12px 16px", borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px", backgroundColor: isUser ? DARK_BG : "#f3f4f6", color: isUser ? "#fff" : "#111827", fontSize: fontSize || 14, lineHeight: 1.65, fontFamily: FONT }}>
          {msg.content}
        </div>
        {!isUser && !isPlaceholder && (
          <div style={{ display: "flex", gap: 2, marginTop: 6, marginLeft: 4 }}>
            <ActionBtn onClick={() => handleFeedback("up")}   active={feedback === "up"}   title="Good response"><ThumbsUp size={15} strokeWidth={1.8} /></ActionBtn>
            <ActionBtn onClick={() => handleFeedback("down")} active={feedback === "down"} title="Bad response"><ThumbsDown size={15} strokeWidth={1.8} /></ActionBtn>
            <ActionBtn onClick={handleCopy} active={copied} title={copied ? "Copied!" : "Copy"}>
              {copied ? <Check size={15} strokeWidth={2} /> : <Copy size={15} strokeWidth={1.8} />}
            </ActionBtn>
            {onRetry && <ActionBtn onClick={onRetry} title="Retry"><RotateCcw size={15} strokeWidth={1.8} /></ActionBtn>}
          </div>
        )}
      </div>
    </div>
  );
}

function InputPanel({ inputMsg, setInputMsg, sendMessage, loading, activePersona, setActivePersona, setActiveRole, accessibilityMode, A11Y }) {
  return (
    <div style={{ padding: "14px 24px 20px", flexShrink: 0 }}>
      <div style={{ backgroundColor: A11Y.inputBg, border: A11Y.inputBorder, borderRadius: 14, padding: "16px 18px" }}>
        <Label>PERSONA SELECTION</Label>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
          {ROLES.map(r => {
            const sel = activePersona === r.name;
            return (
              <button key={r.name}
                onClick={() => { setActivePersona(r.name); setActiveRole(ROLES.find(x => x.name === r.name)); }}
                style={{ padding: accessibilityMode ? "9px 16px" : "7px 14px", borderRadius: 999, border: `${accessibilityMode ? "2px" : "1px"} solid ${sel ? PURPLE : (accessibilityMode ? "#9ca3af" : "#e5e7eb")}`, backgroundColor: sel ? PURPLE : "#fff", color: sel ? "#fff" : "#1f2937", fontWeight: 600, fontSize: A11Y.fontSize, cursor: "pointer", fontFamily: FONT, transition: "all 0.15s" }}>
                {r.name}
              </button>
            );
          })}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, backgroundColor: "#fff", border: accessibilityMode ? "2px solid #d1d5db" : "1px solid #e5e7eb", borderRadius: 999, padding: "9px 14px" }}>
          <input value={inputMsg} onChange={e => setInputMsg(e.target.value)} onKeyDown={e => e.key === "Enter" && sendMessage()} placeholder="How may we help you today?"
            style={{ flex: 1, border: "none", outline: "none", fontSize: A11Y.fontSize, color: "#374151", backgroundColor: "transparent", fontFamily: FONT, minWidth: 0 }} />
          <button onClick={sendMessage} disabled={loading}
            style={{ backgroundColor: loading ? "#d1d5db" : PURPLE, border: "none", borderRadius: "50%", width: accessibilityMode ? 38 : 32, height: accessibilityMode ? 38 : 32, display: "flex", alignItems: "center", justifyContent: "center", cursor: loading ? "not-allowed" : "pointer", flexShrink: 0, transition: "background 0.2s" }}>
            <Send size={accessibilityMode ? 16 : 14} color="#fff" />
          </button>
        </div>
      </div>
      <div style={{ textAlign: "center", marginTop: 10, fontFamily: FONT, fontWeight: accessibilityMode ? 500 : 300, fontSize: accessibilityMode ? 14 : 13, color: accessibilityMode ? "#111827" : "#6b7280", letterSpacing: "0.02em" }}>
        Uses Qwen 3-1.7B Model
      </div>
    </div>
  );
}

export default function PersonaWeave() {
  const [activeTab,         setActiveTab]        = useState("Settings");
  const [activeRole,        setActiveRole]        = useState(ROLES[0]);
  const [activePersona,     setActivePersona]     = useState("Case Witness");
  const [temperature,       setTemperature]       = useState(0.5);
  const [topP,              setTopP]              = useState(0.9);
  const [conversations,     setConversations]     = useState([]);
  const [activeChatId,      setActiveChatId]      = useState(null);
  const [inputMsg,          setInputMsg]          = useState("");
  const [loading,           setLoading]           = useState(false);
  const [accessibilityMode, setAccessibilityMode] = useState(false);
  const [expandedRole,      setExpandedRole]      = useState(ROLES[0].name);
  const [windowWidth,       setWindowWidth]       = useState(typeof window !== "undefined" ? window.innerWidth : 1280);
  const bottomRef = useRef(null);

  useEffect(() => {
    const onResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const isCompact    = windowWidth < 1100;
  const isMobile     = windowWidth < 768;
  const sidebarWidth = isMobile ? 240 : isCompact ? 300 : 380;

  const A11Y = {
    sidebarBg:      accessibilityMode ? "#0f0a2a"                          : DARK_BG,
    cardBg:         accessibilityMode ? "rgba(255,255,255,0.08)"           : "rgba(45,27,94,0.85)",
    cardBgActive:   accessibilityMode ? "#7c3aed"                          : PURPLE,
    cardBorder:     accessibilityMode ? "2px solid rgba(200,160,255,0.55)" : "2px solid transparent",
    cardText:       accessibilityMode ? "#ffffff"                          : "#fff",
    cardSubText:    accessibilityMode ? "rgba(255,255,255,0.8)"            : "rgba(255,255,255,0.65)",
    labelColor:     accessibilityMode ? "#e5d9ff"                          : "#fff",
    fontSize:       accessibilityMode ? 15                                 : 14,
    inputBg:        accessibilityMode ? "#ffffff"                          : "#f9fafb",
    inputBorder:    accessibilityMode ? "2px solid #7c3aed"                : "1px solid #e5e7eb",
    historyBg:      accessibilityMode ? "rgba(255,255,255,0.08)"           : "rgba(255,255,255,0.07)",
    historyBorder:  accessibilityMode ? "2px solid rgba(200,160,255,0.45)" : "2px solid transparent",
    tabActiveBg:    accessibilityMode ? "#7c3aed"                          : PURPLE,
    bubbleFontSize: accessibilityMode ? 15                                 : 14,
  };

  const activeChat = conversations.find(c => c.id === activeChatId) || null;
  const chatRole   = ROLES.find(r => r.name === (activeChat?.role || activePersona)) || ROLES[0];
  const RoleIcon   = chatRole.icon;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages?.length]);

  async function retryMessage(assistantIndex) {
    if (loading || !activeChat) return;
    const userIndex = assistantIndex - 1;
    if (userIndex < 0) return;
    const userMsg = activeChat.messages[userIndex];
    if (!userMsg || userMsg.role !== "user") return;
    const truncated = activeChat.messages.slice(0, userIndex + 1);
    const chatId    = activeChatId;
    setConversations(c => c.map(x => x.id === chatId ? { ...x, messages: [...truncated, { role: "assistant", content: "…" }] } : x));
    setLoading(true);
    const role = ROLES.find(r => r.name === activeChat.role) || ROLES[0];
    try {
      const res  = await fetch("http://localhost:8000/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ system: role.systemPrompt, temperature, top_p: topP, messages: truncated.map(m => ({ role: m.role, content: m.content })) }) });
      const data = await res.json();
      setConversations(c => c.map(x => x.id === chatId ? { ...x, messages: [...truncated, { role: "assistant", content: data.reply || "No response received." }] } : x));
    } catch {
      setConversations(c => c.map(x => x.id === chatId ? { ...x, messages: [...truncated, { role: "assistant", content: "Connection error — please try again." }] } : x));
    } finally { setLoading(false); }
  }

  function setMessageFeedback(messageIndex, value) {
    if (!activeChat) return;
    const chatId = activeChatId;
    setConversations(c => c.map(x => x.id === chatId ? { ...x, messages: x.messages.map((m, i) => i === messageIndex ? { ...m, feedback: value } : m) } : x));
  }

  async function sendMessage() {
    const text = inputMsg.trim();
    if (!text || loading) return;
    setInputMsg("");
    let chatId = activeChatId;
    let baseConvos = conversations;
    if (!chatId) {
      const now = Date.now();
      const newChat = { id: now, title: text.slice(0, 42), role: activePersona, messages: [], createdAt: now };
      baseConvos = [newChat, ...conversations];
      setConversations(baseConvos);
      chatId = newChat.id;
      setActiveChatId(chatId);
    }
    const prev     = baseConvos.find(c => c.id === chatId)?.messages || [];
    const withUser = [...prev, { role: "user", content: text }];
    setConversations(c => c.map(x => x.id === chatId ? { ...x, messages: [...withUser, { role: "assistant", content: "…" }] } : x));
    setLoading(true);
    const role = ROLES.find(r => r.name === (baseConvos.find(c => c.id === chatId)?.role || activePersona)) || ROLES[0];
    try {
      const res  = await fetch("http://localhost:8000/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ system: role.systemPrompt, temperature, top_p: topP, messages: withUser.map(m => ({ role: m.role, content: m.content })) }) });
      const data = await res.json();
      setConversations(c => c.map(x => x.id === chatId ? { ...x, messages: [...withUser, { role: "assistant", content: data.reply || "No response received." }] } : x));
    } catch {
      setConversations(c => c.map(x => x.id === chatId ? { ...x, messages: [...withUser, { role: "assistant", content: "Connection error — please try again." }] } : x));
    } finally { setLoading(false); }
  }

  const inputPanelProps = { inputMsg, setInputMsg, sendMessage, loading, activePersona, setActivePersona, setActiveRole, accessibilityMode, A11Y };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", fontFamily: FONT, backgroundColor: "#fff", overflow: "hidden" }}>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "13px 26px", borderBottom: accessibilityMode ? "2px solid #e5e7eb" : "1px solid #e5e7eb", backgroundColor: "#fff", flexShrink: 0 }}>
        <img src="/leidos_logo.png" alt="Leidos" style={{ height: 38, width: "auto", marginLeft: "auto" }} />
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden", minHeight: 0 }}>

        <aside style={{ width: sidebarWidth, flexShrink: 0, backgroundColor: A11Y.sidebarBg, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <div style={{ position: "relative", zIndex: 1, flex: 1, display: "flex", flexDirection: "column", padding: "20px 16px 0", overflowY: "auto" }}>

            <div style={{ display: "flex", backgroundColor: "#fff", borderRadius: 999, padding: 4, marginBottom: 24, flexShrink: 0 }}>
              {["History", "Settings"].map(tab => (
                <button key={tab} onClick={() => setActiveTab(tab)}
                  style={{ flex: 1, padding: accessibilityMode ? "12px 0" : "10px 0", borderRadius: 999, border: "none", fontWeight: 700, fontSize: accessibilityMode ? 15 : 14, cursor: "pointer", fontFamily: FONT, backgroundColor: activeTab === tab ? A11Y.tabActiveBg : "transparent", color: activeTab === tab ? "#fff" : "#374151", transition: "all 0.2s" }}>
                  {tab}
                </button>
              ))}
            </div>

            {activeTab === "History" && (
              <div style={{ flex: 1, display: "flex", flexDirection: "column", paddingBottom: 20 }}>
                <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 13, letterSpacing: "0.12em", color: A11Y.labelColor, marginBottom: 14 }}>CHAT HISTORY</div>
                <button onClick={() => setActiveChatId(null)}
                  style={{ display: "flex", alignItems: "center", gap: 10, padding: accessibilityMode ? "14px 16px" : "12px 16px", borderRadius: 12, backgroundColor: PURPLE, border: accessibilityMode ? "2px solid rgba(255,255,255,0.3)" : "none", color: "#fff", fontWeight: 700, fontSize: accessibilityMode ? 15 : 13, cursor: "pointer", marginBottom: 14, fontFamily: FONT }}>
                  <Plus size={17} /> New Conversation
                </button>
                {conversations.length === 0 ? (
                  <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12, paddingBottom: 60 }}>
                    <MessageSquare size={50} color="rgba(255,255,255,0.2)" strokeWidth={1.2} />
                    <div style={{ textAlign: "center" }}>
                      <div style={{ color: "#fff", fontWeight: 600, fontSize: accessibilityMode ? 15 : 14, marginBottom: 4, fontFamily: FONT }}>No conversations yet.</div>
                      <div style={{ color: "rgba(255,255,255,0.6)", fontSize: accessibilityMode ? 13 : 12, fontFamily: FONT }}>Start a new chat to get going.</div>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
                    {conversations.map(c => {
                      const isActive = activeChatId === c.id;
                      return (
                        <button key={c.id} onClick={() => setActiveChatId(c.id)}
                          style={{ padding: accessibilityMode ? "15px 16px" : "13px 16px", borderRadius: 14, backgroundColor: isActive ? PURPLE : A11Y.historyBg, border: isActive ? (accessibilityMode ? "2px solid #c4b5fd" : "2px solid #4ea3ff") : A11Y.historyBorder, color: "#fff", textAlign: "left", cursor: "pointer", fontFamily: FONT, transition: "all 0.15s", display: "flex", flexDirection: "column", gap: 4 }}>
                          <div style={{ fontWeight: 700, fontSize: 15, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{c.title}</div>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                            <span style={{ fontSize: accessibilityMode ? 13 : 12, color: "rgba(255,255,255,0.75)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{c.role}</span>
                            {c.createdAt && <span style={{ fontSize: accessibilityMode ? 12 : 11, color: "rgba(255,255,255,0.65)", whiteSpace: "nowrap", flexShrink: 0 }}>{formatTimestamp(c.createdAt)}</span>}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {activeTab === "Settings" && (
              <div style={{ flex: 1, display: "flex", flexDirection: "column", paddingBottom: 28 }}>
                <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 13, letterSpacing: "0.12em", color: A11Y.labelColor, marginBottom: 14 }}>PERSONA SELECTION</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {ROLES.map(role => {
                    const Icon       = role.icon;
                    const isActive   = activeRole.name === role.name;
                    const isExpanded = expandedRole === role.name;

                    return (
                      <div key={role.name} style={{
                        borderRadius: 15,
                        border: isActive ? `2px solid rgba(200,100,200,0.7)` : A11Y.cardBorder,
                        backgroundColor: isActive ? A11Y.cardBgActive : A11Y.cardBg,
                        overflow: "hidden",
                        transition: "border 0.15s, background 0.15s",
                      }}>
                        <button
                          onClick={() => { setActiveRole(role); setActivePersona(role.name); setExpandedRole(isExpanded ? null : role.name); }}
                          style={{ width: "100%", display: "flex", alignItems: "center", gap: 13, padding: accessibilityMode ? "15px 14px" : "13px 14px", background: "transparent", border: "none", cursor: "pointer", textAlign: "left", position: "relative" }}>
                          <div style={{ position: "absolute", top: "50%", right: 12, transform: `translateY(-50%) rotate(${isExpanded ? 180 : 0}deg)`, transition: "transform 0.22s ease", color: "rgba(255,255,255,0.5)", display: "flex", alignItems: "center" }}>
                            <ChevronDown size={16} strokeWidth={2} />
                          </div>
                          <div style={{ width: 46, height: 46, borderRadius: "50%", backgroundColor: "#fff", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                            <Icon size={21} color={DARK_BG} strokeWidth={2} />
                          </div>
                          <div style={{ minWidth: 0, flex: 1, paddingRight: 28 }}>
                            <div style={{ color: A11Y.cardText, fontWeight: 700, fontSize: accessibilityMode ? 16 : 15, marginBottom: 3, fontFamily: FONT }}>{role.name}</div>
                            <div style={{ color: "rgba(255,255,255,0.92)", fontSize: accessibilityMode ? 13 : 12, lineHeight: 1.4, fontFamily: FONT }}>{role.description}</div>
                          </div>
                        </button>

                        {/* ── Expanded dropdown — same padding for all cards ── */}
                        <div style={{ maxHeight: isExpanded ? 320 : 0, overflow: "hidden", transition: "max-height 0.25s ease", backgroundColor: isActive ? "rgba(49,32,90,0.95)" : "rgba(49,32,90,0.5)" }}>
                          <div style={{
                            borderTop: "1px solid rgba(255,255,255,0.15)",
                            padding: "14px 16px 16px",
                          }}>
                            <p style={{ color: "rgba(255,255,255,0.92)", fontSize: accessibilityMode ? 13 : 12, lineHeight: 1.65, fontFamily: FONT, margin: "0 0 12px" }}>
                              {role.extendedDescription}
                            </p>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
                              {role.tags.map(tag => (
                                <span key={tag} style={{ padding: "3px 10px", borderRadius: 999, backgroundColor: "rgba(255,255,255,0.12)", border: "1px solid rgba(255,255,255,0.15)", color: "rgba(255,255,255,0.9)", fontSize: accessibilityMode ? 12 : 11, fontFamily: FONT, fontWeight: 500, letterSpacing: "0.02em", textTransform: "capitalize" }}>
                                  {tag}
                                </span>
                              ))}
                            </div>
                            <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                              <span style={{ color: "rgba(255,255,255,0.45)", fontSize: accessibilityMode ? 12 : 11, fontFamily: FONT, letterSpacing: "0.06em", fontWeight: 600 }}>TONE</span>
                              <span style={{ padding: "2px 10px", borderRadius: 999, backgroundColor: isActive ? "rgba(255,255,255,0.2)" : "rgba(160,32,160,0.35)", color: "#fff", fontSize: accessibilityMode ? 12 : 11, fontFamily: FONT, fontWeight: 700, letterSpacing: "0.04em" }}>
                                {role.tone}
                              </span>
                            </div>
                          </div>
                        </div>

                      </div>
                    );
                  })}
                </div>

                <div style={{ marginTop: 28 }}>
                  <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 13, letterSpacing: "0.12em", color: A11Y.labelColor, marginBottom: 14 }}>ACCESSIBILITY</div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, backgroundColor: accessibilityMode ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.05)", border: accessibilityMode ? "2px solid rgba(200,160,255,0.45)" : "2px solid transparent", borderRadius: 15, padding: "14px 16px" }}>
                    <div>
                      <div style={{ color: "#fff", fontWeight: 700, fontSize: accessibilityMode ? 15 : 14, fontFamily: FONT }}>Accessibility Friendly</div>
                      <div style={{ color: A11Y.cardSubText, fontSize: accessibilityMode ? 13 : 12, fontFamily: FONT, marginTop: 3 }}>High contrast, larger text</div>
                    </div>
                    <label style={{ position: "relative", width: 50, height: 28, flexShrink: 0, cursor: "pointer" }}>
                      <input type="checkbox" checked={accessibilityMode} onChange={e => setAccessibilityMode(e.target.checked)} style={{ opacity: 0, width: 0, height: 0, position: "absolute" }} />
                      <span style={{ position: "absolute", inset: 0, borderRadius: 999, backgroundColor: accessibilityMode ? "#7c3aed" : "rgba(255,255,255,0.25)", transition: "background 0.2s", border: "2px solid rgba(255,255,255,0.2)" }}>
                        <span style={{ position: "absolute", top: 3, left: accessibilityMode ? 24 : 3, width: 18, height: 18, borderRadius: "50%", backgroundColor: "#fff", transition: "left 0.2s", boxShadow: "0 1px 3px rgba(0,0,0,0.3)" }} />
                      </span>
                    </label>
                  </div>
                </div>

                <Stepper label="TEMPERATURE" value={temperature} onChange={setTemperature} a11y={accessibilityMode} />
                <Slider  label="TOP P"       value={topP}         onChange={setTopP}         a11y={accessibilityMode} />
              </div>
            )}
          </div>
        </aside>

        <main style={{ flex: 1, display: "flex", flexDirection: "column", backgroundColor: "#fff", overflow: "hidden", minWidth: 0 }}>
          {activeChat ? (
            <>
              <div style={{ padding: "18px 28px 14px", borderBottom: accessibilityMode ? "2px solid #f0f0f0" : "1px solid #f0f0f0", flexShrink: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <img src="/airplane.png" alt="Persona Weave" style={{ width: 50, height: 50, objectFit: "contain", flexShrink: 0 }} />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: accessibilityMode ? 22 : 20, fontWeight: 700, color: "#111827", fontFamily: FONT }}>Hello, User!</div>
                    <div style={{ fontSize: accessibilityMode ? 14 : 13, color: "#6b7280", display: "flex", alignItems: "center", gap: 6, marginTop: 2, fontFamily: FONT, flexWrap: "wrap" }}>
                      You are chatting with:
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 5, backgroundColor: "#f3f4f6", borderRadius: 999, padding: "2px 10px 2px 5px" }}>
                        <div style={{ width: 18, height: 18, borderRadius: "50%", backgroundColor: PURPLE, display: "flex", alignItems: "center", justifyContent: "center" }}>
                          <RoleIcon size={10} color="#fff" strokeWidth={2.2} />
                        </div>
                        <span style={{ fontWeight: 600, color: "#111827", fontSize: accessibilityMode ? 14 : 13 }}>{activeChat.role}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div style={{ flex: 1, overflowY: "auto", padding: "22px 28px" }}>
                {activeChat.messages.map((msg, i) => (
                  <Bubble key={i} msg={msg} RoleIcon={RoleIcon} fontSize={A11Y.bubbleFontSize}
                    onRetry={msg.role === "assistant" ? () => retryMessage(i) : undefined}
                    onFeedback={msg.role === "assistant" ? (val) => setMessageFeedback(i, val) : undefined}
                  />
                ))}
                <div ref={bottomRef} />
              </div>
              <InputPanel {...inputPanelProps} />
            </>
          ) : (
            <>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "20px", textAlign: "center" }}>
                <img src="/airplane.png" alt="Persona Weave" style={{ width: 111, height: 111, marginBottom: 22, objectFit: "contain" }} />
                <h1 style={{ fontSize: accessibilityMode ? 44 : 40, fontWeight: 700, color: "#111827", margin: "0 0 8px", fontFamily: FONT }}>Hello, User!</h1>
                <p style={{ fontSize: accessibilityMode ? 19 : 17, color: "#6b7280", margin: 0, fontFamily: FONT }}>Welcome to Persona Weave.</p>
              </div>
              <InputPanel {...inputPanelProps} />
            </>
          )}
        </main>
      </div>
    </div>
  );
}