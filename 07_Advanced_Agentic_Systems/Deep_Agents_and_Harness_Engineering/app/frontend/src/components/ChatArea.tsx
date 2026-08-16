import { useRef, useEffect, useState } from "react";
import styles from "./ChatArea.module.css";
import MarkdownRenderer from "./MarkdownRenderer";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "tool" | "status";
  content: string;
  node?: string;
  toolCalls?: { name: string; args: Record<string, unknown> }[];
}

interface Props {
  messages: ChatMessage[];
  isStreaming: boolean;
  onSend: (message: string) => void;
  activeAgent: string | null;
  loadingHistory?: boolean;
}

export default function ChatArea({
  messages,
  isStreaming,
  onSend,
  activeAgent,
  loadingHistory,
}: Props) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!isStreaming) inputRef.current?.focus();
  }, [isStreaming]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  };

  return (
    <div className={styles.chatArea}>
      {/* Messages */}
      <div className={styles.messages}>
        {loadingHistory && (
          <div className={styles.loadingHistory}>
            <div className={styles.typingDots}>
              <span className={styles.dot} style={{ animationDelay: "0s" }} />
              <span className={styles.dot} style={{ animationDelay: "0.15s" }} />
              <span className={styles.dot} style={{ animationDelay: "0.3s" }} />
            </div>
            <span className={styles.loadingText}>Loading history...</span>
          </div>
        )}
        {messages.length === 0 && !loadingHistory && (
          <div className={styles.welcome}>
            <div className={styles.welcomeOrb}>
              <div className={styles.orbInner} />
              <div className={styles.orbRing} />
              <div className={styles.orbRingOuter} />
            </div>
            <h1 className={styles.welcomeTitle}>Deep Agent</h1>
            <p className={styles.welcomeDesc}>
              Multi-agent orchestrator with persistent memory.
              <br />
              8 specialized agents at your command.
            </p>
            <div className={styles.capabilities}>
              <div className={styles.capGroup}>
                <span className={styles.capDot} style={{ background: "var(--accent)" }} />
                <span className={styles.capLabel}>Code</span>
              </div>
              <div className={styles.capGroup}>
                <span className={styles.capDot} style={{ background: "var(--memory)" }} />
                <span className={styles.capLabel}>Memory</span>
              </div>
              <div className={styles.capGroup}>
                <span className={styles.capDot} style={{ background: "var(--warning)" }} />
                <span className={styles.capLabel}>Research</span>
              </div>
              <div className={styles.capGroup}>
                <span className={styles.capDot} style={{ background: "var(--agent-active)" }} />
                <span className={styles.capLabel}>Analytics</span>
              </div>
            </div>
            <div className={styles.starters}>
              {[
                "Build a Python CLI tool for CSV parsing",
                "What do you remember about me?",
                "Analyze our customer retention metrics",
              ].map((s) => (
                <button
                  key={s}
                  className={styles.starter}
                  onClick={() => onSend(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages
          .filter((msg) => msg.role !== "tool")
          .map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${styles[msg.role]}`}
          >
            {msg.role === "user" ? (
              <div className={styles.userBubble}>
                <div className={styles.userAvatar}>U</div>
                <div className={styles.userContent}>
                  <p>{msg.content}</p>
                </div>
              </div>
            ) : msg.role === "status" ? (
              <div className={styles.statusBubble}>
                <span className={styles.statusGear}>⚙</span>
                <span className={styles.statusText}>{msg.content}</span>
              </div>
            ) : (
              <div className={styles.aiBubble}>
                <div className={styles.aiGutter}>
                  <div className={styles.aiAvatar}>
                    <span className={styles.robotEmoji}>🤖</span>
                  </div>
                </div>
                <div className={styles.aiBody}>
                  <div className={styles.aiContent}>
                    <MarkdownRenderer content={msg.content} />
                  </div>
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className={styles.toolCallsRow}>
                      {msg.toolCalls.map((tc, i) => (
                        <span key={i} className={styles.toolCallChip}>
                          <span className={styles.toolCallGear}>⚙</span> {tc.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}

        {isStreaming && (
          <div className={styles.typingRow}>
            {activeAgent && (
              <span className={styles.typingAgent}>{activeAgent}</span>
            )}
            <div className={styles.typingDots}>
              <span className={styles.dot} style={{ animationDelay: "0s" }} />
              <span className={styles.dot} style={{ animationDelay: "0.15s" }} />
              <span className={styles.dot} style={{ animationDelay: "0.3s" }} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className={styles.inputArea}>
        <form className={styles.inputForm} onSubmit={handleSubmit}>
          <div className={styles.inputShell}>
            <textarea
              ref={inputRef}
              className={styles.input}
              value={input}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder="Message Deep Agent..."
              rows={1}
              disabled={isStreaming}
            />
            <button
              type="submit"
              className={styles.sendBtn}
              disabled={isStreaming || !input.trim()}
              aria-label="Send message"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M8 14V2M8 2L3 7M8 2L13 7"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
          <p className={styles.inputHint}>
            Enter to send &middot; Shift+Enter for new line
          </p>
        </form>
      </div>
    </div>
  );
}
