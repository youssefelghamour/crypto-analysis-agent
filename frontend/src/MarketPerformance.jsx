import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./MarketPerformance.css";



const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ASSET_COLORS = {
  bitcoin: "#040401",
  ethereum: "#a9a9a9",
  solana: "#25b09b",
  ripple: "#6297f9",
};

const ASSET_NAMES = {
  bitcoin: "BTC",
  ethereum: "ETH",
  solana: "SOL",
  ripple: "XRP",
};

function MarketPerformance() {
    const [assets, setAssets] = useState([]);
    const [selectedAssets, setSelectedAssets] = useState([
        "bitcoin",
        "ethereum",
        "solana",
        "ripple",
    ]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;

        async function fetchHistory() {
            try {
                const response = await fetch(`${API_URL}/market/history`);

                if (!response.ok) {
                    throw new Error("Unable to load historical market data.");
                }

                const data = await response.json();

                if (active) {
                    setAssets(data.assets);
                    setError("");
                }
            } catch (err) {
                if (active) {
                    setError(err.message);
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        fetchHistory();

        const interval = setInterval(fetchHistory, 300_000);

        return () => {
            active = false;
            clearInterval(interval);
        };
    }, []);

    const chartData = useMemo(() => {
        if (assets.length === 0) return [];

        // Find the shortest price array from all coins so all coins have matching indexes
        // to determine the number of points on the chart's X-axis
        const pointCount = Math.min(
            ...assets.map((asset) => asset.prices.length)
        );

        // A list of points
        const chartPoints = [];

        // For each timestamp, we create a point for the graph:
        // {
        //      timestamp: 1795718400000,
        //      bitcoin: 2.5,
        //      ethereum: -1.3,
        //      solana: 4.8,
        //      ripple: 0.7
        //  }
        for (let index = 0; index < pointCount; index++) {
            // Each X-axis point is a timestamp
            const point = {
                timestamp: assets[0].prices[index].timestamp,
            };

            // Add percentage change of every coin per time stamp
            for (const asset of assets) {
                point[asset.id] = asset.prices[index].change_pct;
            }

            chartPoints.push(point);
        }

        return chartPoints;
    }, [assets]);

    function toggleAsset(assetId) {
        setSelectedAssets((current) =>
            current.includes(assetId)
                ? current.filter((id) => id !== assetId)
                : [...current, assetId]
        );
    }

    function formatDate(timestamp) {
        return new Date(timestamp).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
        });
    }

    if (loading) {
        return (
            <section className="performance-section">
                <div className="section-heading">
                    <h3>Market performance</h3>
                    <span>7-day overview</span>
                </div>
                <p className="performance-status">Loading historical data...</p>
            </section>
        );
    }

    if (error || assets.length === 0) {
        return (
            <section className="performance-section">
                <div className="section-heading">
                    <h3>Market performance</h3>
                    <span>7-day overview</span>
                </div>
                <p className="performance-status">
                    {error || "Historical data unavailable."}
                </p>
            </section>
        );
    }

    return (
        <section className="performance-section">
            <div className="section-heading">
                <h3>Market performance</h3>
                <span>7-day overview</span>
            </div>

            <div className="performance-card">
                <div className="performance-toolbar">
                    <div className="performance-description">
                        <strong>Price performance</strong>
                        <span>Percentage change from the start of the period</span>
                    </div>

                    <div className="asset-filters">
                        {assets.map((asset) => {
                            const active = selectedAssets.includes(asset.id);

                            return (
                                <button
                                    key={asset.id}
                                    type="button"
                                    className={`asset-filter ${active ? "active" : ""}`}
                                    style={{
                                        "--asset-color": ASSET_COLORS[asset.id],
                                    }}
                                    onClick={() => toggleAsset(asset.id)}
                                >
                                    <span className="filter-dot" />
                                    {ASSET_NAMES[asset.id]}
                                </button>
                            );
                        })}
                    </div>
                </div>


                <div className="performance-layout">
                    <div className="performance-sidebar">
                        <strong>Assets</strong>

                        {assets.map((asset) => (
                            <div className="performance-asset" key={asset.id}>
                                <span>{ASSET_NAMES[asset.id]}</span>
                                <strong>
                                    {asset.prices.at(-1).change_pct > 0 ? "+" : ""}
                                    {asset.prices.at(-1).change_pct.toFixed(2)}%
                                </strong>
                            </div>
                        ))}
                    </div>

                    <div className="performance-chart">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                                data={chartData}
                                margin={{ top: 12, right: 12, left: 0, bottom: 0 }}
                            >

                                
                                <CartesianGrid
                                    stroke="#edf0f3"
                                    vertical={false}
                                    strokeDasharray="3 3"
                                />

                                <XAxis
                                    dataKey="timestamp"
                                    tickFormatter={formatDate}
                                    tick={{ fill: "#8993a2", fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                    minTickGap={35}
                                />

                                <YAxis
                                    tickFormatter={(value) => `${value}%`}
                                    tick={{ fill: "#8993a2", fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                    width={48}
                                />

                                <Tooltip
                                    labelFormatter={(timestamp) =>
                                        new Date(timestamp).toLocaleString("en-US", {
                                            month: "short",
                                            day: "numeric",
                                            hour: "2-digit",
                                            minute: "2-digit",
                                        })
                                    }
                                    formatter={(value, name) => [
                                        `${value.toFixed(2)}%`,
                                        ASSET_NAMES[name] || name,
                                    ]}
                                    contentStyle={{
                                        border: "1px solid #e5e9ef",
                                        borderRadius: "8px",
                                        fontSize: "12px",
                                        fontWeight: "bold",
                                        boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                                    }}
                                />

                                {assets
                                    .filter((asset) => selectedAssets.includes(asset.id))
                                    .map((asset) => (
                                    <Line
                                        key={asset.id}
                                        type="monotone"
                                        dataKey={asset.id}
                                        name={asset.id}
                                        stroke={ASSET_COLORS[asset.id]}
                                        strokeWidth={2.2}
                                        dot={false}
                                        activeDot={{ r: 4, strokeWidth: 0 }}
                                        connectNulls
                                    />
                                    ))
                                }
                            
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="performance-summary">
                        <strong>7D price range</strong>

                        {assets.map((asset) => {
                            const prices = asset.prices.map((point) => point.price_usd);

                            return (
                                <div className="summary-item" key={asset.id}>
                                    <span>{ASSET_NAMES[asset.id]}</span>
                                    <strong>
                                        ${Math.min(...prices).toLocaleString("en-US", {
                                            maximumFractionDigits: 2,
                                        })}
                                        {" – "}
                                        ${Math.max(...prices).toLocaleString("en-US", {
                                            maximumFractionDigits: 2,
                                        })}
                                    </strong>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </section>
    );
}

export default MarketPerformance;
