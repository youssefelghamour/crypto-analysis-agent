import { useEffect, useState } from "react";
import "./MarketTicker.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function formatPrice(price) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: price < 1 ? 6 : 2,
    }).format(price);
}

function MarketTicker() {
    const [assets, setAssets] = useState([]);

    useEffect(() => {
        let active = true;

        async function fetchTicker() {
            try {
                const response = await fetch(`${API_URL}/market/ticker`);

                if (!response.ok) {
                    throw new Error("Failed to fetch market ticker");
                }

                const data = await response.json();

                if (active) {
                    setAssets(data.assets);
                }
            } catch (error) {
                console.error("Market ticker error:", error);
            }
        }

        fetchTicker();

        // run the function every minute to update the data
        const interval = setInterval(fetchTicker, 60_000);

        return () => {
            active = false;
            clearInterval(interval);
        };
    }, []);

    if (assets.length === 0) {
        return null;
    }

    // Duplicate the assets to create a scrolling loop
    const tickerItems = [...assets, ...assets];

    return (
        <div className="market-ticker">
            <div className="ticker-label">
                <span className="ticker-live-dot" />
                MARKETS
            </div>

            <div className="ticker-viewport">
                <div className="ticker-track">
                    {tickerItems.map((asset, index) => (
                        <div
                            className="ticker-item"
                            key={`${asset.id}-${index}`}
                        >
                            <img
                                className="ticker-logo"
                                src={asset.image}
                                alt=""
                                loading="lazy"
                            />
                            <span className="ticker-symbol">
                                {asset.symbol}
                            </span>

                            <span className="ticker-price">
                                {formatPrice(asset.price_usd)}
                            </span>

                            <span
                                className={`ticker-change ${
                                    asset.change_24h > 0
                                        ? "positive"
                                        : asset.change_24h < 0
                                        ? "negative"
                                        : "neutral"
                                    }`
                                }
                            >
                                {asset.change_24h == null
                                    ? "—"
                                    : `${asset.change_24h > 0 ? "+" : ""}${asset.change_24h.toFixed(2)}%`
                                }
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default MarketTicker;
