import { useState, useRef, useEffect } from "react";
import type { Thread } from "../api";
import { deleteThread, renameThread } from "../api";
import styles from "./ThreadSidebar.module.css";

interface Props {
  threads: Thread[];
  activeThreadId: string | null;
  onSelectThread: (id: string) => void;
  onNewThread: () => void;
  onDeleteThread: (id: string) => void;
  onRenameThread: (id: string, title: string) => void;
}

export default function ThreadSidebar({
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  onDeleteThread,
  onRenameThread,
}: Props) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [menuId, setMenuId] = useState<string | null>(null);
  const editRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingId && editRef.current) editRef.current.focus();
  }, [editingId]);

  const startRename = (t: Thread) => {
    setEditingId(t.id);
    setEditTitle(t.title);
    setMenuId(null);
  };

  const commitRename = async () => {
    if (!editingId) return;
    const trimmed = editTitle.trim();
    if (trimmed) {
      await renameThread(editingId, trimmed);
      onRenameThread(editingId, trimmed);
    }
    setEditingId(null);
  };

  const handleDelete = async (id: string) => {
    setMenuId(null);
    await deleteThread(id);
    onDeleteThread(id);
  };

  return (
    <aside className={styles.sidebar}>
      {/* Brand header */}
      <div className={styles.brand}>
        <div className={styles.brandMark}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="3" fill="var(--accent)" />
            <circle cx="12" cy="12" r="7" stroke="var(--accent)" strokeWidth="1.5" opacity="0.4" />
            <circle cx="12" cy="12" r="11" stroke="var(--accent)" strokeWidth="1" opacity="0.15" />
          </svg>
        </div>
        <div className={styles.brandText}>
          <span className={styles.brandName}>Deep Agent</span>
          <span className={styles.brandTag}>synaptic command</span>
        </div>
      </div>

      {/* New thread button */}
      <button className={styles.newThread} onClick={onNewThread}>
        <span className={styles.newIcon}>+</span>
        <span>New Thread</span>
      </button>

      {/* Thread list */}
      <div className={styles.threadList}>
        {threads.length === 0 && (
          <div className={styles.empty}>
            <p className={styles.emptyText}>No conversations yet</p>
            <p className={styles.emptyHint}>Start one above</p>
          </div>
        )}
        {threads.map((t) => (
          <div
            key={t.id}
            className={`${styles.thread} ${
              t.id === activeThreadId ? styles.active : ""
            }`}
          >
            <button
              className={styles.threadBtn}
              onClick={() => onSelectThread(t.id)}
            >
              <span className={styles.threadDot} />
              <div className={styles.threadInfo}>
                {editingId === t.id ? (
                  <input
                    ref={editRef}
                    className={styles.renameInput}
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={commitRename}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commitRename();
                      if (e.key === "Escape") setEditingId(null);
                    }}
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <span className={styles.threadTitle}>{t.title}</span>
                )}
                <span className={styles.threadTime}>
                  {new Date(t.created_at).toLocaleDateString()}
                </span>
              </div>
            </button>

            {/* Context menu trigger */}
            <button
              className={styles.menuBtn}
              onClick={(e) => {
                e.stopPropagation();
                setMenuId(menuId === t.id ? null : t.id);
              }}
              aria-label="Thread options"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="5" r="2" />
                <circle cx="12" cy="12" r="2" />
                <circle cx="12" cy="19" r="2" />
              </svg>
            </button>

            {/* Context menu */}
            {menuId === t.id && (
              <div className={styles.contextMenu}>
                <button
                  className={styles.menuItem}
                  onClick={() => startRename(t)}
                >
                  Rename
                </button>
                <button
                  className={`${styles.menuItem} ${styles.menuDanger}`}
                  onClick={() => handleDelete(t.id)}
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className={styles.footer}>
        <div className={styles.footerPill}>
          <span className={styles.footerDot} />
          <span className={styles.footerText}>8 agents</span>
        </div>
        <div className={styles.footerPill}>
          <span className={styles.footerDotMemory} />
          <span className={styles.footerText}>long-term memory</span>
        </div>
      </div>
    </aside>
  );
}
