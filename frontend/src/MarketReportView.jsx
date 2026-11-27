import "./MarketReportView.css";
import {
    ResponsiveContainer,
    LineChart,
    Line,
    AreaChart,
    Area,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
} from "recharts";



function formatDate(value) {
    return new Date(value).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
    });
}

function formatPrice(value) {
    return `$${value.toLocaleString("en-US", {
        maximumFractionDigits: 0,
    })}`;
}

function formatCompact(value) {
    return `$${(value / 1_000_000_000).toFixed(1)}B`;
}


function formatCurrency(value) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        notation: "compact",
        maximumFractionDigits: 2,
    }).format(value);
}

function formatPercent(value) {
    return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function MarketReportView({ report }) {
    const { metrics, analysis, news } = report;

    const indicators = [
        {
            label: "Current price",
            value: formatCurrency(metrics.current_price_usd),
        },
        {
            label: "Market cap",
            value: formatCurrency(metrics.market_cap_usd),
        },
        {
            label: "24h change",
            value: formatPercent(metrics.price_change_24h_pct),
        },
        {
            label: "Period change",
            value: formatPercent(metrics.period_change_pct),
        },
        {
            label: "24h volume",
            value: formatCurrency(metrics.total_volume_24h_usd),
        },
        {
            label: "Volatility",
            value: `${metrics.price_volatility_pct.toFixed(2)}%`,
        },
    ];

    return (
        <div className="market-report">
            <div className="report-header">
                <div>
                    <h2>{report.coin_name} Market Report</h2>
                    <span>
                        {report.coin_symbol} · {report.period_days}-day analysis
                    </span>
                </div>

                <span className={`confidence ${analysis.confidence}`}>
                    {analysis.confidence} confidence
                </span>
            </div>

            <section className="report-section">
                <h3>Summary</h3>
                <p>{analysis.summary}</p>
            </section>

            <section className="report-section">
                <h3>Market indicators</h3>
                <div className="report-metrics">
                    {indicators.map((item) => (
                        <div className="report-metric" key={item.label}>
                            <span>{item.label}</span>
                            <strong>{item.value}</strong>
                        </div>
                    ))}
                </div>
            </section>

            <section className="report-section">
                <h3>Price History</h3>

                <div className="report-chart">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={report.price_history} margin={{ top: 15, right: 25, left: -15, bottom: 5 }}>
                            <CartesianGrid stroke="#edf0f3" vertical={false} />
                            <XAxis
                                dataKey="timestamp"
                                tickFormatter={formatDate}
                                minTickGap={35}
                            />
                            <YAxis
                                domain={["auto", "auto"]}
                                tickFormatter={formatPrice}
                                width={75}
                            />
                            <Tooltip
                                labelFormatter={(value) =>
                                    new Date(value).toLocaleString()
                                }
                                formatter={(value) => [formatPrice(value), "Price"]}
                            />
                            <Line
                                type="monotone"
                                dataKey="price_usd"
                                stroke="#64748b"
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </section>

            <section className="report-section">
                <h3>Trading Volume</h3>

                <div className="report-chart">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={report.volume_history} margin={{ top: 15, right: 25, left: -15, bottom: 0 }}>
                            <CartesianGrid stroke="#edf0f3" vertical={false} />
                            <XAxis
                                dataKey="timestamp"
                                tickFormatter={formatDate}
                                minTickGap={35}
                            />
                            <YAxis tickFormatter={formatCompact} width={75} />
                            <Tooltip
                                labelFormatter={(value) =>
                                    new Date(value).toLocaleString()
                                }
                                formatter={(value) => [formatCompact(value), "Volume"]}
                            />
                            <Area
                                type="monotone"
                                dataKey="volume_usd"
                                stroke="#0d9488"
                                fill="#0d9488"
                                fillOpacity={0.12}
                                dot={false}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </section>

            <section className="report-section">
                <h3>Key findings</h3>
                <ul>
                    {analysis.key_findings.map((finding, index) => (
                        <li key={index}>{finding}</li>
                    ))}
                </ul>
            </section>

            <section className="report-section">
                <h3>Risks</h3>
                <ul>
                    {analysis.risks.map((risk, index) => (
                        <li key={index}>{risk}</li>
                    ))}
                </ul>
            </section>

            <section className="report-section">
                <h3>Market outlook</h3>
                <p>{analysis.outlook}</p>
            </section>

            <section className="report-section">
                <h3>Confidence assessment</h3>
                <p>{analysis.confidence_reason}</p>
            </section>

            <section className="report-section">
                <h3>Related News</h3>

                <div className="report-news">
                    {report.news.map((article) => (
                    <a
                        className="report-news-card"
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        key={article.url}
                    >
                        <div className="report-news-meta">
                        <span>{article.source}</span>
                        <span>{formatDate(article.published_at)}</span>
                        </div>

                        <h4>{article.title}</h4>

                        <span className="report-news-link">Read article ↗</span>
                    </a>
                    ))}
                </div>
            </section>

            <div className="report-footer">
                <span>
                    Generated {new Date(report.generated_at).toLocaleString()}
                </span>
                <span><b>Market data:</b> {report.data_sources.join(", ")}, <b>News provider:</b> {report.news_provider} GDELT</span>
            </div>
        </div>
    );
}

export default MarketReportView;
