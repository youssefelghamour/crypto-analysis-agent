import { useEffect, useState } from "react";
import "./MarketWatch.css";


const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function formatPrice(price) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: price < 1 ? 6 : 2,
    }).format(price);
}

function MarketWatch({ onSelectAsset }) {
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let active = true;

        async function fetchMarketData() {
            try {
                const response = await fetch(`${API_URL}/market/ticker`);

                if (!response.ok) {
                    throw new Error("Failed to fetch market data");
                }

                const data = await response.json();

                if (active) {
                    setAssets(data.assets.slice(0,8));
                }
            } catch (error) {
                console.error("Market watch error:", error);
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        fetchMarketData();

        // runs the function again every minute
        const interval = setInterval(fetchMarketData, 60_000);

        return () => {
            active = false;
            clearInterval(interval);
        };
    }, []);

    return (
        <div className="market-section">
            <div className="section-heading">
                <h3>Market watch</h3>
                <span>Featured assets</span>
            </div>

            <div className="market-grid">
                {loading && assets.length === 0 ? (
                    <p className="market-status">Loading market data...</p>
                ) : assets.length === 0 ? (
                    <p className="market-status">Market data unavailable.</p>
                ) : (
                    assets.map((asset) => {
                        const isPositive = asset.change_24h > 0;
                        const isNegative = asset.change_24h < 0;

                        return (
                            <button
                                className="market-card"
                                key={asset.id}
                                onClick={() => onSelectAsset(asset)}
                                type="button"
                            >
                                <div className="asset-heading">
                                    <img
                                        className="asset-logo"
                                        src={asset.image}
                                        alt=""
                                    />

                                    <div className="asset-identity">
                                        <strong>{asset.name}</strong>
                                        <span>{asset.symbol}</span>
                                    </div>

                                    <span
                                        className={`asset-change ${
                                            isPositive
                                                ? "positive"
                                                : isNegative
                                                ? "negative"
                                                : "neutral"
                                            }`
                                        }
                                    >
                                        {asset.change_24h == null
                                            ? "—"
                                            : `${isPositive ? "+" : ""}${asset.change_24h.toFixed(2)}%`
                                        }
                                    </span>
                                </div>

                                <div className="asset-details">
                                    <strong className="asset-price">
                                        {formatPrice(asset.price_usd)}
                                    </strong>

                                    <span className="asset-action">
                                        Discuss currency
                                    </span>
                                </div>
                            </button>
                        );
                    })
                )}
            </div>
        </div>
    );
}

export default MarketWatch;
