package com.surveillance.core;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents the result of a surveillance detection run.
 */
public class DetectionResult {
    private String reportType;
    private int alertCount;
    private List<Alert> alerts;
    private String summary;
    private long executionTimeMs;

    public DetectionResult(String reportType) {
        this.reportType = reportType;
        this.alerts = new ArrayList<>();
        this.alertCount = 0;
    }

    public void addAlert(Alert alert) {
        alerts.add(alert);
        alertCount++;
    }

    public String getReportType() {
        return reportType;
    }

    public int getAlertCount() {
        return alertCount;
    }

    public List<Alert> getAlerts() {
        return alerts;
    }

    public String getSummary() {
        return summary;
    }

    public void setSummary(String summary) {
        this.summary = summary;
    }

    public long getExecutionTimeMs() {
        return executionTimeMs;
    }

    public void setExecutionTimeMs(long executionTimeMs) {
        this.executionTimeMs = executionTimeMs;
    }

    /**
     * Represents a single surveillance alert.
     */
    public static class Alert {
        private String tradeId;
        private String accountId;
        private String symbol;
        private String alertType;
        private String severity;
        private String description;
        private String timestamp;

        public Alert(String tradeId, String accountId, String symbol, String alertType) {
            this.tradeId = tradeId;
            this.accountId = accountId;
            this.symbol = symbol;
            this.alertType = alertType;
            this.severity = "MEDIUM";
        }

        // Getters and setters
        public String getTradeId() { return tradeId; }
        public void setTradeId(String tradeId) { this.tradeId = tradeId; }
        
        public String getAccountId() { return accountId; }
        public void setAccountId(String accountId) { this.accountId = accountId; }
        
        public String getSymbol() { return symbol; }
        public void setSymbol(String symbol) { this.symbol = symbol; }
        
        public String getAlertType() { return alertType; }
        public void setAlertType(String alertType) { this.alertType = alertType; }
        
        public String getSeverity() { return severity; }
        public void setSeverity(String severity) { this.severity = severity; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public String getTimestamp() { return timestamp; }
        public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    }
}
