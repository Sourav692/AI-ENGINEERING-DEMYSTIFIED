import { useState, useEffect, useCallback, useRef } from "react";
import "./App.css";
import ThreadSidebar from "./components/ThreadSidebar";
import ChatArea from "./components/ChatArea";
import type { ChatMessage } from "./components/ChatArea";
import MemoryPanel from "./components/MemoryPanel";
import AgentTopology from "./components/AgentTopology";
import ExecutionGraph from "./components/ExecutionGraph";
import type { ExecutionTrace, ExecNode, ExecEdge } from "./components/ExecutionGraph";
import ToastContainer from "./components/Toast";
import type { ToastData } from "./components/Toast";
import type { Thread, Memory } from "./api";
import {
  createThread,
  listThreads,
  listMemories,
  getThreadMessages,
  streamChat,
} from "./api";

function App() {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messagesByThread, setMessagesByThread] = useState<
    Record<string, ChatMessage[]>
  >({});
  const [memories, setMemories] = useState<Memory[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [memoryOpen, setMemoryOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [execTrace, setExecTrace] = useState<ExecutionTrace>({ nodes: [], edges: [] });

  // Mutable ref to build the trace during streaming without triggering
  // re-renders on every intermediate step — we flush to state via rAF.
  const traceRef = useRef<{
    nodes: Map<string, ExecNode>;
    edges: Set<string>;
    edgeList: ExecEdge[];
    lastNodeId: string | null;
    lastAgentId: string | null;
    dirty: boolean;
    rafId: number | null;
  }>({
    nodes: new Map(),
    edges: new Set(),
    edgeList: [],
    lastNodeId: null,
    lastAgentId: null,
    dirty: false,
    rafId: null,
  });

  // Throttled flush: only updates React state once per animation frame
  const scheduleFlush = useCallback(() => {
    const t = traceRef.current;
    t.dirty = true;
    if (t.rafId !== null) return; // already scheduled
    t.rafId = requestAnimationFrame(() => {
      t.rafId = null;
      if (t.dirty) {
        t.dirty = false;
        setExecTrace({
          nodes: Array.from(t.nodes.values()),
          edges: [...t.edgeList],
        });
      }
    });
  }, []);

  const resetTrace = useCallback(() => {
    const t = traceRef.current;
    if (t.rafId !== null) cancelAnimationFrame(t.rafId);
    traceRef.current = {
      nodes: new Map(),
      edges: new Set(),
      edgeList: [],
      lastNodeId: null,
      lastAgentId: null,
      dirty: false,
      rafId: null,
    };
    setExecTrace({ nodes: [], edges: [] });
  }, []);

  const addTraceNode = useCallback(
    (node: ExecNode, parentId?: string) => {
      const t = traceRef.current;
      if (t.nodes.has(node.id)) {
        t.nodes.set(node.id, { ...t.nodes.get(node.id)!, status: node.status });
      } else {
        t.nodes.set(node.id, node);
      }
      if (parentId) {
        const edgeKey = `${parentId}->${node.id}`;
        if (!t.edges.has(edgeKey)) {
          t.edges.add(edgeKey);
          t.edgeList.push({ from: parentId, to: node.id });
        }
      }
      scheduleFlush();
    },
    [scheduleFlush]
  );

  const completeTraceNode = useCallback(
    (nodeId: string) => {
      const t = traceRef.current;
      const existing = t.nodes.get(nodeId);
      if (existing) {
        t.nodes.set(nodeId, { ...existing, status: "complete" });
        scheduleFlush();
      }
    },
    [scheduleFlush]
  );

  const addToast = useCallback(
    (message: string, type: ToastData["type"] = "error") => {
      const id = `toast-${Date.now()}-${Math.random()}`;
      setToasts((prev) => [...prev, { id, message, type }]);
    },
    []
  );

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  useEffect(() => {
    listThreads().then(setThreads).catch(() => {});
    refreshMemories();
  }, []);

  const refreshMemories = useCallback(() => {
    listMemories().then(setMemories).catch(() => {});
  }, []);

  const handleNewThread = useCallback(async () => {
    try {
      const thread = await createThread("New Chat");
      setThreads((prev) => [thread, ...prev]);
      setActiveThreadId(thread.id);
      resetTrace();
    } catch {
      addToast("Failed to create thread");
    }
  }, [addToast, resetTrace]);

  const handleSelectThread = useCallback(
    async (id: string) => {
      setActiveThreadId(id);
      resetTrace();

      if (!messagesByThread[id] || messagesByThread[id].length === 0) {
        setLoadingHistory(true);
        try {
          const history = await getThreadMessages(id);
          if (history.length > 0) {
            const msgs: ChatMessage[] = history.map((h, i) => ({
              id: `hist-${i}-${Date.now()}`,
              role:
                h.role === "assistant"
                  ? "assistant"
                  : h.role === "tool"
                    ? "tool"
                    : "user",
              content: h.content,
              node: h.node,
              toolCalls: h.tool_calls,
            }));
            setMessagesByThread((prev) => ({
              ...prev,
              [id]: msgs,
            }));
          }
        } catch {
          // Silently fail
        } finally {
          setLoadingHistory(false);
        }
      }
    },
    [messagesByThread, resetTrace]
  );

  const handleDeleteThread = useCallback(
    (id: string) => {
      setThreads((prev) => prev.filter((t) => t.id !== id));
      setMessagesByThread((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
      if (activeThreadId === id) {
        setActiveThreadId(null);
        resetTrace();
      }
      addToast("Thread deleted", "info");
    },
    [activeThreadId, addToast, resetTrace]
  );

  const handleRenameThread = useCallback((id: string, title: string) => {
    setThreads((prev) =>
      prev.map((t) => (t.id === id ? { ...t, title } : t))
    );
  }, []);

  const currentMessages = activeThreadId
    ? messagesByThread[activeThreadId] || []
    : [];

  const handleSend = useCallback(
    async (message: string) => {
      let threadId = activeThreadId;

      if (!threadId) {
        try {
          const thread = await createThread(message.slice(0, 50));
          setThreads((prev) => [thread, ...prev]);
          threadId = thread.id;
          setActiveThreadId(threadId);
        } catch {
          addToast("Failed to create thread");
          return;
        }
      }

      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
      };

      setMessagesByThread((prev) => ({
        ...prev,
        [threadId!]: [...(prev[threadId!] || []), userMsg],
      }));

      // Reset and initialize execution trace
      resetTrace();
      const startId = "start";
      addTraceNode({ id: startId, label: "User Input", type: "start", status: "complete" });

      setIsStreaming(true);
      setActiveAgent(null);

      let assistantContent = "";
      let currentNode = "";
      let assistantId = `ai-${Date.now()}`;

      try {
        for await (const event of streamChat(message, threadId)) {
          if (event.type === "done") break;
          if (event.type === "error") {
            addToast(event.content || "Agent error");
            break;
          }

          // Track agent/node transitions for the DAG
          if (event.node && event.node !== currentNode) {
            // Complete previous agent node
            if (currentNode) {
              completeTraceNode(`agent-${currentNode}`);
            }
            currentNode = event.node;
            setActiveAgent(currentNode);

            const agentId = `agent-${currentNode}`;
            const t = traceRef.current;
            // Connect to parent: either the last tool, or start node
            const parentId = t.lastNodeId || startId;
            addTraceNode(
              { id: agentId, label: currentNode, type: "agent", status: "active" },
              parentId
            );
            t.lastAgentId = agentId;
            t.lastNodeId = agentId;
          }

          if (event.type === "ai" && event.content) {
            assistantContent += event.content;

            setMessagesByThread((prev) => {
              const msgs = prev[threadId!] || [];
              const existing = msgs.find((m) => m.id === assistantId);
              if (existing) {
                return {
                  ...prev,
                  [threadId!]: msgs.map((m) =>
                    m.id === assistantId
                      ? {
                          ...m,
                          content: assistantContent,
                          node: currentNode,
                          toolCalls: event.tool_calls,
                        }
                      : m
                  ),
                };
              } else {
                return {
                  ...prev,
                  [threadId!]: [
                    ...msgs,
                    {
                      id: assistantId,
                      role: "assistant",
                      content: assistantContent,
                      node: currentNode,
                      toolCalls: event.tool_calls,
                    },
                  ],
                };
              }
            });
          } else if (event.type === "tool" && event.content) {
            const toolMsg: ChatMessage = {
              id: `tool-${Date.now()}-${Math.random()}`,
              role: "tool",
              content: event.content,
              node: currentNode,
            };
            setMessagesByThread((prev) => ({
              ...prev,
              [threadId!]: [...(prev[threadId!] || []), toolMsg],
            }));

            // Mark latest tool nodes as complete
            const t = traceRef.current;
            for (const [id, node] of t.nodes) {
              if (node.type === "tool" && node.status === "active") {
                completeTraceNode(id);
              }
            }
          } else if (
            event.type === "ai" &&
            event.tool_calls &&
            event.tool_calls.length > 0 &&
            !event.content
          ) {
            // Track tool calls in the DAG
            const t = traceRef.current;
            for (const tc of event.tool_calls) {
              const toolKey = `${currentNode}-${tc.name}`;
              // Deduplicate: use a counter for repeat calls of same tool
              let toolId = `tool-${toolKey}`;
              if (t.nodes.has(toolId)) {
                let count = 2;
                while (t.nodes.has(`${toolId}-${count}`)) count++;
                toolId = `${toolId}-${count}`;
              }
              const parentId = t.lastAgentId || startId;
              addTraceNode(
                { id: toolId, label: tc.name, type: "tool", status: "active" },
                parentId
              );
              t.lastNodeId = toolId;

              const statusMsg: ChatMessage = {
                id: `status-${Date.now()}-${Math.random()}`,
                role: "status",
                content: `Calling ${tc.name}...`,
                node: currentNode,
              };
              setMessagesByThread((prev) => ({
                ...prev,
                [threadId!]: [...(prev[threadId!] || []), statusMsg],
              }));
            }
            assistantContent = "";
            assistantId = `ai-${Date.now()}-${Math.random()}`;
          }
        }
      } catch (err) {
        addToast(
          err instanceof Error ? err.message : "Connection failed"
        );
      } finally {
        // Complete all remaining nodes and add end node (sync flush)
        const t = traceRef.current;
        for (const [, node] of t.nodes) {
          if (node.status === "active") {
            t.nodes.set(node.id, { ...node, status: "complete" });
          }
        }
        const endParent = t.lastNodeId || startId;
        const endNode: ExecNode = { id: "end", label: "Response", type: "end", status: "complete" };
        t.nodes.set(endNode.id, endNode);
        const edgeKey = `${endParent}->end`;
        if (!t.edges.has(edgeKey)) {
          t.edges.add(edgeKey);
          t.edgeList.push({ from: endParent, to: "end" });
        }
        // Cancel any pending rAF and do a final sync flush
        if (t.rafId !== null) cancelAnimationFrame(t.rafId);
        t.rafId = null;
        setExecTrace({
          nodes: Array.from(t.nodes.values()),
          edges: [...t.edgeList],
        });

        setIsStreaming(false);
        setActiveAgent(null);
        refreshMemories();
      }
    },
    [activeThreadId, refreshMemories, addToast, resetTrace, addTraceNode, completeTraceNode]
  );

  return (
    <div className="app">
      <div className="leftPanel">
        <ThreadSidebar
          threads={threads}
          activeThreadId={activeThreadId}
          onSelectThread={handleSelectThread}
          onNewThread={handleNewThread}
          onDeleteThread={handleDeleteThread}
          onRenameThread={handleRenameThread}
        />
        <ExecutionGraph trace={execTrace} isStreaming={isStreaming} />
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          flex: 1,
          minWidth: 0,
          minHeight: 0,
          position: "relative",
          zIndex: 1,
        }}
      >
        <AgentTopology activeAgent={activeAgent} isStreaming={isStreaming} />
        <ChatArea
          messages={currentMessages}
          isStreaming={isStreaming}
          onSend={handleSend}
          activeAgent={activeAgent}
          loadingHistory={loadingHistory}
        />
      </div>
      <MemoryPanel
        memories={memories}
        onRefresh={refreshMemories}
        isOpen={memoryOpen}
        onToggle={() => setMemoryOpen((o) => !o)}
      />
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}

export default App;
