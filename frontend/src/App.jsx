import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";
import MarketTicker from "./MarketTicker";
import MarketWatch from "./MarketWatch";
import MarketPerformance from "./MarketPerformance";


const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function createThreadId() {
  return crypto.randomUUID();
}

function normalizeMarkdown(content) {
  // Sometimes the LLM returns escaped markdown with backslashes
  // This function removes any backlash that comes before * _ ~ | used to skip them (\* to *)
  return content.replace(/\\([*_~|])/g, "$1");
}

function formatPrice(value) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        notation: "compact",
        maximumFractionDigits: 2,
    }).format(value);
}


function App() {
  const [threadId, setThreadId] = useState(() => {
    return localStorage.getItem("crypto-agent-thread-id") || createThreadId();
  });

  const [messages, setMessages] = useState(() => {
    const savedThreadId = localStorage.getItem("crypto-agent-thread-id");
    if (!savedThreadId) return [];

    try {
      return JSON.parse(
        localStorage.getItem(`crypto-agent-messages-${savedThreadId}`) || "[]"
      );
    } catch {
      return [];
    }
  });

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  // Controls which page is displayed: overview (main page), discussion, report and analysis
  const [activePage, setActivePage] = useState("overview");

  const [globalStats, setGlobalStats] = useState(null);

  useEffect(() => {
    // saves thread id and messages to localStorage whenever either changes
    localStorage.setItem("crypto-agent-thread-id", threadId);
    localStorage.setItem(
      `crypto-agent-messages-${threadId}`,
      JSON.stringify(messages)
    );
  }, [threadId, messages]);


  useEffect(() => {
    let active = true;

    async function fetchGlobalStats() {
        try {
          const response = await fetch(`${API_URL}/market/global`);

          if (!response.ok) {
            throw new Error("Failed to fetch global market data");
          }

          const data = await response.json();

          if (active) {
            setGlobalStats(data);
          }
        } catch (error) {
          console.error("Global market data error:", error);
        }
    }

    fetchGlobalStats();

    const interval = setInterval(fetchGlobalStats, 300_000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);


  async function sendMessage(event) {
    event.preventDefault();

    const message = input.trim();
    if (!message || loading) return;

    setInput("");
    // Adds the user message to the UI
    setMessages((current) => [...current, { role: "user", content: message }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, thread_id: threadId }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();

      // Adds the assistant response with its intent
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.response,
          intent: data.intent,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: "error", content: error.message || "Something went wrong." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    if (loading) return;
    setThreadId(createThreadId());
    setMessages([]);
    setActivePage("discussion");
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">₿</div>
          <div>
            <strong>Crypto Analysis Agent</strong>
            <span></span>
          </div>
        </div>

        <span className="nav-label">WORKSPACE</span>

        <nav className="navigation">
          <button
            className={activePage === "overview" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("overview")}
          >
            <span>▦</span> Overview
          </button>

          <button
            className={activePage === "analysis" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("analysis")}
          >
            <span>⌁</span> Market analysis
          </button>

          <button
            className={activePage === "reports" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("reports")}
          >
            <span>▤</span> Reports
          </button>

          <button
            className={activePage === "discussion" ? "nav-item active" : "nav-item"}
            onClick={() => setActivePage("discussion")}
          >
            <span>◌</span> Discussion
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button className="new-chat-button" onClick={startNewChat}>
            + New discussion
          </button>
          <div className="sidebar-footer">
            <span className="status-dot" />
            AI research assistant
          </div>
        </div>
      </aside>

      <main className="main">
        <MarketTicker />
        <header className="topbar">
          <div>
            <span className="breadcrumb">WORKSPACE / {activePage.toUpperCase()}</span>
            <h1>
              {activePage === "overview" && "Market overview"}
              {activePage === "analysis" && "Market analysis"}
              {activePage === "reports" && "Research reports"}
              {activePage === "discussion" && "Discussion"}
            </h1>
          </div>
          <div className="topbar-right">
            <span className="live-indicator" /> Research workspace
          </div>
        </header>

        {activePage === "overview" && (
          <section className="dashboard-content">
            <div className="page-intro">

              <div className="global-market-stats">
                <div className="global-stat">
                  <span>Total Market Cap</span>
                  <strong>
                    {globalStats
                        ? formatPrice(globalStats.total_market_cap_usd)
                        : "—"}
                  </strong>
                </div>

                <div className="global-stat">
                  <span>24h Trading Volume</span>
                  <strong>
                    {globalStats
                        ? formatPrice(globalStats.total_volume_24h_usd)
                        : "—"}
                  </strong>
                </div>

                <div className="global-stat">
                    <span>BTC Dominance</span>
                    <strong>
                      {globalStats
                          ? `${globalStats.btc_dominance_pct.toFixed(2)}%`
                          : "—"}
                    </strong>
                </div>
              </div>

              <button
                className="primary-button"
                onClick={() => setActivePage("discussion")}
              >
                Start analysis
              </button>
            </div>

            <div className="research-section">
              <div className="section-heading">
                <h3>Research workspace</h3>
                <span>AI-powered analysis</span>
              </div>

              <div className="research-grid">
                <button className="research-card" onClick={() => setActivePage("discussion")}>
                  <span className="research-icon">↗</span>
                  <strong>Generate a market report</strong>
                  <p>Explore a cryptocurrency's performance, metrics, news and risks.</p>
                  <span className="card-action">Start research →</span>
                </button>

                <button className="research-card" onClick={() => setActivePage("discussion")}>
                  <span className="research-icon">⌕</span>
                  <strong>Discuss the market</strong>
                  <p>Ask questions, compare assets and explore market developments.</p>
                  <span className="card-action">Open discussion →</span>
                </button>
              </div>
            </div>

            <MarketWatch
              onSelectAsset={(asset) => {
                setInput(
                  `Analyze ${asset.name} (${asset.symbol}) and its current market conditions.`
                );
                setActivePage("discussion");
              }}
            />

            <MarketPerformance />
          </section>
        )}

        {activePage === "discussion" && (
          <section className="discussion-content">
            <div className="messages-container">
              <div className="messages">
                {messages.length === 0 ? (
                  <div className="discussion-welcome">
                    <span className="eyebrow">RESEARCH ASSISTANT</span>
                    <h2>What are we researching today?</h2>
                    <p>Generate cryptocurrency reports or discuss market developments.</p>
                    <div className="suggestions">
                      <button onClick={() => setInput("Generate a 7-day Bitcoin market report")}>
                        Generate a Bitcoin report →
                      </button>
                      <button onClick={() => setInput("Compare Bitcoin and Ethereum")}>
                        Compare Bitcoin and Ethereum →
                      </button>
                    </div>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div className={`message-row ${message.role}`} key={index}>
                      <div className="message">
                        {message.role === "assistant" && message.intent && (
                          <span className="message-intent">{message.intent}</span>
                        )}
                        {typeof message.content === "string" ? (
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {normalizeMarkdown(message.content)}
                          </ReactMarkdown>
                        ) : (
                          <pre>{JSON.stringify(message.content, null, 2)}</pre>
                        )}
                      </div>
                    </div>
                  ))
                )}

                {loading && (
                  <div className="message-row assistant">
                    <div className="message loading-message">Analyzing market data...</div>
                  </div>
                )}
              </div>
            </div>

            <form className="input-area" onSubmit={sendMessage}>
              <textarea
                value={input}
                onChange={(event) => {
                  setInput(event.target.value);
                  event.target.style.height = "28px";
                  event.target.style.height = `${Math.min(event.target.scrollHeight, 120)}px`;
                }}
                placeholder="Ask a question or request a market report..."
                rows={1}
                disabled={loading}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage(event);
                  }
                }}
              />
              <button type="submit" disabled={loading || !input.trim()}>
                {loading ? "..." : "Send"}
              </button>
            </form>
          </section>
        )}

        {(activePage === "analysis" || activePage === "reports") && (
          <section className="empty-workspace">
            <span className="eyebrow">COMING NEXT</span>
            <h2>{activePage === "analysis" ? "Market analysis" : "Research reports"}</h2>
            <p>
              {activePage === "analysis"
                ? "Your market analysis workspace will be built here."
                : "Your generated research reports will be organized here."}
            </p>
            <button className="primary-button" onClick={() => setActivePage("discussion")}>
              Open discussion →
            </button>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
